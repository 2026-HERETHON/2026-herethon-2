from collections import OrderedDict

from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q

from accounts.decorators import role_required, onboarding_required
from core.models import JobCategory, JobSkill, TimeSlot
from projects.models import Project
from worker.models import (
    WorkerConcern,
    WorkerCoreTime,
    WorkerHiddenActivity,
    WorkerPreferredScale,
    WorkerProfile,
    WorkerSkill,
)

from worker.services.hidden_ability import classify_hidden_abilities, get_worker_hidden_abilities
from worker.services.matching import rank_projects_for_worker


def _get_prefetched_worker_profile(user):
    worker_profile = getattr(user, 'worker_profile', None)
    if not worker_profile:
        return None

    return worker_profile.__class__.objects.select_related('job_category').prefetch_related(
        'worker_skills__skill',
        'hidden_activities__hidden_ability',
        'preferred_scales',
    ).get(pk=worker_profile.pk)


def _worker_completed_redirect(request):
    if request.session.get('show_worker_onboarding_results'):
        return redirect('worker:hidden_ability_result')
    return redirect('worker:project_list')


@role_required('WORKER')
def onboarding_step1(request):
    # 이미 온보딩 끝난 유저가 실수로 다시 들어오면 리스트로 바로 보냄
    if request.user.onboarding_completed:
        return _worker_completed_redirect(request)

    if request.method == 'POST':
        job_category_id = request.POST.get('job_category')
        if not job_category_id:
            return render(request, 'b_worker_onboarding_step1.html', {
                'job_categories': JobCategory.objects.all(),
                'error': '직무를 선택해주세요.',
                'selected_id': None,
            })
        # 세션에 저장 - 마지막 단계에서 WorkerProfile 일괄 생성
        request.session['onboarding_job_category_id'] = int(job_category_id)
        return redirect('worker:onboarding_step2')

    return render(request, 'b_worker_onboarding_step1.html', {
        'job_categories': JobCategory.objects.all(),
        'selected_id': request.session.get('onboarding_job_category_id'),
    })


@role_required('WORKER')
def onboarding_step2(request):
    if request.user.onboarding_completed:
        return _worker_completed_redirect(request)

    # step1에서 직무를 선택하지 않고 직접 접근하면 step1으로 되돌림
    job_category_id = request.session.get('onboarding_job_category_id')
    if not job_category_id:
        return redirect('worker:onboarding_step1')

    if request.method == 'POST':
        skill_ids   = request.POST.getlist('skills') # 다중 선택
        career_years = request.POST.get('career_years', '').strip()
        achievement  = request.POST.get('achievement_keywords', '').strip()
        gap_text     = request.POST.get('gap_activities', '').strip()

        errors = {}
        if not career_years:
            errors['career_years'] = '경력 연차를 선택해주세요.'

        if errors:
            skills = JobSkill.objects.filter(
                job_category_id=job_category_id
            ).select_related('skill')
            return render(request, 'b_worker_onboarding_step2.html', {
                'skills': skills,
                'career_choices': WorkerProfile.CareerYears.choices,
                'selected_skills': list(map(int, skill_ids)),
                'selected_career': career_years,
                'achievement_keywords': achievement,
                'gap_activities': gap_text,
                'errors': errors,
            })

        # 세션에 저장
        request.session['onboarding_skill_ids']          = list(map(int, skill_ids))
        request.session['onboarding_career_years']       = career_years
        request.session['onboarding_achievement']        = achievement
        # 쉼표로 분리해서 공백 제거 후 빈 항목 제거
        gap_items = [item.strip() for item in gap_text.split(',') if item.strip()]
        request.session['onboarding_gap_activities']     = gap_items

        return redirect('worker:onboarding_step3')

    skills = JobSkill.objects.filter(
        job_category_id=job_category_id
    ).select_related('skill')

    gap_error = request.session.pop('onboarding_gap_error', None)

    return render(request, 'b_worker_onboarding_step2.html', {
        'skills': skills,
        'career_choices': WorkerProfile.CareerYears.choices,
        'selected_skills': request.session.get('onboarding_skill_ids', []),
        'selected_career': request.session.get('onboarding_career_years', ''),
        'achievement_keywords': request.session.get('onboarding_achievement', ''),
        'gap_activities': ', '.join(request.session.get('onboarding_gap_activities', [])),
        'errors': {},
        'gap_error': gap_error,
    })


