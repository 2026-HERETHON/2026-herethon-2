from functools import wraps

from django.shortcuts import redirect

def role_required(required_role):
    # 로그인 여부 + role인지 체크
    # 비로그인 -> 랜딩으로
    # role이 없거나 다른 role -> 역할선택으로
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:landing')
            if request.user.role != required_role:
                return redirect('accounts:role_select')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def onboarding_required(view_func):
    # 온보딩 완료 여부 체크
    # 비로그인 -> 랜딩으로
    # role 없음 -> 역할선택으로
    # 온보딩 미완료 -> 역할별 온보딩 페이지로
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:landing')
        if not request.user.role:
            return redirect('accounts:role_select')
        if not request.user.onboarding_completed:
            if request.user.role == 'WORKER':
                return redirect('worker:onboarding_step1')
            return redirect('company:onboarding')
        return view_func(request, *args, **kwargs)
    return _wrapped