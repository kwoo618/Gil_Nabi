# 요청 처리 (API 구현)
# 실제 동작/로직이 구현되는 파일
# KaKao, Naver 소셜 로그인 API 호출 및 응답 처리

# Django REST Framework에서 APIView와 응답 도구 가져오기 
from rest_framework.views import APIView # API 요청 처리용 클래스 
from rest_framework.response import Response # API 응답용 클래스 (JSON 응답 생성)
from rest_framework import status # HTTP 상태 코드

# 시리얼라이저 가져오기 
from .serializers import SocialLoginSerializer, UserSerializer
from .models import User # User 모델 가져오기
import requests # 파이썬에서 다른 서버 API에 HTTP 요청 보낼 때 사용 (ex. 파이썬용 브라우저)

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

        # 닉네임 중복 처리 (DB에 이미 있는 닉네임이면 뒤에 숫자 붙이기)
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1 
        # 사용자 정보 DB 저장


        # DB에 사용자 정보 저장 (없으면 새로 생성)
            # DB에 이미 있는 사용자 조회 
        user, created = User.objects.get_or_create(
            social_id=social_id,    # 검색 조건 (이미 있으면 조회)
            provider=provider,      # 카카오 or 구글
            defaults={'username': username, 'profile_image': profile_image} # 없으면 생성
        )

        # 최종 사용자 정보 반환 
            # 클라이언트에 반환할 시리얼라이징
        data = UserSerializer(user).data # User 객체 -> JSON 변환
        return Response(data, status=status.HTTP_200_OK) # 200 OK 응답

# 요약 흐름
# 1. 클라이언트가 소셜 로그인 토큰과 제공자(kakao/google) 전송
# 2. 서버가 토큰 검증 및 소셜 API 호출로 사용자 정보 조회
# 3. 사용자 정보를 DB에 저장 (없으면 새로 생성)
# 3-1. 닉네임 중복 시 뒤에 숫자 붙여서 고유하게 만듦
# 4. 최종 사용자 정보를 클라이언트에 반환
# 5. 클라이언트는 이 정보를 받아서 앱 내에서 로그인 상태 유지