@role_required('WORKER')
def onboarding_step3(request):
    if request.user.onboarding_completed:
        return _worker_completed_redirect(request)

    if not request.session.get('onboarding_job_category_id'):
        return redirect('worker:onboarding_step1')
    if not request.session.get('onboarding_career_years'):
        return redirect('worker:onboarding_step2')

    if request.method == 'POST':
        weekly_hours = request.POST.get('weekly_hours', '').strip()
        preferred_work_style = request.POST.get('preferred_work_style', '').strip()
        core_time_ids = request.POST.getlist('core_times')
        preferred_scales = request.POST.getlist('preferred_scales')

        errors = {}
        if not weekly_hours:
            errors['weekly_hours'] = '주간 가용 시간을 선택해주세요.'
        if not preferred_work_style:
            errors['preferred_work_style'] = '선호 근무 형태를 선택해주세요.'

        if errors:
            return render(request, 'b_worker_onboarding_step3.html', {
                'weekly_hours_choices': WorkerProfile.WeeklyHours.choices,
                'work_style_choices': WorkerProfile.WorkStyle.choices,
                'time_slots': TimeSlot.objects.all(),
                'scale_choices': WorkerPreferredScale.ScaleType.choices,
                'selected_weekly_hours': weekly_hours,
                'selected_work_style': preferred_work_style,
                'selected_core_times': [int(time_id) for time_id in core_time_ids],
                'selected_scales': preferred_scales,
                'errors': errors,
            })

        request.session['onboarding_weekly_hours'] = weekly_hours
        request.session['onboarding_preferred_work_style'] = preferred_work_style
        request.session['onboarding_core_time_ids'] = [
            int(time_id) for time_id in core_time_ids
        ]
        request.session['onboarding_preferred_scales'] = preferred_scales

        return redirect('worker:onboarding_step4')

    return render(request, 'b_worker_onboarding_step3.html', {
        'weekly_hours_choices': WorkerProfile.WeeklyHours.choices,
        'work_style_choices': WorkerProfile.WorkStyle.choices,
        'time_slots': TimeSlot.objects.all(),
        'scale_choices': WorkerPreferredScale.ScaleType.choices,
        'selected_weekly_hours': request.session.get('onboarding_weekly_hours', ''),
        'selected_work_style': request.session.get(
            'onboarding_preferred_work_style', ''
        ),
        'selected_core_times': request.session.get('onboarding_core_time_ids', []),
        'selected_scales': request.session.get('onboarding_preferred_scales', []),
        'errors': {},
    })


@role_required('WORKER')
def onboarding_step4(request):
    if request.user.onboarding_completed:
        return _worker_completed_redirect(request)

    if not request.session.get('onboarding_job_category_id'):
        return redirect('worker:onboarding_step1')
    if not request.session.get('onboarding_career_years'):
        return redirect('worker:onboarding_step2')
    if not request.session.get('onboarding_weekly_hours'):
        return redirect('worker:onboarding_step3')

    if request.method == 'POST':
        application_type = request.POST.get('application_type', '').strip()
        concern_types = request.POST.getlist('concerns')

        errors = {}
        if application_type not in {
            WorkerProfile.ApplicationType.WARMUP,
            WorkerProfile.ApplicationType.REAL,
        }:
            errors['application_type'] = '업무 지원 방식을 선택해주세요.'

        if errors:
            return render(request, 'b_worker_onboarding_step4.html', {
                'application_type_choices': WorkerProfile.ApplicationType.choices,
                'concern_choices': WorkerConcern.ConcernType.choices,
                'selected_application_type': application_type,
                'selected_concerns': concern_types,
                'errors': errors,
            })

        gap_activities = request.session.get('onboarding_gap_activities', [])
        job_category_id = request.session['onboarding_job_category_id']
        hidden_ability_ids = classify_hidden_abilities(gap_activities, job_category_id)

        # 활동을 입력했는데 전부 유효하지 않으면 step2로 되돌림
        if gap_activities and all(ability_id is None for ability_id in hidden_ability_ids):
            request.session['onboarding_gap_error'] = '활동을 조금 더 구체적으로 입력해주세요. (예: 지역구 선거 참여, 주식 차트 분석)'
            return redirect('worker:onboarding_step2')

        with transaction.atomic():
            worker_profile, _ = WorkerProfile.objects.update_or_create(
                user=request.user,
                defaults={
                    'job_category_id': request.session['onboarding_job_category_id'],
                    'career_years': request.session['onboarding_career_years'],
                    'achievement_keywords': request.session.get('onboarding_achievement', ''),
                    'weekly_hours': request.session['onboarding_weekly_hours'],
                    'preferred_work_style': request.session['onboarding_preferred_work_style'],
                    'application_type': application_type,
                },
            )

            WorkerSkill.objects.filter(worker_profile=worker_profile).delete()
            WorkerHiddenActivity.objects.filter(worker_profile=worker_profile).delete()
            WorkerCoreTime.objects.filter(worker_profile=worker_profile).delete()
            WorkerPreferredScale.objects.filter(worker_profile=worker_profile).delete()
            WorkerConcern.objects.filter(worker_profile=worker_profile).delete()

            for skill_id in request.session.get('onboarding_skill_ids', []):
                WorkerSkill.objects.create(worker_profile=worker_profile, skill_id=skill_id)

            for activity_text, hidden_ability_id in zip(gap_activities, hidden_ability_ids):
                if hidden_ability_id is None:
                    continue
                WorkerHiddenActivity.objects.create(
                    worker_profile=worker_profile,
                    activity_text=activity_text,
                    hidden_ability_id=hidden_ability_id,)

            for time_slot_id in request.session.get('onboarding_core_time_ids', []):
                WorkerCoreTime.objects.create(
                    worker_profile=worker_profile,
                    time_slot_id=time_slot_id,
                )

            for scale_type in request.session.get('onboarding_preferred_scales', []):
                WorkerPreferredScale.objects.create(
                    worker_profile=worker_profile,
                    scale_type=scale_type,
                )

            for concern_type in concern_types:
                WorkerConcern.objects.create(
                    worker_profile=worker_profile,
                    concern_type=concern_type,
                )

            request.user.onboarding_completed = True
            request.user.save(update_fields=['onboarding_completed'])

        request.session['show_worker_onboarding_results'] = True

        for key in [
            'onboarding_job_category_id',
            'onboarding_skill_ids',
            'onboarding_career_years',
            'onboarding_achievement',
            'onboarding_gap_activities',
            'onboarding_weekly_hours',
            'onboarding_preferred_work_style',
            'onboarding_core_time_ids',
            'onboarding_preferred_scales',
        ]:
            request.session.pop(key, None)

        return redirect('worker:hidden_ability_result')

    return render(request, 'b_worker_onboarding_step4.html', {
        'application_type_choices': WorkerProfile.ApplicationType.choices,
        'concern_choices': WorkerConcern.ConcernType.choices,
        'selected_application_type': '',
        'selected_concerns': [],
        'errors': {},
    })


