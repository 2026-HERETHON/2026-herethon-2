def resolve_redirect_url(user, request=None):
# 로그인 후 리다이렉트할 URL을 결정하는 유틸 함수
    if not user.role:
        return 'accounts:role_select'

    if not user.onboarding_completed:
        if user.role == 'WORKER':
            return 'worker:onboarding_step1'
        return 'company:onboarding'

    if user.role == 'WORKER':
        if request and request.session.get('show_worker_onboarding_results'):
            return 'worker:hidden_ability_result'
            # 온보딩 방금 완료한 경우, 숨은 능력 결과 페이지로 이동
        return 'worker:project_list'
        # 이미 결과를 본 경우, 프로젝트 리스트 페이지로 이동
    return 'company:project_create'