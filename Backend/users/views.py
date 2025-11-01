# 요청 처리 (API 구현)
# 실제 동작/로직이 구현되는 파일
# KaKao, Naver 소셜 로그인 API 호출 및 응답 처리

# Django REST Framework에서 APIView와 응답 도구 가져오기 
from rest_framework.views import APIView # API 요청 처리용 클래스 
from rest_framework.response import Response # API 응답용 클래스 (JSON 응답 생성)
from rest_framework import status # HTTP 상태 코드
from django.shortcuts import redirect
from django.http import JsonResponse

from dotenv import load_dotenv # .env로 비밀번호 넣고 호출해오는 기능 
import os


# 시리얼라이저 가져오기 
from .serializers import SocialLoginSerializer, UserSerializer
from .models import User # User 모델 가져오기
import requests # 파이썬에서 다른 서버 API에 HTTP 요청 보낼 때 사용 (ex. 파이썬용 브라우저)

load_dotenv()

# 로그인 API 클래스
class SocialLoginView(APIView):
    # APIView 상속 -> POST, GET 같은 HTTP 요청 처리 가능
    # 클래스 내부에서 POST 메서드 정의 -> 로그인 요청 처리
    """ KaKao or Google 액세스 토큰으로 로그인 처리 """ 

    # post 메서드 정의 
    def post(self, request):
        # 클라이언트에서 보낸 데이터 가져오기
        serializer = SocialLoginSerializer(data=request.data) # 요청 데이터로 시리얼라이저 객체 생성
        serializer.is_valid(raise_exception=True) # 데이터 검증, 틀리면 자동 에러 반환 #.is_valid() -> True/False 반환
        provider = serializer.validated_data['provider'] # kakao or google #
        access_token = serializer.validated_data['access_token'] # 소셜 로그인 토큰

        # 소셜 API 호출 
        # KaKao API 호출
        if provider == 'kakao':
            user_info = requests.get(
                'https://kapi.kakao.com/v2/user/me', # KaKao 사용자 정보 API URL
                headers={'Authorization': f'Bearer {access_token}'} # 요청 헤더에 토큰 정보를 담음
            ).json() # 요청을 JSON으로 변환해서 파이썬 딕셔너리로 사용 가능.
            social_id = str(user_info['id']) # 카카오 고유 ID
            username = user_info.get('kakao_account', {}).get('profile', {}).get('nickname', 'KaKaoUser') # 닉네임, 없으면 기본값 "KaKaoUser"
            profile_image = user_info.get('kakao_account', {}).get('profile', {}).get('profile_image_url') # 프로필 이미지 URL

        # Google API 호출
        elif provider == 'google':
            user_info = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            ).json() # JSON 응답
            social_id = user_info.get('id') # 구글 고유 ID
            username = user_info.get('name', 'GoogleUser') # 닉네임, 없으면 기본값 "GoogleUser"
            profile_image = user_info.get('picture') # 프로필 이미지 URL

        # DB에 사용자 정보 저장 (없으면 새로 생성)
            # DB에 이미 있는 사용자 조회 
        user, created = User.objects.get_or_create(
            social_id=social_id,    # 검색 조건 (이미 있으면 조회)
            provider=provider,      # 카카오 or 구글
            defaults={'username': username, 'profile_image': profile_image} # 없으면 생성
        )
        
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': '로그인 성공',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token), # 액세스 토큰
                'refresh': str(refresh), # 리프레쉬 토큰
            }
        }, status = status.HTTP_200_OK)
    
    def get(self, request):
        code = request.GET.get('code')
        provider = request.GET.get('state', 'kakao') # 카카오 or 구글

        # 에러처리
        if not code:
            return Response(
                {'error': '인가 코드가 없음'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        # 카카오 로그인일 경우 
        if provider == 'kakao':
            token_response = requests.post(  
                'https://kauth.kakao.com/oauth/token',  
                data={  # !!! 배포할때는 키값들 env로 변경해서 호출 !!!
                    'grant_type': 'authorization_code',
                    'client_id': os.getenv('KAKAO_CLIENT_ID'),  # 카카오 REST API
                    'redirect_uri': 'http://localhost:8000/users/auth/login/',  # 카카오 리다이렉트 URI
                    'code': code,
                }
            )

            token_json = token_response.json()

            # 에러처리 
            if 'error' in token_json:
                return Response(  
                    {'error': '토큰 발급 실패', 'detail': token_json, 'code_received': code},  
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            access_token = token_json['access_token']

            # 액세스 토큰으로 사용자 정보 가져오기 
            user_info = requests.get(  
                'https://kapi.kakao.com/v2/user/me',
                headers={'Authorization': f'Bearer {access_token}'}
            ).json()

            social_id = str(user_info['id'])
            username = user_info.get('kakao_account', {}).get('profile', {}).get('nickname', 'KakaoUser')
            profile_image = user_info.get('kakao_account', {}).get('profile', {}).get('profile_image_url')

        elif provider == 'google':  
            token_response = requests.post(  
                'https://oauth2.googleapis.com/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': os.getenv('GOOGLE_CLIENT_ID'),  # 구글 클라이언트 ID로 교체
                    'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),  # 구글 클라이언트 시크릿으로 교체
                    'redirect_uri': 'http://localhost:8000/users/auth/login/',  # 리다이렉트 URI
                    'code': code,
                }
            )
            token_json = token_response.json()
        
            if 'error' in token_json:
                return Response(
                    {'error': '구글 토큰 발급 실패', 'detail': token_json}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
            access_token = token_json['access_token']  
        
            # 2. 액세스 토큰으로 사용자 정보 가져오기
            user_info = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            ).json()
        
            social_id = user_info.get('id')
            username = user_info.get('name', 'GoogleUser')
            profile_image = user_info.get('picture')

        else:
            return Response(
                {'error': '지원하지 않는 provider입니다'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 사용자 생성 또는 조회
        user, created = User.objects.get_or_create(
            social_id=social_id,
            provider=provider,
            defaults={'username': username, 'profile_image': profile_image}
        )
        
        # 응답 방식 선택
        # 옵션 1: 프론트엔드로 리다이렉트 (React 등 사용 시)
        return redirect(f'/signup.html?user_id={user.id}')

class CompleteProfileView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        nickname = request.data.get('nickname')
        disability_type = request.data.get('disability_type')
        has_wheelchair = request.data.get('has_wheelchair')
        
        # 닉네임 중복 체크
        if User.objects.filter(nickname=nickname).exists():
            return Response({
                'error': '닉네임이 중복입니다',
                'message': '다른 닉네임을 입력해주세요'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            user.nickname = nickname
            user.disability_type = disability_type
            user.has_wheelchair = has_wheelchair
            user.is_profile_complete = True
            user.save()
            
            return Response({
                'message': '프로필 완성 성공',
                'user_id': user_id
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': '사용자를 찾을 수 없습니다'
            }, status=status.HTTP_404_NOT_FOUND)

class HomeView(APIView):
    def get(self, request):
        return Response ({
            'message': '로그인 API 서버',
            'endpoints' : {
                'kakao_login': '/users/auth/login/?provider=kakao',
                'google_login': '/users/auth/login/?provider=google',
                'complete_profile': '/users/auth/login/signup/'
            }
        })