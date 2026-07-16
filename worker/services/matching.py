from projects.models import ProjectSkill


# 매칭 항목별 최대 배점
MATCH_WEIGHTS = {
    'job_category': 30,
    'work_style': 15,
    'required_skill': 25,
    'preferred_skill': 10,
    'hidden_ability': 10,
    'weekly_hours': 5,
    'project_scale': 3,
    'career_years': 2,
}


CAREER_RANK = {
    'ONE_TO_THREE': 1,
    'THREE_TO_FIVE': 2,
    'FIVE_TO_SEVEN': 3,
    'OVER_SEVEN': 4,
}


WEEKLY_HOURS_RANK = {
    'UNDER_15': 1,
    'FIFTEEN_TO_25': 2,
    'OVER_25': 3,
}


def _weighted_ratio(matched_count, total_count, weight):
    # 프로젝트가 해당 조건을 지정하지 않은 경우 만점 처리
    if total_count == 0:
        return weight

    return round((matched_count / total_count) * weight)


def score_project_match(worker_profile, project):
    # 경력자가 보유한 스킬 ID
    worker_skill_ids = {
        worker_skill.skill_id
        for worker_skill in (
            worker_profile.worker_skills
            .select_related('skill')
            .all()
        )
    }

    # 경력자의 숨은 능력 ID
    worker_hidden_ability_ids = {
        activity.hidden_ability_id
        for activity in (
            worker_profile.hidden_activities
            .select_related('hidden_ability')
            .all()
        )
        if activity.hidden_ability_id is not None
    }

    # 경력자가 선호하는 업무 규모
    worker_scale_types = {
        preferred_scale.scale_type
        for preferred_scale in worker_profile.preferred_scales.all()
    }

    # 프로젝트 스킬 전체
    project_skill_relations = list(
        project.project_skills
        .select_related('skill')
        .all()
    )

    # 전체 요구 스킬
    # NORMAL + PREFERRED 모두 기본 스킬 점수에 포함
    required_skills = project_skill_relations

    # 전체 요구 스킬 중 우대 스킬
    # PREFERRED는 기본 점수에 포함되면서 우대 가산점도 받음
    preferred_skills = [
        relation
        for relation in project_skill_relations
        if relation.priority == ProjectSkill.Priority.PREFERRED
    ]

    # 프로젝트 숨은 능력
    project_hidden_relations = list(
        project.hidden_abilities
        .select_related('hidden_ability')
        .all()
    )

    project_hidden_ability_ids = {
        relation.hidden_ability_id
        for relation in project_hidden_relations
        if relation.hidden_ability_id is not None
    }

    # 프로젝트 업무 규모
    project_scale_types = {
        scale.scale_type
        for scale in project.preferred_scales.all()
    }

    # 희망 직무: 최대 30점
    job_category_score = (
        MATCH_WEIGHTS['job_category']
        if worker_profile.job_category_id == project.job_category_id
        else 0
    )

    # 근무 형태: 최대 15점
    work_style_score = (
        MATCH_WEIGHTS['work_style']
        if worker_profile.preferred_work_style == project.work_style
        else 0
    )

    # 전체 요구 스킬: 최대 25점
    required_skill_matches = sum(
        1
        for relation in required_skills
        if relation.skill_id in worker_skill_ids
    )

    required_skill_score = _weighted_ratio(
        matched_count=required_skill_matches,
        total_count=len(required_skills),
        weight=MATCH_WEIGHTS['required_skill'],
    )

    # 우대 스킬: 최대 10점
    preferred_skill_matches = sum(
        1
        for relation in preferred_skills
        if relation.skill_id in worker_skill_ids
    )

    preferred_skill_score = _weighted_ratio(
        matched_count=preferred_skill_matches,
        total_count=len(preferred_skills),
        weight=MATCH_WEIGHTS['preferred_skill'],
    )

    # 숨은 능력: 최대 10점
    if not project_hidden_ability_ids:
        hidden_ability_score = MATCH_WEIGHTS['hidden_ability']
    else:
        hidden_ability_matches = len(
            project_hidden_ability_ids
            & worker_hidden_ability_ids
        )

        hidden_ability_score = _weighted_ratio(
            matched_count=hidden_ability_matches,
            total_count=len(project_hidden_ability_ids),
            weight=MATCH_WEIGHTS['hidden_ability'],
        )

    # 주간 가용 시간: 최대 5점
    worker_weekly_hours_rank = WEEKLY_HOURS_RANK.get(
        worker_profile.weekly_hours,
        0,
    )
    project_weekly_hours_rank = WEEKLY_HOURS_RANK.get(
        project.weekly_hours,
        0,
    )

    weekly_hours_score = (
        MATCH_WEIGHTS['weekly_hours']
        if worker_weekly_hours_rank >= project_weekly_hours_rank
        else 0
    )

    # 업무 규모: 최대 3점
    project_scale_score = (
        MATCH_WEIGHTS['project_scale']
        if (
            not project_scale_types
            or bool(project_scale_types & worker_scale_types)
        )
        else 0
    )

    # 경력 연차: 최대 2점
    worker_career_rank = CAREER_RANK.get(
        worker_profile.career_years,
        0,
    )
    project_career_rank = CAREER_RANK.get(
        project.career_years,
        0,
    )

    career_years_score = (
        MATCH_WEIGHTS['career_years']
        if worker_career_rank >= project_career_rank
        else 0
    )

    # 총점
    total_score = (
        job_category_score
        + work_style_score
        + required_skill_score
        + preferred_skill_score
        + hidden_ability_score
        + weekly_hours_score
        + project_scale_score
        + career_years_score
    )

    project.match_score = min(total_score, 100)

    project.match_breakdown = {
        'job_category': job_category_score,
        'work_style': work_style_score,
        'required_skill': required_skill_score,
        'preferred_skill': preferred_skill_score,
        'hidden_ability': hidden_ability_score,
        'weekly_hours': weekly_hours_score,
        'project_scale': project_scale_score,
        'career_years': career_years_score,
    }

    # 전체 요구 스킬 매칭 정보
    project.required_skill_total = len(required_skills)
    project.required_skill_matches = required_skill_matches

    # 우대 스킬 매칭 정보
    project.preferred_skill_total = len(preferred_skills)
    project.preferred_skill_matches = preferred_skill_matches

    project.project_hidden_abilities_list = [
        relation.hidden_ability
        for relation in project_hidden_relations
        if relation.hidden_ability is not None
    ]

    project.matched_hidden_abilities_list = [
        hidden_ability
        for hidden_ability in project.project_hidden_abilities_list
        if hidden_ability.id in worker_hidden_ability_ids
    ]

    return project


def rank_projects_for_worker(worker_profile, projects):
    # 모든 프로젝트의 매칭 점수를 계산
    ranked_projects = [
        score_project_match(worker_profile, project)
        for project in projects
    ]

    # 매칭률에 따른 CSS 클래스 지정
    for project in ranked_projects:
        project.match_class = (
            'heart'
            if project.match_score >= 70
            else 'good'
        )

    # 매칭률 -> 마감일 -> 최신 등록순 정렬
    ranked_projects.sort(
        key=lambda project: (
            -project.match_score,
            project.deadline,
            -project.id,
        )
    )

    return ranked_projects
