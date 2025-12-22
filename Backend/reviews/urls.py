from django.urls import path, include

# Django REST Framework의 Router 클래스
# ViewSet을 자동으로 URL 패턴으로 변환해주는 도구
from rest_framework.routers import DefaultRouter 

from .views import ReviewViewSet, ReviewListAPI, ReviewLikeView

router = DefaultRouter()
router.register(r'', ReviewViewSet, basename='review')
app_name = 'reviews'

urlpatterns = [
    # 프론트에서 이 경로로 요청을 보냄
    path('<int:pk>/like/', ReviewLikeView.as_view(), name='review-like'),
    path('', include(router.urls)),
    path('', ReviewListAPI.as_view(), name='review-list'),
]