@role_required('WORKER')
@onboarding_required
def project_list(request):
    request.session.pop('show_worker_onboarding_results', None)

    view_type = request.GET.get('type', 'real')
    if view_type not in {'real', 'warmup'}:
        view_type = 'real'

    current_sort = request.GET.get('sort', 'matching')
    if current_sort not in {'matching', 'deadline', 'latest'}:
        current_sort = 'matching'
        
    keyword = request.GET.get('keyword', '').strip()
        
    selected_job_categories = [
        int(cat_id) for cat_id in request.GET.getlist('job_category')
        if cat_id.isdigit()
    ]
    valid_work_style_values = {value for value, _ in WorkerProfile.WorkStyle.choices}
    selected_work_styles = [
        style for style in request.GET.getlist('work_style')
        if style in valid_work_style_values
    ]

    worker_profile = _get_prefetched_worker_profile(request.user)

    projects_qs = Project.objects.filter(
        status=Project.Status.OPEN,
    ).select_related('company_profile', 'job_category').prefetch_related(
        'project_skills__skill',
        'preferred_scales',
        'hidden_abilities__hidden_ability',
    ).order_by('-id')
    
    if keyword:
        projects_qs = projects_qs.filter(
        Q(title__icontains=keyword)
        | Q(company_profile__company_name__icontains=keyword)
        | Q(project_skills__skill__name__icontains=keyword)
        ).distinct()

    
    if selected_job_categories:
        projects_qs = projects_qs.filter(job_category_id__in=selected_job_categories)

    if selected_work_styles:
        projects_qs = projects_qs.filter(work_style__in=selected_work_styles)


    real_projects = projects_qs.filter(
        project_type=Project.ProjectType.REAL,
    )

    warmup_projects = projects_qs.filter(
        project_type=Project.ProjectType.WARMUP,
    )

    if view_type == 'warmup':
        ranked_projects = list(warmup_projects)
        for project in ranked_projects:
            project.match_score = 100
            project.preferred_skills_list = [
                project_skill.skill
                for project_skill in project.project_skills.all()
                if project_skill.priority == 'PREFERRED'
            ]
        projects = ranked_projects
    else:
        ranked_projects = rank_projects_for_worker(worker_profile, list(real_projects)) if worker_profile else list(real_projects)
        for project in ranked_projects:
            project.preferred_skills_list = [
                project_skill.skill
                for project_skill in project.project_skills.all()
                if project_skill.priority == 'PREFERRED'
            ]

        if current_sort == 'deadline':
            projects = sorted(ranked_projects, key=lambda project: (project.deadline, project.created_at, project.id))
        elif current_sort == 'latest':
            projects = sorted(ranked_projects, key=lambda project: (project.created_at, project.id), reverse=True)
        else:
            projects = ranked_projects

    today = timezone.localdate()
    for project in projects:
        project.deadline_d_day = (project.deadline - today).days

    top_projects = ranked_projects[:3]

    worker_hidden_abilities = get_worker_hidden_abilities(worker_profile) if worker_profile else []
    
    #페이지 6개 단위, 더보기
    PAGE_SIZE = 6
    try:
        page_number = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
         page_number = 1
    page_number = max(page_number, 1)
    
    total_count = len(projects)
    visible_count = page_number * PAGE_SIZE
    projects_to_show = projects[:visible_count]
    has_next_page = visible_count < total_count
    
    next_querystring = request.GET.copy()
    next_querystring['page'] = page_number + 1
    next_page_querystring = next_querystring.urlencode()

    return render(request, 'b_project_list.html', {
        'projects': projects_to_show,
        'project_count': total_count,
        'top_projects': top_projects,
        'worker_hidden_abilities': worker_hidden_abilities,
        'view_type': view_type,
        'current_sort': current_sort,
        'job_categories': JobCategory.objects.all(),
        'work_style_choices': WorkerProfile.WorkStyle.choices,
        'selected_job_categories': selected_job_categories,
        'selected_work_styles': selected_work_styles,
        'keyword': keyword,
        'has_next_page': has_next_page,
        'next_page_querystring': next_page_querystring,
    })


