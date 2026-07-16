import json
 
from django.contrib import messages
from django.db.models import Prefetch
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.urls import reverse
 
from accounts.decorators import role_required, onboarding_required
from worker.services.matching import rank_projects_for_worker
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


def _get_time_slots_for_display():
    time_slots = list(TimeSlot.objects.all())

    for slot in time_slots:
        full_name = slot.name.strip()

        if '(' in full_name and full_name.endswith(')'):
            display_name, time_range = full_name.rsplit('(', 1)

            slot.display_name = display_name.strip()
            slot.time_range = time_range.rstrip(')').strip()
        else:
            slot.display_name = full_name
            slot.time_range = ''

    return time_slots
 
 
def _build_context():
    job_categories = JobCategory.objects.all()

    skills_by_job = {}

    for js in JobSkill.objects.select_related(
        'job_category',
        'skill',
    ).all():
        skills_by_job.setdefault(
            str(js.job_category_id),
            [],
        ).append({
            'id': js.skill_id,
            'name': js.skill.name,
        })

    hidden_abilities_by_job = {}

    for relation in JobHiddenAbility.objects.select_related(
        'job_category',
        'hidden_ability',
    ).all():
        hidden_abilities_by_job.setdefault(
            str(relation.job_category_id),
            [],
        ).append({
            'id': relation.hidden_ability_id,
            'name': relation.hidden_ability.name,
        })

    return {
        'job_categories': job_categories,

        'time_slots': _get_time_slots_for_display(),

        'work_style_choices': Project.WorkStyle.choices,
        'weekly_hours_choices': Project.WeeklyHours.choices,
        'career_years_choices': Project.CareerYears.choices,
        'scale_choices': ProjectPreferredScale.ScaleType.choices,

        'skills_by_job_json': json.dumps(
            skills_by_job,
            cls=DjangoJSONEncoder,
            ensure_ascii=False,
        ),

        'hidden_abilities_by_job_json': json.dumps(
            hidden_abilities_by_job,
            cls=DjangoJSONEncoder,
            ensure_ascii=False,
        ),
    }
 
 
