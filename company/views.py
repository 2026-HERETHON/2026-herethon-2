import json

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect

from accounts.decorators import role_required, onboarding_required
from .models import CompanyProfile
from core.models import (
    HiddenAbility,
    JobCategory,
    JobHiddenAbility,
    JobSkill,
    TimeSlot,
)
from projects.models import (
    Project,
    ProjectSkill,
    ProjectCoreTime,
    ProjectPreferredScale,
    ProjectHiddenAbility,
)


@role_required('COMPANY')
def company_onboarding(request):
    # 기업 온보딩 - 기업명만 간단히 받고 바로 기업 공고 등록으로

    if request.user.onboarding_completed:
        return redirect('company:project_manage')

    if request.method == 'POST':
        company_name = request.POST.get('company_name', '').strip()

        if not company_name:
            return render(request, 'company_onboarding.html', {
                'error': '기업명을 입력해주세요.'
            })

        CompanyProfile.objects.create(
            user=request.user,
            company_name=company_name,
        )
        request.user.onboarding_completed = True
        request.user.save(update_fields=['onboarding_completed'])

        return redirect('company:project_create')

    return render(request, 'company_onboarding.html')


def _build_context():
    job_categories = JobCategory.objects.all()
    time_slots = TimeSlot.objects.all()

    skills_by_job = {}
    for js in JobSkill.objects.select_related('job_category', 'skill').all():
        skills_by_job.setdefault(js.job_category_id, []).append(
            {'id': js.skill_id, 'name': js.skill.name}
        )

    hidden_abilities_by_job = {}
    for relation in JobHiddenAbility.objects.select_related(
        'job_category', 'hidden_ability'
    ).all():
        hidden_abilities_by_job.setdefault(relation.job_category_id, []).append(
            {'id': relation.hidden_ability_id, 'name': relation.hidden_ability.name}
        )

    return {
        'job_categories': job_categories,
        'time_slots': time_slots,
        'skills_by_job_json': json.dumps(skills_by_job, cls=DjangoJSONEncoder),
        'hidden_abilities_by_job_json': json.dumps(
            hidden_abilities_by_job, cls=DjangoJSONEncoder
        ),
    }


@role_required('COMPANY')
@onboarding_required
def project_create(request):
    context = _build_context()

    if request.method == 'POST':
        company = request.user.company_profile

        try:
            skill_priorities = json.loads(request.POST.get('skill_priorities', '{}'))
        except (json.JSONDecodeError, TypeError):
            skill_priorities = {}

        project = Project.objects.create(
            company_profile=company,
            job_category_id=request.POST.get('job_category'),
            project_type=request.POST.get('project_type'),
            title=request.POST.get('title'),
            work_style=request.POST.get('work_style'),
            weekly_hours=request.POST.get('weekly_hours'),
            compensation_amount=request.POST.get('compensation_amount'),
            career_years=request.POST.get('career_years'),
            description=request.POST.get('description'),
            deadline=request.POST.get('deadline'),
            duration=request.POST.get('duration'),
            recruitment_count=request.POST.get('recruit_count'),
            status=Project.Status.OPEN,
        )

        for skill_id, priority in skill_priorities.items():
            ProjectSkill.objects.create(
                project=project, skill_id=skill_id, priority=priority
            )

        for time_id in request.POST.getlist('core_times'):
            ProjectCoreTime.objects.create(project=project, time_slot_id=time_id)

        for scale in request.POST.getlist('preferred_scales'):
            ProjectPreferredScale.objects.create(project=project, scale_type=scale)

        for ability_id in request.POST.getlist('hidden_abilities'):
            ProjectHiddenAbility.objects.create(
                project=project, hidden_ability_id=ability_id
            )

        return redirect('company:project_manage')

    return render(request, 'b_project_create.html', context)


@role_required('COMPANY')
@onboarding_required
def project_manage(request):
    projects = Project.objects.filter(
        company_profile=request.user.company_profile
    ).order_by('-id')
    return render(request, 'b_project_manage.html', {'projects': projects})
