from projects.models import ProjectSkill

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
    if total_count == 0:
        return weight
    return round((matched_count / total_count) * weight)


def score_project_match(worker_profile, project):
    worker_skill_ids = {
        worker_skill.skill_id
        for worker_skill in worker_profile.worker_skills.select_related('skill').all()
    }
    worker_hidden_ability_ids = {
        activity.hidden_ability_id
        for activity in worker_profile.hidden_activities.select_related('hidden_ability').all()
        if activity.hidden_ability_id is not None
    }
    worker_scale_types = {
        preferred_scale.scale_type
        for preferred_scale in worker_profile.preferred_scales.all()
    }

    project_skill_relations = list(project.project_skills.select_related('skill').all())
    required_skills = [
        relation for relation in project_skill_relations
        if relation.priority == ProjectSkill.Priority.NORMAL
    ]
    preferred_skills = [
        relation for relation in project_skill_relations
        if relation.priority == ProjectSkill.Priority.PREFERRED
    ]

    project_hidden_relations = list(
        project.hidden_abilities.select_related('hidden_ability').all()
    )
    project_hidden_ability_ids = {
        relation.hidden_ability_id
        for relation in project_hidden_relations
        if relation.hidden_ability_id is not None
    }
    project_scale_types = {
        scale.scale_type for scale in project.preferred_scales.all()
    }

    job_category_score = 20 if worker_profile.job_category_id == project.job_category_id else 0
    work_style_score = 15 if worker_profile.preferred_work_style == project.work_style else 0

    required_skill_matches = sum(
        1 for relation in required_skills if relation.skill_id in worker_skill_ids
    )
    required_skill_score = _weighted_ratio(required_skill_matches, len(required_skills), 25)

    preferred_skill_matches = sum(
        1 for relation in preferred_skills if relation.skill_id in worker_skill_ids
    )
    preferred_skill_score = _weighted_ratio(preferred_skill_matches, len(preferred_skills), 10)

    if not project_hidden_ability_ids:
        hidden_ability_score = 10
    else:
        hidden_ability_matches = len(project_hidden_ability_ids & worker_hidden_ability_ids)
        hidden_ability_score = _weighted_ratio(
            hidden_ability_matches,
            len(project_hidden_ability_ids),
            10,
        )

    weekly_hours_score = 10 if WEEKLY_HOURS_RANK.get(worker_profile.weekly_hours, 0) >= WEEKLY_HOURS_RANK.get(project.weekly_hours, 0) else 0
    project_scale_score = (
        5
        if not project_scale_types or (project_scale_types & worker_scale_types)
        else 0
    )
    career_years_score = 5 if CAREER_RANK.get(worker_profile.career_years, 0) >= CAREER_RANK.get(project.career_years, 0) else 0

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

    project.match_score = total_score
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
    project.required_skill_total = len(required_skills)
    project.required_skill_matches = required_skill_matches
    project.preferred_skill_total = len(preferred_skills)
    project.preferred_skill_matches = preferred_skill_matches
    project.project_hidden_abilities_list = [
        relation.hidden_ability for relation in project_hidden_relations if relation.hidden_ability is not None
    ]
    project.matched_hidden_abilities_list = [
        hidden_ability for hidden_ability in project.project_hidden_abilities_list
        if hidden_ability.id in worker_hidden_ability_ids
    ]

    return project


def rank_projects_for_worker(worker_profile, projects):
    ranked_projects = [score_project_match(worker_profile, project) for project in projects]
    ranked_projects.sort(key=lambda project: (-project.match_score, project.deadline, -project.id))
    return ranked_projects
