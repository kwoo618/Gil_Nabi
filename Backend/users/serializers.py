# serializers.py는 API 통신에서 데이터 포맷을 바꿔주는 중간 다리 역할입니다.
# 요청/응답 데이터 직렬화 ex) JSON <-> Python Object

# Django REST Framework에서 제공하는 serializers 가져오기 
from rest_framework import serializers

# User 모델 가져오기
from .models import User

# 외부 API 호출할 때 사용
import requests

# DB User 정보를 변환/검증용 Serializer 정의
class UserSerializer(serializers.ModelSerializer):
    """ DB User 모델 기반 로그인 성공 후, 클라이언트에 반환할 사용자 정보 """
    class Meta:
        model = User # User 모델 사용
        fields = ['id', 'social_id', 'provider', 'username', 'profile_image']  # 클라이언트에 보내줄 정보

# 소셜 로그인용 토큰 시리얼라이저 
class SocialLoginSerializer(serializers.Serializer):
    """ 클라이언트에서 보내는 소셜 로그인 정보 검증용"""
    provider = serializers.ChoiceField(
        choices=['kakao', 'naver'], # 허용되는 소셜 로그인 제공자
        required=True # 필수 입력
    )

    # 액세스 토큰은 보안이 필요한 정보임
    # 클라이언트에 그대로 보내버리면 누군가 토큰을 탈취해서 다른 계정으로 로그인 할 수 있음
    access_token = serializers.CharField(
        required=True # 필수 입력
        write_only=True # 서버에서만 사용, 응답으로 보내지 않음 why? -> 보안상 이유
    )