@role_required('COMPANY')
@onboarding_required
def project_create(request):
    context = _build_context()

    # GET/POST 공통 기본값
    context.update({
        'today': timezone.localdate().isoformat(),
        'form_data': {},
        'selected_core_times': [],
        'selected_scales': [],
        'selected_required_skills': [],
        'selected_preferred_skills': [],
        'selected_hidden_abilities': [],
    })

    if request.method == 'POST':
        company = request.user.company_profile

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        job_category_id = request.POST.get('job_category', '').strip()
        work_style = request.POST.get('work_style', '').strip()
        weekly_hours = request.POST.get('weekly_hours', '').strip()
        career_years = request.POST.get('career_years', '').strip()

        compensation_amount = request.POST.get(
            'compensation_amount',
            '',
        ).strip()

        deadline = request.POST.get('deadline', '').strip()
        duration = request.POST.get('duration', '').strip()

        recruitment_count = request.POST.get(
            'recruit_count',
            '',
        ).strip()

        core_time_ids = {
            value
            for value in request.POST.getlist('core_times')
            if value.isdigit()
        }

        selected_scales = request.POST.getlist(
            'preferred_scales'
        )

        required_skill_ids = {
            value
            for value in request.POST.getlist('skill_required')
            if value.isdigit()
        }

        preferred_skill_ids = {
            value
            for value in request.POST.getlist('skill_preferred')
            if value.isdigit()
        }

        # 우대 스킬은 필수 스킬로 먼저 선택한 항목만 허용
        preferred_skill_ids &= required_skill_ids

        try:
            hidden_ability_ids = json.loads(
                request.POST.get(
                    'hidden_abilities',
                    '[]',
                )
            )
        except (json.JSONDecodeError, TypeError):
            hidden_ability_ids = []

        if not isinstance(hidden_ability_ids, list):
            hidden_ability_ids = []

        hidden_ability_ids = {
            str(value)
            for value in hidden_ability_ids
            if str(value).isdigit()
        }

        errors = []

        if not title:
            errors.append('프로젝트명을 입력해주세요.')

        if not description:
            errors.append('상세 내용을 입력해주세요.')

        if not job_category_id:
            errors.append('직무 유형을 선택해주세요.')

        if not work_style:
            errors.append('근무 형태를 선택해주세요.')

        if not weekly_hours:
            errors.append('주간 가용 시간을 선택해주세요.')

        if not career_years:
            errors.append('필요 경력 연차를 선택해주세요.')

        if not required_skill_ids:
            errors.append('필수 스킬을 1개 이상 선택해주세요.')

        if not core_time_ids:
            errors.append('코어타임을 1개 이상 선택해주세요.')

        if not selected_scales:
            errors.append('업무 규모를 1개 이상 선택해주세요.')

        try:
            compensation_value = int(compensation_amount)

            if compensation_value < 0:
                raise ValueError

        except (TypeError, ValueError):
            compensation_value = 0
            errors.append(
                '보수 금액은 0 이상의 숫자로 입력해주세요.'
            )

        try:
            recruitment_value = int(recruitment_count)

            if recruitment_value < 1:
                raise ValueError

        except (TypeError, ValueError):
            recruitment_value = 1
            errors.append(
                '모집 인원은 1명 이상의 숫자로 입력해주세요.'
            )

        if not deadline:
            errors.append('모집 마감일을 선택해주세요.')
        else:
            try:
                deadline_date = timezone.datetime.strptime(
                    deadline,
                    '%Y-%m-%d',
                ).date()

                if deadline_date < timezone.localdate():
                    errors.append(
                        '모집 마감일은 오늘 이후로 선택해주세요.'
                    )

            except ValueError:
                errors.append(
                    '모집 마감일 형식이 올바르지 않습니다.'
                )

        if not duration:
            errors.append('프로젝트 기간을 입력해주세요.')

        if errors:
            context.update({
                'error': errors[0],
                'form_data': request.POST,
                'selected_core_times': [
                    int(value)
                    for value in core_time_ids
                ],
                'selected_scales': selected_scales,
                'selected_required_skills': [
                    int(value)
                    for value in required_skill_ids
                ],
                'selected_preferred_skills': [
                    int(value)
                    for value in preferred_skill_ids
                ],
                'selected_hidden_abilities': [
                    int(value)
                    for value in hidden_ability_ids
                ],
            })

            return render(
                request,
                'project_create.html',
                context,
            )

        with transaction.atomic():
            project = Project.objects.create(
                company_profile=company,
                job_category_id=job_category_id,

                # 기업 공고는 항상 실무 프로젝트
                project_type=Project.ProjectType.REAL,

                title=title,
                work_style=work_style,
                weekly_hours=weekly_hours,
                compensation_amount=compensation_value,
                deadline=deadline,
                description=description,
                duration=duration,
                recruitment_count=recruitment_value,
                career_years=career_years,
                status=Project.Status.OPEN,
            )

            # 모델상 하나의 스킬은 NORMAL 또는 PREFERRED 중 하나로 저장
            for skill_id in required_skill_ids:
                priority = (
                    ProjectSkill.Priority.PREFERRED
                    if skill_id in preferred_skill_ids
                    else ProjectSkill.Priority.NORMAL
                )

                ProjectSkill.objects.create(
                    project=project,
                    skill_id=int(skill_id),
                    priority=priority,
                )

            for time_id in core_time_ids:
                ProjectCoreTime.objects.create(
                    project=project,
                    time_slot_id=int(time_id),
                )

            for scale in selected_scales:
                ProjectPreferredScale.objects.create(
                    project=project,
                    scale_type=scale,
                )

            for ability_id in hidden_ability_ids:
                ProjectHiddenAbility.objects.create(
                    project=project,
                    hidden_ability_id=int(ability_id),
                )

        messages.success(
            request,
            '프로젝트 공고가 등록되었습니다.',
        )

        return redirect('company:project_manage')

    return render(
        request,
        'project_create.html',
        context,
    )
 
def _sync_deadline_status(projects):
    # 마감일이 지난 OPEN 프로젝트를 SELECTING으로 자동 전환.
    today = timezone.localdate()

    target_projects = [
        project
        for project in projects
        if (
            project.status == Project.Status.OPEN
            and project.deadline < today
        )
    ]

    if not target_projects:
        return

    for project in target_projects:
        project.status = Project.Status.SELECTING

    Project.objects.bulk_update(
        target_projects,
        ['status'],
    )

 
 
