import json
 
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.urls import reverse
 
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
    Application,
    Project,
    ProjectSkill,
    ProjectCoreTime,
    ProjectPreferredScale,
    ProjectHiddenAbility,
    Returnship, 
)

from projects.services.returnship import create_returnship_offer

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
 
 
def _sync_deadline_status(projects):
    # 마감일이 지난 OPEN 프로젝트를 SELECTING으로 자동 전환.

    today = timezone.localdate()
    to_update = [
        project for project in projects
        if project.status == Project.Status.OPEN and project.deadline < today
    ]
    if to_update:
        for project in to_update:
            project.status = Project.Status.SELECTING
        Project.objects.bulk_update(to_update, ['status'])
 
 
@role_required('COMPANY')
@onboarding_required
def project_manage(request):
    tab = request.GET.get('tab', 'recruiting')
 
    all_projects = list(
        Project.objects.filter(company_profile=request.user.company_profile)
        .select_related('company_profile', 'job_category')
    )
    _sync_deadline_status(all_projects)  # 마감일 지나면 자동으로 선발중 전환
 
    if tab == 'recruiting':
        # 모집 중 탭은 OPEN + SELECTING을 같이 보여줌
        projects = [
            p for p in all_projects
            if p.status in (Project.Status.OPEN, Project.Status.SELECTING)
        ]
    elif tab == 'progress':
        projects = [p for p in all_projects if p.status == Project.Status.IN_PROGRESS]
    elif tab == 'completed':
        projects = [p for p in all_projects if p.status == Project.Status.COMPLETED]
    else:
        projects = all_projects
 
    projects.sort(key=lambda p: -p.id)
 
    today = timezone.localdate()
 
    for project in projects:
        project.applicant_count = project.applications.count()
 
        # D-day 계산 (마감일 당일은 D-DAY, 지난 건 "마감"으로 표시)
        days_left = (project.deadline - today).days
        if days_left > 0:
            project.d_day_label = f'D-{days_left}'
        elif days_left == 0:
            project.d_day_label = 'D-DAY'
        else:
            project.d_day_label = '마감'
 
        # 필수 스킬 이름 목록 (표시용)
        required_skills = (
            project.project_skills
            .filter(priority=ProjectSkill.Priority.NORMAL)
            .select_related('skill')
        )
        project.required_skill_names = [rel.skill.name for rel in required_skills]
 
        # 진행중 프로젝트는 지원자 확인 대신 수락된 참여자 이름만 표시
        if project.status == Project.Status.IN_PROGRESS:
            accepted = (
                project.applications
                .filter(status=Application.Status.ACCEPTED)
                .select_related('worker_profile__user')
            )
            project.participant_names = [
                app.worker_profile.user.name for app in accepted
            ]

    # "완료된 프로젝트" 탭에서는 목록 위에서 클릭한 프로젝트의 참여인원을 아래에 보여줌
    selected_project = None
    participants = []
    if tab == 'completed':
        selected_id = request.GET.get('selected')
        if selected_id:
            selected_project = next(
                (p for p in projects if str(p.id) == selected_id), None
            )
        elif projects:
            selected_project = projects[0]  # 기본값: 첫 번째 완료 프로젝트

        if selected_project:
            applications = list(
                Application.objects
                .filter(project=selected_project, status=Application.Status.ACCEPTED)
                .select_related('worker_profile__user')
            )

            returnship_map = {
                r.application_id: r
                for r in Returnship.objects.filter(application__in=applications)
            }
            for application in applications:
                application.returnship = returnship_map.get(application.id)

            participants = applications

    return render(request, 'b_project_manage.html', {
        'projects': projects,
        'tab': tab,
        'selected_project': selected_project,
        'participants': participants,
    })
 
 
@role_required('COMPANY')
@onboarding_required
def project_delete(request, project_id):
    project = get_object_or_404(
        Project, id=project_id, company_profile=request.user.company_profile
    )
 
    # 모집중(OPEN)일 때만 삭제 가능. 지원자가 있어도 하드 삭제 (CASCADE로 Application도 같이 삭제됨)
    if project.status != Project.Status.OPEN:
        messages.error(request, '모집중인 프로젝트만 삭제할 수 있어요.')
        return redirect('company:project_manage')
 
    if request.method == 'POST':
        project.delete()
        messages.success(request, '프로젝트를 삭제했어요.')
        return redirect('company:project_manage')
 
    return redirect('company:project_manage')
 
 
@role_required('COMPANY')
@onboarding_required
def project_applicants(request, project_id):
    project = get_object_or_404(
        Project, id=project_id, company_profile=request.user.company_profile
    )
    applications = (
        Application.objects
        .filter(project=project)
        .select_related('worker_profile__user', 'worker_profile__job_category')
        .order_by('-id')
    )
 
    return render(request, 'b_project_applicants.html', {
        'project': project,
        'applications': applications,
        # 모집 중(OPEN)일 때는 수락/거절 자체를 못 함. 선발중부터 가능해짐
        'can_decide': project.status == Project.Status.SELECTING,
    })
 
 
