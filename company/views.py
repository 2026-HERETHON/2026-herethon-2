import json

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect

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


def _build_context():
    job_categories = JobCategory.objects.all()
    time_slots = TimeSlot.objects.all()
    hidden_abilities = HiddenAbility.objects.all()

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
            {
                'id': relation.hidden_ability_id,
                'name': relation.hidden_ability.name,
            }
        )

    return {
        'job_categories': job_categories,
        'time_slots': time_slots,
        'hidden_abilities': hidden_abilities,
        'skills_by_job_json': json.dumps(skills_by_job, cls=DjangoJSONEncoder),
        'hidden_abilities_by_job_json': json.dumps(
            hidden_abilities_by_job, cls=DjangoJSONEncoder
        ),
    }


def project_create(request):
    context = _build_context()

    if request.method == 'POST':
        # TODO: 로그인/기업 온보딩 완료 후 request.user.company_profile로 교체
        company = CompanyProfile.objects.first()

        if company is None:
            context['error'] = '테스트용 기업 프로필이 없습니다. Admin에서 CompanyProfile을 먼저 생성해주세요.'
            return render(request, 'b_project_create.html', context)

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


def project_manage(request):
    projects = Project.objects.all().order_by('-id')
    return render(request, 'b_project_manage.html', {'projects': projects})
