from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from projects.models import Application, Project, Returnship
from worker.services.matching import rank_projects_for_worker
from worker.models import WorkerProfile, WorkerSkill
from core.models import JobCategory, Skill


# [공통] 상단 프로필 요약
def _get_mypage_context(request):
    worker_profile = request.user.worker_profile
    completed_count = Application.objects.filter(
        worker_profile=worker_profile,
        status=Application.Status.ACCEPTED,
        project__status=Project.Status.COMPLETED,
    ).count()

    return {
        'user': request.user,
        'worker_profile': worker_profile,
        'completed_count': completed_count,
    }

@login_required
def mypage_dashboard(request):
    
    context = _get_mypage_context(request)
    worker_profile = context['worker_profile']

    #프로필
    context['worker_skills'] = worker_profile.worker_skills.select_related('skill')
    context['hidden_activities'] = worker_profile.hidden_activities.select_related('hidden_ability')

    applications_accepted = Application.objects.filter(
        worker_profile=worker_profile,
        status=Application.Status.ACCEPTED,
    ).select_related('project', 'project__company_profile', 'project__job_category')

    in_progress_raw = [a.project for a in applications_accepted if a.project.status == Project.Status.IN_PROGRESS]
    completed_raw = [a.project for a in applications_accepted if a.project.status == Project.Status.COMPLETED]

    context['in_progress_projects'] = rank_projects_for_worker(worker_profile, in_progress_raw) if in_progress_raw else []
    context['completed_projects'] = rank_projects_for_worker(worker_profile, completed_raw) if completed_raw else []


    #지원현황
    all_applications = list(
        Application.objects.filter(
            worker_profile=worker_profile,
        ).select_related('project', 'project__company_profile', 'project__job_category')
    )

    if all_applications:
        projects = [a.project for a in all_applications]
        ranked_projects = rank_projects_for_worker(worker_profile, projects)
        app_by_project_id = {a.project_id: a for a in all_applications}
        applications = []
        for p in ranked_projects:
            app = app_by_project_id[p.id]
            app.project = p  
            applications.append(app)
        context['applications'] = applications
    else:
        context['applications'] = []


    #리턴십 제안
    all_offers = Returnship.objects.filter(
        application__worker_profile=worker_profile
    ).select_related('application__project__company_profile').order_by('-created_at')

    context['pending_offers'] = [o for o in all_offers if o.status == Returnship.Status.PENDING]
    context['past_offers'] = [o for o in all_offers if o.status != Returnship.Status.PENDING]


    #근무 조건
    context['job_categories'] = JobCategory.objects.all()
    context['skills'] = Skill.objects.all()
    context['work_style_choices'] = WorkerProfile.WorkStyle.choices
    context['selected_skill_ids'] = list(
        worker_profile.worker_skills.values_list('skill_id', flat=True)
    )

    return render(request, 'b_worker_mypage.html', context)


@login_required
@require_POST
def cancel_application(request, application_id): #지원 취소

    worker_profile = request.user.worker_profile
    application = get_object_or_404(Application, id=application_id, worker_profile=worker_profile)

    if application.status != Application.Status.PENDING:
        messages.error(request, '심사중인 지원만 취소할 수 있습니다.')
        return redirect('/mypage/?tab=apply')

    application.delete()
    messages.success(request, '지원이 취소되었습니다.')
    return redirect('/mypage/?tab=apply')


@login_required
@require_POST
def respond_returnship(request, returnship_id):
    
    worker_profile = request.user.worker_profile
    offer = get_object_or_404(Returnship, id=returnship_id, application__worker_profile=worker_profile)

    if offer.status != Returnship.Status.PENDING:
        messages.error(request, '이미 응답한 제안입니다.')
        return redirect('/mypage/?tab=offer')

    action = request.POST.get('action')
    if action == 'accept':
        offer.status = Returnship.Status.ACCEPTED
    elif action == 'reject':
        offer.status = Returnship.Status.REJECTED
    else:
        messages.error(request, '잘못된 요청입니다.')
        return redirect('/mypage/?tab=offer')

    offer.save(update_fields=['status'])
    return redirect('/mypage/?tab=offer')

@login_required
@require_POST
def work_conditions(request):
    """근무 조건 수정하기"""
    worker_profile = request.user.worker_profile

    job_category_id = request.POST.get('job_category')
    skill_ids = request.POST.getlist('skills')
    preferred_work_style = request.POST.get('preferred_work_style')

    worker_profile.job_category_id = job_category_id
    worker_profile.preferred_work_style = preferred_work_style
    worker_profile.save(update_fields=['job_category', 'preferred_work_style'])

    # 스킬-삭제 후 재등록
    WorkerSkill.objects.filter(worker_profile=worker_profile).delete()
    WorkerSkill.objects.bulk_create([
        WorkerSkill(worker_profile=worker_profile, skill_id=sid) for sid in skill_ids
    ])

    messages.success(request, '근무 조건이 저장되었습니다.')
    return redirect('/mypage/?tab=condition')