@role_required('COMPANY')
@onboarding_required
def project_applicant_detail(request, project_id, application_id):
    project = get_object_or_404(
        Project, id=project_id, company_profile=request.user.company_profile
    )
    application = get_object_or_404(
        Application.objects.select_related('worker_profile__user', 'worker_profile__job_category'),
        id=application_id, project=project,
    )
    worker_profile = application.worker_profile
 
    return render(request, 'b_project_applicant_detail.html', {
        'project': project,
        'application': application,
        'worker_profile': worker_profile,
        'can_decide': project.status == Project.Status.SELECTING,
    })
 
 
@role_required('COMPANY')
@onboarding_required
def application_decide(request, project_id, application_id):
    # 지원자 수락/거절 처리. SELECTING 상태에서만 동작
    project = get_object_or_404(
        Project, id=project_id, company_profile=request.user.company_profile
    )
    application = get_object_or_404(
        Application, id=application_id, project=project
    )
 
    if project.status != Project.Status.SELECTING:
        messages.error(request, '선발중 상태에서만 수락/거절이 가능해요.')
        return redirect(
            'company:project_applicant_detail',
            project_id=project.id, application_id=application.id,
        )
 
    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision == 'accept':
            application.status = Application.Status.ACCEPTED
            application.save(update_fields=['status'])
            messages.success(request, '지원자를 수락했어요.')
        elif decision == 'reject':
            application.status = Application.Status.REJECTED
            application.save(update_fields=['status'])
            messages.success(request, '지원자를 거절했어요.')
 
    return redirect('company:project_applicants', project_id=project.id)
 
 
@role_required('COMPANY')
@onboarding_required
def project_start(request, project_id):
    # 선발중(SELECTING) -> 진행중(IN_PROGRESS) 전환
    # 시작하는 순간, 아직 결정 안 된(PENDING) 지원자는 전부 자동 거절 처리
    project = get_object_or_404(
        Project, id=project_id, company_profile=request.user.company_profile
    )
 
    if project.status != Project.Status.SELECTING:
        messages.error(request, '선발중 상태에서만 프로젝트를 시작할 수 있어요.')
        return redirect('company:project_manage')
 
    if request.method == 'POST':
        # 남은 PENDING 지원자 전부 자동 거절
        project.applications.filter(
            status=Application.Status.PENDING
        ).update(status=Application.Status.REJECTED)
 
        project.status = Project.Status.IN_PROGRESS
        project.started_at = timezone.now()
        project.save(update_fields=['status', 'started_at'])
        messages.success(request, '프로젝트를 시작했어요. 남은 지원자는 자동으로 거절 처리되었어요.')
 
    return redirect('company:project_manage')
 
 
@role_required('COMPANY')
@onboarding_required
def project_progress_detail(request, project_id):
    # 진행중 프로젝트 상세보기
    project = get_object_or_404(
        Project, id=project_id, company_profile=request.user.company_profile
    )
    return render(request, 'b_project_progress_detail.html', {'project': project})
 
 
@role_required('COMPANY')
@onboarding_required
def project_edit(request, project_id):
    # 진행중 상태에서만 제목/상세내용만 수정 가능
    project = get_object_or_404(
        Project, id=project_id, company_profile=request.user.company_profile
    )
 
    if project.status != Project.Status.IN_PROGRESS:
        messages.error(request, '진행중 상태에서만 수정할 수 있어요.')
        return redirect('company:project_progress_detail', project_id=project.id)
 
    if request.method == 'POST':
        project.title = request.POST.get('title', project.title)
        project.description = request.POST.get('description', project.description)
        project.save(update_fields=['title', 'description'])
        messages.success(request, '프로젝트 정보를 수정했어요.')
        return redirect('company:project_progress_detail', project_id=project.id)
 
    return render(request, 'b_project_edit.html', {'project': project})
 
 
@role_required('COMPANY')
@onboarding_required
def project_complete(request, project_id):
    # 진행중 -> 완료 전환
    project = get_object_or_404(
        Project, id=project_id, company_profile=request.user.company_profile
    )
 
    if project.status != Project.Status.IN_PROGRESS:
        messages.error(request, '진행중 상태에서만 마감할 수 있어요.')
        return redirect('company:project_manage')
 
    if request.method == 'POST':
        project.status = Project.Status.COMPLETED
        project.completed_at = timezone.now()
        project.save(update_fields=['status', 'completed_at'])
        messages.success(request, '프로젝트를 완료 처리했어요.')
 
    return redirect('company:project_manage')
    

@role_required('COMPANY')
@onboarding_required
def returnship_create(request, project_id, application_id):
    project = get_object_or_404(
        Project, id=project_id, company_profile=request.user.company_profile
    )
    application = get_object_or_404(Application, id=application_id, project=project)

    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')

        try:
            create_returnship_offer(application=application, title=title, content=content)
        except ValidationError as error:
            message = error.messages[0] if hasattr(error, 'messages') else str(error)
            messages.error(request, message)
        else:
            messages.success(request, '리턴십을 제안했어요.')

        redirect_url = f"{reverse('company:project_manage')}?tab=completed&selected={project.id}"
        return redirect(redirect_url)

    return render(request, 'b_returnship_create.html', {
        'project': project,
        'application': application,
    })