import secrets
from urllib.parse import urlencode

import requests
from requests import RequestException

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import User
from .utils import resolve_redirect_url


GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


def landing(request):
    if request.user.is_authenticated:
        return redirect(resolve_redirect_url(request.user, request))

    return render(request, 'b_landing.html')


def google_login(request):
    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state

    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account',
    }

    return redirect(f'{GOOGLE_AUTH_URL}?{urlencode(params)}')


def google_callback(request):
    if request.GET.get('error'):
        return redirect('accounts:landing')

    received_state = request.GET.get('state')
    saved_state = request.session.pop('google_oauth_state', None)

    if not received_state or received_state != saved_state:
        return redirect('accounts:landing')

    code = request.GET.get('code')

    if not code:
        return redirect('accounts:landing')

    try:
        token_res = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            },
            timeout=10,
        )
        token_res.raise_for_status()

        access_token = token_res.json().get('access_token')

        if not access_token:
            return redirect('accounts:landing')

        userinfo_res = requests.get(
            GOOGLE_USERINFO_URL,
            headers={
                'Authorization': f'Bearer {access_token}',
            },
            timeout=10,
        )
        userinfo_res.raise_for_status()
        info = userinfo_res.json()

    except (RequestException, ValueError):
        return redirect('accounts:landing')

    google_uid = info.get('sub')

    if not google_uid:
        return redirect('accounts:landing')

    user, _ = User.objects.get_or_create(
        google_uid=google_uid,
        defaults={
            'username': google_uid,
            'email': info.get('email', ''),
            'name': info.get('name', ''),
            'profile_image_url': info.get('picture', ''),
        },
    )

    login(request, user)

    return redirect(resolve_redirect_url(user, request))


@login_required
def role_select(request):
    if request.user.role:
        return redirect(resolve_redirect_url(request.user, request))

    if request.method == 'POST':
        role = request.POST.get('role')

        if role not in ('WORKER', 'COMPANY'):
            return render(
                request,
                'b_role_select.html',
                {'error': '역할을 선택해주세요.'},
            )

        request.user.role = role
        request.user.save(update_fields=['role'])

        return redirect(resolve_redirect_url(request.user, request))

    return render(request, 'b_role_select.html')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('accounts:landing')
