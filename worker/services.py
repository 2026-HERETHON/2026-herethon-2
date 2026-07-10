import json
import re

from django.conf import settings
from openai import OpenAI

from core.models import JobHiddenAbility
from projects.models import ProjectSkill

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 경력 기간을 비교하기 위한 순위값
# 숫자가 클수록 경력이 긴 것으로 판단
CAREER_RANK = {
    'ONE_TO_THREE': 1,
    'THREE_TO_FIVE': 2,
    'FIVE_TO_SEVEN': 3,
    'OVER_SEVEN': 4,
}

# 주당 근무 가능 시간을 비교하기 위한 순위값
# 숫자가 클수록 더 많은 시간 근무 가능
WEEKLY_HOURS_RANK = {
    'UNDER_15': 1,
    'FIFTEEN_TO_25': 2,
    'OVER_25': 3,
}


def _weighted_ratio(matched_count, total_count, weight):
    if total_count == 0:
        return weight
    return round((matched_count / total_count) * weight)


def get_worker_hidden_abilities(worker_profile):
    # 숨은 능력 목록을 가져온다. (중복 제거)
    abilities = []
    seen_ids = set()

    for activity in worker_profile.hidden_activities.select_related('hidden_ability').all():
        hidden_ability = activity.hidden_ability
        if hidden_ability is None or hidden_ability.id in seen_ids:
            continue
        seen_ids.add(hidden_ability.id)
        abilities.append(hidden_ability)

    return abilities


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
    # 프로젝트 필수 기술
    required_skills = [
        relation for relation in project_skill_relations
        if relation.priority == ProjectSkill.Priority.NORMAL
    ]
    # 프로젝트 우대 기술
    preferred_skills = [
        relation for relation in project_skill_relations
        if relation.priority == ProjectSkill.Priority.PREFERRED
    ]
    # 프로젝트가 요구하는 숨은 역량
    project_hidden_relations = list(
        project.hidden_abilities.select_related('hidden_ability').all()
    )
    project_hidden_ability_ids = {
        relation.hidden_ability_id
        for relation in project_hidden_relations
        if 
        relation.hidden_ability_id is not None
    }
    # 프로젝트가 요구하는 업무 규모
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


def is_valid_activity_text(text):
    """명백한 무의미 입력만 1차로 차단한다."""
    if not text:
        return False

    text = text.strip()

    if len(text) < 2:
        return False

    invalid_values = {
        '없음',
        '모름',
        '몰라',
        '아무거나',
        '테스트',
        'test',
    }

    if text.lower() in invalid_values:
        return False

    # 한글이나 영문이 하나도 없는 경우
    if not re.search(r'[가-힣A-Za-z]', text):
        return False

    compact = text.replace(' ', '')

    # 같은 문자만 반복된 경우: ㅋㅋㅋ, aaa
    if len(set(compact)) == 1:
        return False

    return True


def classify_hidden_abilities(activities, job_category_id):
    if not activities:
        return []

    relations = list(
        JobHiddenAbility.objects
        .filter(job_category_id=job_category_id)
        .select_related('hidden_ability')
    )
    if not relations:
        return [None] * len(activities)

    code_to_id = {rel.hidden_ability.code: rel.hidden_ability_id for rel in relations}
    ability_codes = list(code_to_id.keys())
    allowed_codes = ability_codes + ['INVALID']

    # 1차 검증: 유효한 항목만 AI로 넘김
    valid_indexes = []
    valid_activities = []
    for index, activity in enumerate(activities):
        if is_valid_activity_text(activity):
            valid_indexes.append(index)
            valid_activities.append(activity.strip())

    if not valid_activities:
        return [None] * len(activities)

    options_text = '\n'.join(
        f'- {rel.hidden_ability.code}: {rel.hidden_ability.name} ({rel.hidden_ability.description})'
        for rel in relations
    )
    activities_text = '\n'.join(
        f'{i + 1}. {text}' for i, text in enumerate(valid_activities)
    )

    prompt = f"""
당신은 경력 공백기 동안의 활동을 분석하여,
그 활동에서 드러나는 업무 역량으로 분류하는 역할을 합니다.

다음처럼 의미가 없거나 활동이라고 보기 어려운 입력만 INVALID로 분류하세요.

- 한 글자 또는 의미 없는 짧은 입력
- 자음, 숫자, 같은 문자 반복
- "없음", "모름", "아무거나", "테스트" 같은 표현

그 외에는 활동이 짧거나 다소 포괄적이더라도
아래 숨은 능력 후보 중 가장 가까운 하나를 선택하세요.

예:
- 지역구 선거 참여 → 유효
- 주식 차트 분석 → 유효
- 커뮤니티 운영 → 유효
- 학교 행사 참여 → 유효
- 아이 돌봄 → 유효

[숨은 능력 후보]
{options_text}

[분석할 활동 목록]
{activities_text}

각 활동 순서대로 코드를 반환하세요.
명백하게 의미 없는 입력만 INVALID로 반환하세요.
""".strip()

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            response_format={
                'type': 'json_schema',
                'json_schema': {
                    'name': 'hidden_ability_batch_classification',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'results': {
                                'type': 'array',
                                'items': {
                                    'type': 'string',
                                    'enum': allowed_codes,
                                },
                                'minItems': len(valid_activities),
                                'maxItems': len(valid_activities),
                            }
                        },
                        'required': ['results'],
                        'additionalProperties': False,
                    },
                    'strict': True,
                },
            },
        )
        result = json.loads(response.choices[0].message.content)
        codes = result['results']
    except Exception:
        return [None] * len(activities)

    classified_ids = [None] * len(activities)
    for original_index, code in zip(valid_indexes, codes):
        if code != 'INVALID':
            classified_ids[original_index] = code_to_id.get(code)

    return classified_ids