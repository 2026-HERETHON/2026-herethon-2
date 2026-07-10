import json
import re

from django.conf import settings
from openai import OpenAI

from core.models import JobHiddenAbility

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_worker_hidden_abilities(worker_profile):
    abilities = []
    seen_ids = set()

    for activity in worker_profile.hidden_activities.select_related('hidden_ability').all():
        hidden_ability = activity.hidden_ability
        if hidden_ability is None or hidden_ability.id in seen_ids:
            continue
        seen_ids.add(hidden_ability.id)
        abilities.append(hidden_ability)

    return abilities


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

    if not re.search(r'[가-힣A-Za-z]', text):
        return False

    compact = text.replace(' ', '')

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
