# serializers.py는 API 통신에서 데이터 포맷을 바꿔주는 중간 다리 역할입니다.
# 요청/응답 데이터 직렬화 ex) JSON <-> Python Object
# 데이터 변환기 역할 
# Python 객체 ↔ JSON 변환
# 클라이언트가 보낸 데이터 검증
# DB 데이터를 API 응답용으로 가공

# Django REST Framework에서 제공하는 serializers 가져오기 
from rest_framework import serializers

# User 모델 가져오기 (models.py에 정의된 User 모델)
from .models import User

# 외부 API 호출할 때 사용  / requests 라이브러리
import requests

# DB User 정보를 변환 Serializer 
class UserSerializer(serializers.ModelSerializer):
    """ DB User 모델 기반 로그인 성공 후, 클라이언트에 반환할 사용자 정보 """
    class Meta: # 메타 정보 설정 
        model = User # User 모델 사용 
        fields = ['id', 'social_id', 'provider', 'username', 'profile_image']  # 클라이언트에 보내줄 정보

# 소셜 로그인 검증용 시리얼라이저
class SocialLoginSerializer(serializers.Serializer):
    """ 클라이언트에서 보내는 소셜 로그인 정보 검증용"""
    provider = serializers.ChoiceField(
        choices=['kakao', 'google'], # 카카오인지 구글인지 둘 중 하나인지 검증하는 역할
        required=True # 위에 choices 중 하나의 값이 필수로 입력돼서 와야된다는 뜻. 안오면 에러 발생
    )

    # 액세스 토큰은 보안이 필요한 정보임
    # 클라이언트에 그대로 보내버리면 누군가 토큰을 탈취해서 다른 계정으로 로그인 할 수 있음
    access_token = serializers.CharField(
        required=True, # 필수 입력
        write_only=True # 서버에서만 사용, 응답으로 보내지 않음 why? -> 보안상 이유
    )


# 처리 흐름 
# 1. POST /auth/social-login/ 요청 받음
#   ↓
# 2. provider, access_token 검증 (Serializer)
#   ↓
# 3. Kakao/Google API 호출
#   ↓
# 4. 사용자 정보 추출 (social_id, username, profile_image)
#   ↓
# 5. 닉네임 중복 체크 → 중복 시 숫자 추가
#   ↓
# 6. DB에 사용자 저장 (get_or_create)
#   ↓
# 7. 사용자 정보 JSON으로 반환