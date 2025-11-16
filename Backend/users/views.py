# 요청 처리 (API 구현)
# 실제 동작/로직이 구현되는 파일
# KaKao, Google 소셜 로그인 API 호출 및 응답 처리

# Django REST Framework에서 APIView와 응답 도구 가져오기 
from rest_framework.views import APIView                    # API 요청 처리용 클래스 
from rest_framework.response import Response                # API 응답용 클래스 (JSON 응답 생성)
from rest_framework import status                           # HTTP 상태 코드
from rest_framework_simplejwt.tokens import RefreshToken    # JWT 설정 
from django.core.cache import cache                         # redis 설정 
from rest_framework.permissions import AllowAny, IsAuthenticated # 접근 권한 
from django.shortcuts import redirect
from django.http import JsonResponse
from dotenv import load_dotenv                              # .env로 비밀번호 넣고 호출해오는 기능 
import os
import requests                                             # 파이썬에서 다른 서버 API에 HTTP 요청 보낼 때 사용 (ex. 파이썬용 브라우저)


# 시리얼라이저 가져오기 
from .serializers import SocialLoginSerializer, UserSerializer
from .models import User                                    # User 모델 가져오기

load_dotenv()

# 로그인 API 클래스
class SocialLoginView(APIView):
    # APIView 상속 -> POST, GET 같은 HTTP 요청 처리 가능
    permission_classes = [AllowAny] # 로그인은 인증없이 접근 가능

    # post 메서드 정의 
    def post(self, request):
        # 클라이언트에서 보낸 데이터 가져오기
        serializer = SocialLoginSerializer(data=request.data)       # 요청 데이터로 시리얼라이저 객체 생성
        serializer.is_valid(raise_exception=True)                   # 데이터 검증, 틀리면 자동 에러 반환 #.is_valid() -> True/False 반환
        provider = serializer.validated_data['provider']            # kakao or google #
        access_token = serializer.validated_data['access_token']    # 소셜 로그인 토큰

        # 소셜 API 호출 
        # KaKao API 호출
        if provider == 'kakao':
            user_info = requests.get(
                'https://kapi.kakao.com/v2/user/me',                # KaKao 사용자 정보 API URL
                headers={'Authorization': f'Bearer {access_token}'} # 요청 헤더에 토큰 정보를 담음
            ).json()                                                # 요청을 JSON으로 변환해서 파이썬 딕셔너리로 사용 가능.
            social_id = str(user_info['id'])                        # 카카오 고유 ID
            username = user_info.get('kakao_account', {}).get('profile', {}).get('nickname', 'KaKaoUser')   # 닉네임, 없으면 기본값 "KaKaoUser"
            profile_image = user_info.get('kakao_account', {}).get('profile', {}).get('profile_image_url')  # 프로필 이미지 URL

        # Google API 호출
        elif provider == 'google':
            user_info = requests.get(
                f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={access_token}'
            ).json()

            if 'error' in user_info or not user_info.get('sub'):
                return Response({
                    'error': 'Google ID 토큰이 유효하지 않습니다.',
                    'detail': user_info
                }, status=status.HTTP_400_BAD_REQUEST)

            social_id = user_info.get('sub')

            username = user_info.get('name', 'GoogleUser')
            profile_image = user_info.get('picture')
        # DB에 사용자 정보 저장 (없으면 새로 생성)
            # DB에 이미 있는 사용자 조회 
        user, created = User.objects.get_or_create(
            social_id=social_id,                                    # 검색 조건 (이미 있으면 조회)
            provider=provider,                                      # 카카오 or 구글
            defaults={'username': username, 'profile_image': profile_image} # 없으면 생성
        )

         # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh) 

        # Refresh Token을 Redis에 저장 (7일 만료)
        cache.set(
            f'refresh_token:{user.id}',
            refresh_token,
            timeout=60*60*24*7  # 7일
        )

        return Response({
            'message': '로그인 성공',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': access_token,             # 액세스 토큰
                'refresh': refresh_token,           # 리프레쉬 토큰
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
                    'client_id': os.getenv('KAKAO_RESTAPI_KEY'),  # 카카오 REST API
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

            if 'error' in user_info:
                return Response({
                    'error': 'Google 사용자 정보 조회에 실패했습니다.',
                    'detail': user_info
                }, status=status.HTTP_400_BAD_REQUEST)
        
            social_id = user_info.get('sub') or user_info.get('id')

            if not social_id: 
                return Response({
                    'error': 'Google 응답에서 social_id를 찾을 수 없습니다.', 
                    'detail': user_info 
                }, status=status.HTTP_400_BAD_REQUEST)

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

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Redis에 저장
        cache.set(
            f'refresh_token:{user.id}',
            refresh_token,
            timeout=60*60*24*7
        )
        # 이미 가입했으면 맵 뷰로 바로 이동 
        if user.is_profile_complete:
            return redirect(f'/map/?access_token={access_token}&refresh_token={refresh_token}&user_id={user.id}')
        else :   # 아니면 회원가입 
            return redirect(f'/signup/?access_token={access_token}&refresh_token={refresh_token}&user_id={user.id}')

class CompleteProfileView(APIView):
    permission_classes = [AllowAny] # 로그인 전이라 접근 가능.

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

            # 회원가입 이후 자동 로그인이 안되는 현상이 발생하여 토큰 추가 
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            cache.set(
                f'refresh_token:{user.id}',
                refresh_token,
                timeout=60*60*24*7  # 7일
            )
        
            return Response({
                'message': '회원가입이 완료되었습니다',
                'access_token': str(refresh.access_token),  
                'refresh_token': str(refresh),  
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.nickname,
                    'disability_type': user.disability_type
                }
            })
            
            
        except User.DoesNotExist:
            return Response({
                'error': '사용자를 찾을 수 없습니다'
            }, status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated] # 로그인 된 사용자만 접근 가능
    def post(self, request):
        try:
            # Redis에서 Refresh Token 삭제
            cache.delete(f'refresh_token:{request.user.id}')
            
            return Response({
                'message': '로그아웃 성공'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': '로그아웃 실패',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    # 액세스 토큰 갱신 
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:       # 토큰이 없을때
            return Response({
                'error': 'Refresh Token이 필요합니다'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Refresh Token 검증
            refresh = RefreshToken(refresh_token)
            user_id = refresh['user_id']
            
            # Redis에서 저장된 토큰과 비교
            stored_token = cache.get(f'refresh_token:{user_id}')
            
            if stored_token != refresh_token:
                return Response({
                    'error': '유효하지 않은 Refresh Token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 새 Access Token 발급
            new_access_token = str(refresh.access_token)
            
            return Response({
                'access': new_access_token
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Token 갱신 실패',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.nickname,
            'nickname': user.nickname,
            'profile_image': user.profile_image,
            'disability_type': user.disability_type,
        })

class HomeView(APIView):
    permission_classes = [AllowAny]     # 홈은 누구나 접근 가능
    def get(self, request):
        return Response ({
            'message': '로그인 API 서버',
            'endpoints' : {
                'kakao_login': '/users/auth/login/?provider=kakao',
                'google_login': '/users/auth/login/?provider=google',
                'complete_profile': '/users/auth/login/signup/',
                'logout': '/users/auth/logout/',
                'token_refresh': '/users/auth/token/refresh/'
            }
        })