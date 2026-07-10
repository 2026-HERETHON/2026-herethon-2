from django.shortcuts import render
import requests
import secrets
from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from .models import User

#def landing(request):
 #   return render(request, 'landing.html')


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def landing(request): #랜딩페이지
    
    return render(request, 'accounts/landing.html')


def google_login(request): #시작하기(2개) 버튼 눌렀을 때 실행됨 -> 구글 로그인 페이지로 보냄
    
    state = secrets.token_urlsafe(16)
    request.session['google_oauth_state'] = state

    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile', #구글에서 받아오는 정보 openid email profile 요청
        'state': state,
        'prompt': 'select_account',
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return redirect(f"{GOOGLE_AUTH_URL}?{query}")


def google_callback(request): #구글에서 로그인 끝내고 우리 사이트로 돌아왔을 때 실행됨

    # 혹시 유저가 구글 로그인 취소했으면
    if request.GET.get('error'):
        return redirect('landing')

    # 보안 체크 (CSRF 방지) - 우리가 보낸 state랑 같은지 확인
    state = request.GET.get('state')
    if state != request.session.get('google_oauth_state'):
        return redirect('landing')

    code = request.GET.get('code')
    
    if not code:
        return redirect('landing')

    # code를 진짜 토큰으로 교환
    token_res = requests.post(GOOGLE_TOKEN_URL, data={
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
    })
    print("TOKEN RESPONSE:", token_res.status_code, token_res.json())
    access_token = token_res.json().get('access_token')

    # 토큰으로 유저 정보(이메일/이름/사진) 받아오기
    userinfo_res = requests.get(
        GOOGLE_USERINFO_URL,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    info = userinfo_res.json()

    # 우리 DB에서 이 유저 찾기, 없으면 새로 만들기
    user, created = User.objects.get_or_create(
        google_uid=info['sub'], #필수 구글 고유 ID
        defaults={
            'username': info['sub'],
            'email': info.get('email', ''),
            'name': info.get('name', ''),
            'profile_image_url': info.get('picture', ''),
        }
    )

    
    login(request, user)

    return render(request, 'accounts/success.html', {'user': user, 'created': created})


def logout_view(request):
    logout(request)
    return redirect('landing')
