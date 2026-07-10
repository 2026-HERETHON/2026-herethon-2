def resolve_redirect_url(user, request=None):
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