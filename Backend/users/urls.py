#users 관련 API 관리
#urls.py는 URL로 들어오면 이 view가 처리한다 라는 지도를 그리는 파일입니다.
# URL 라우팅

# 역할
# URL과 View를 연결하는 지도
# 클라이언트가 어떤 URL로 요청하면 어떤 View가 처리할지 정의

from django.urls import path
from .views import SocialLoginView

urlpatterns = [
    path('auth/social-login/', SocialLoginView.as_view(), name='social-login'),
]