@role_required('WORKER')
@onboarding_required
def hidden_ability_result(request):
    worker_profile = _get_prefetched_worker_profile(request.user)
    hidden_abilities = get_worker_hidden_abilities(worker_profile) if worker_profile else []
    activities = worker_profile.hidden_activities.select_related('hidden_ability').all() if worker_profile else []

    # 공백기 활동을 입력하지 않았거나 분류된 숨은 능력이 없으면 바로 매칭 결과로
    if not activities or not hidden_abilities:
        return redirect('worker:match_top3_result')

    grouped_activities = OrderedDict()
    for activity in activities:
        ability_name = activity.hidden_ability.name if activity.hidden_ability else '분류 대기'
        if ability_name not in grouped_activities:
            grouped_activities[ability_name] = []
        grouped_activities[ability_name].append(activity.activity_text)

    return render(request, 'b_worker_onboarding_result_hidden.html', {
        'worker_profile': worker_profile,
        'hidden_abilities': hidden_abilities,
        'activities': activities,
        'grouped_activities': grouped_activities.items(),
        'hidden_ability_count': len(hidden_abilities),
    })


@role_required('WORKER')
@onboarding_required
def match_top3_result(request):
    worker_profile = _get_prefetched_worker_profile(request.user)

    projects_qs = Project.objects.filter(
        status=Project.Status.OPEN,
    ).select_related('company_profile', 'job_category').prefetch_related(
        'project_skills__skill',
        'core_times__time_slot',
        'preferred_scales',
        'hidden_abilities__hidden_ability',
    ).order_by('-id')

    if worker_profile and worker_profile.application_type == WorkerProfile.ApplicationType.WARMUP:
        top_projects = list(projects_qs.filter(project_type=Project.ProjectType.WARMUP)[:3])
        for project in top_projects:
            project.match_score = 100
            project.preferred_skills_list = [
                project_skill.skill
                for project_skill in project.project_skills.all()
                if project_skill.priority == 'PREFERRED'
            ]
        best_match_score = 100 if top_projects else 0
        high_match_count = len(top_projects)
        is_warmup_mode = True
    else:
        ranked_projects = rank_projects_for_worker(
            worker_profile,
            list(projects_qs.filter(project_type=Project.ProjectType.REAL)),
        ) if worker_profile else list(projects_qs.filter(project_type=Project.ProjectType.REAL))
        for project in ranked_projects:
            project.preferred_skills_list = [
                project_skill.skill
                for project_skill in project.project_skills.all()
                if project_skill.priority == 'PREFERRED'
            ]

        top_projects = ranked_projects[:3]
        best_match_score = top_projects[0].match_score if top_projects else 0
        high_match_count = sum(1 for project in ranked_projects if getattr(project, 'match_score', 0) >= 80)
        is_warmup_mode = False

    return render(request, 'b_worker_onboarding_result_match.html', {
        'worker_profile': worker_profile,
        'top_projects': top_projects,
        'best_match_score': best_match_score,
        'high_match_count': high_match_count,
        'is_warmup_mode': is_warmup_mode,
    })
