# users/views.py
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from urllib.parse import urlencode
import requests

def kakao_login(request):
    """카카오 로그인 시작 - 사용자를 카카오 로그인 페이지로 리다이렉트"""
    kakao_auth_url = "https://kauth.kakao.com/oauth/authorize"
    params = {
        "client_id": settings.KAKAO_REST_API_KEY,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "response_type": "code"
    }
    url = f"{kakao_auth_url}?{urlencode(params)}"
    return redirect(url)

def kakao_callback(request):
    """카카오 로그인 콜백 - 인증 코드를 받아서 토큰 발급"""
    code = request.GET.get('code')
    
    if not code:
        return JsonResponse({"error": "인증 코드가 없습니다."}, status=400)
    
    # 1. 액세스 토큰 받기
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_REST_API_KEY,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "code": code
    }
    
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    if not access_token:
        return JsonResponse({"error": "토큰 발급 실패", "details": token_json}, status=400)
    
    # 2. 사용자 정보 가져오기
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_info_url, headers=headers)
    user_info = user_response.json()
    
    return JsonResponse({
        "message": "카카오 로그인 성공!",
        "access_token": access_token,
        "user_info": user_info
    })

def google_login(request):
    """구글 로그인 시작"""
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile"
    }
    url = f"{google_auth_url}?{urlencode(params)}"
    return redirect(url)

def google_callback(request):
    """구글 로그인 콜백"""
    code = request.GET.get('code')
    
    if not code:
        return JsonResponse({"error": "인증 코드가 없습니다."}, status=400)
    
    # 1. 액세스 토큰 받기
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "code": code
    }
    
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    if not access_token:
        return JsonResponse({"error": "토큰 발급 실패", "details": token_json}, status=400)
    
    # 2. 사용자 정보 가져오기
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_info_url, headers=headers)
    user_info = user_response.json()
    
    return JsonResponse({
        "message": "구글 로그인 성공!",
        "access_token": access_token,
        "user_info": user_info
    })

def test_login_page(request):
    """테스트용 로그인 페이지"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>소셜 로그인 테스트</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
            }
            .button {
                display: block;
                width: 100%;
                padding: 15px;
                margin: 10px 0;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                text-align: center;
            }
            .kakao {
                background-color: #FEE500;
                color: #000000;
            }
            .google {
                background-color: #4285F4;
                color: white;
            }
            h1 { text-align: center; }
        </style>
    </head>
    <body>
        <h1>🔐 소셜 로그인 테스트</h1>
        <p>아래 버튼을 클릭하여 로그인을 테스트하세요</p>
        
        <a href="/users/auth/kakao/login/" class="button kakao">
            카카오 로그인 테스트
        </a>
        
        <a href="/users/auth/google/login/" class="button google">
            구글 로그인 테스트
        </a>
    </body>
    </html>
    """
    return HttpResponse(html)