#users 관련 API 관리
#urls.py는 URL로 들어오면 이 view가 처리한다 라는 지도를 그리는 파일입니다.
# URL 라우팅

# 역할
# URL과 View를 연결하는 지도
# 클라이언트가 어떤 URL로 요청하면 어떤 View가 처리할지 정의

from django.urls import path, include
from .views import SocialLoginView, CompleteProfileView # LoginView : 소셜 로그인 처리 뷰, CompleteProfileView : 프로필 완성 뷰

urlpatterns = [
    path('auth/social-login/', SocialLoginView.as_view(), name='social-login'),
    path('auth/complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),
]