@role_required('COMPANY')
@onboarding_required
def project_manage(request):
    tab = request.GET.get('tab', 'recruiting')

    valid_tabs = {
        'recruiting',
        'progress',
        'completed',
    }

    if tab not in valid_tabs:
        tab = 'recruiting'

    project_skill_queryset = (
        ProjectSkill.objects
        .select_related('skill')
        .order_by('id')
    )

    application_queryset = (
        Application.objects
        .select_related(
            'worker_profile__user',
            'worker_profile__job_category',
        )
        .order_by('-id')
    )

    all_projects = list(
        Project.objects
        .filter(
            company_profile=request.user.company_profile,
            project_type=Project.ProjectType.REAL,
        )
        .select_related(
            'company_profile',
            'job_category',
        )
        .prefetch_related(
            Prefetch(
                'project_skills',
                queryset=project_skill_queryset,
            ),
            Prefetch(
                'applications',
                queryset=application_queryset,
            ),
        )
        .order_by('-id')
    )

    _sync_deadline_status(all_projects) # 마감일 지나면 자동으로 선발중 전환

    if tab == 'recruiting':
        # 모집 중 탭은 OPEN + SELECTING을 같이 보여줌
        projects = [
            project
            for project in all_projects
            if project.status in {
                Project.Status.OPEN,
                Project.Status.SELECTING,
            }
        ]

    elif tab == 'progress':
        projects = [
            project
            for project in all_projects
            if project.status == Project.Status.IN_PROGRESS
        ]

    else:
        projects = [
            project
            for project in all_projects
            if project.status == Project.Status.COMPLETED
        ]

    today = timezone.localdate()

    for project in projects:
        applications = list(project.applications.all())

        project.applicant_count = len(applications)
        # D-day 계산 (마감일 당일은 D-DAY, 지난 건 "마감"으로 표시)
        days_left = (project.deadline - today).days

        if days_left > 0:
            project.d_day_label = f'D-{days_left}'
        elif days_left == 0:
            project.d_day_label = 'D-DAY'
        else:
            project.d_day_label = '마감'

        # 필수 스킬 이름 목록 (표시용)
        project.required_skill_names = [
            relation.skill.name
            for relation in project.project_skills.all()
            if relation.priority == ProjectSkill.Priority.NORMAL
        ]

        project.preferred_skill_names = [
            relation.skill.name
            for relation in project.project_skills.all()
            if relation.priority == ProjectSkill.Priority.PREFERRED
        ]

        # 진행중 프로젝트는 지원자 확인 대신 수락된 참여자 이름만 표시
        project.participants = [
            application
            for application in applications
            if application.status == Application.Status.ACCEPTED
        ]

    # "완료된 프로젝트" 탭에서는 목록 위에서 클릭한 프로젝트의 참여인원을 아래에 보여줌
    selected_project = None
    participants = []

    if tab == 'completed':
        selected_id = request.GET.get('selected')

        if selected_id:
            selected_project = next(
                (
                    project
                    for project in projects
                    if str(project.id) == selected_id
                ),
                None,
            )

        if selected_project is None and projects:
            selected_project = projects[0] # 기본값: 첫 번째 완료 프로젝트

        if selected_project:
            participants = [
                application
                for application
                in selected_project.applications.all()
                if application.status == Application.Status.ACCEPTED
            ]

            returnship_map = {
                returnship.application_id: returnship
                for returnship in Returnship.objects.filter(
                    application__in=participants,
                )
            }

            for application in participants:
                application.returnship = returnship_map.get(
                    application.id
                )

    return render(
        request,
        'project_manage.html',
        {
            'projects': projects,
            'tab': tab,
            'selected_project': selected_project,
            'participants': participants,
        },
    )
 
 
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
        Project.objects
        .select_related(
            'company_profile',
            'job_category',
        )
        .prefetch_related(
            'project_skills__skill',
        ),
        id=project_id,
        company_profile=request.user.company_profile,
    )

    # 사용자가 지원자 화면을 직접 새로고침해도 마감일이 지났으면 선발중으로 전환
    _sync_deadline_status([project])

    applications = list(
        Application.objects
        .filter(project=project)
        .select_related(
            'worker_profile__user',
            'worker_profile__job_category',
        )
        .prefetch_related(
            'worker_profile__worker_skills__skill',
            'worker_profile__hidden_activities__hidden_ability',
        )
        .order_by('-id')
    )

    for application in applications:
        worker_profile = application.worker_profile

        ranked = rank_projects_for_worker(
            worker_profile,
            [project],
        )

        application.match_score = (
            getattr(ranked[0], 'match_score', 0)
            if ranked
            else 0
        )

        application.skill_names = [
            worker_skill.skill.name
            for worker_skill
            in worker_profile.worker_skills.all()
        ]

        application.hidden_ability_names = list(dict.fromkeys(
            activity.hidden_ability.name
            for activity
            in worker_profile.hidden_activities.all()
            if activity.hidden_ability
        ))

        application.in_progress_projects = list(
            Project.objects.filter(
                applications__worker_profile=worker_profile,
                applications__status=Application.Status.ACCEPTED,
                status=Project.Status.IN_PROGRESS,
            )
            .select_related(
                'company_profile',
                'job_category',
            )
            .distinct()
        )

        application.completed_projects = list(
            Project.objects.filter(
                applications__worker_profile=worker_profile,
                applications__status=Application.Status.ACCEPTED,
                status=Project.Status.COMPLETED,
            )
            .select_related(
                'company_profile',
                'job_category',
            )
            .distinct()
        )

    today = timezone.localdate()
    days_left = (project.deadline - today).days

    if days_left > 0:
        project.d_day_label = f'D-{days_left}'
    elif days_left == 0:
        project.d_day_label = 'D-DAY'
    else:
        project.d_day_label = '마감'

    project.required_skill_names = [
        relation.skill.name
        for relation in project.project_skills.all()
        if relation.priority == ProjectSkill.Priority.NORMAL
    ]

    return render(
        request,
        'project_applicants.html',
        {
            'project': project,
            'applications': applications,
            'applicant_count': len(applications),
            'can_decide': (
                project.status
                == Project.Status.SELECTING
            ),
        },
    )
 
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
            'company:project_applicantsl',
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