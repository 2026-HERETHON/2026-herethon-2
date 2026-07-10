def resolve_redirect_url(user, request=None):
    # 유저 상태(role, onboarding_completed)에 따라 어디로 보내야 할지 URL name 리턴
    # 로그인 직후, 랜딩페이지 재접속 시 등 여러 곳에서 공통으로 사용되는 유틸
    if not user.role:
        return 'accounts:role_select'

    if not user.onboarding_completed:
        if user.role == 'WORKER':
            return 'worker:onboarding_step1'
        return 'company:onboarding'

    if user.role == 'WORKER':
        if request and request.session.get('show_worker_onboarding_results'):
            return 'worker:hidden_ability_result'
        return 'worker:project_list'
    return 'company:project_create'