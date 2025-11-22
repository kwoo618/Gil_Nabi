from django.urls import path, include

# Django REST Framework의 Router 클래스
# ViewSet을 자동으로 URL 패턴으로 변환해주는 도구
from rest_framework.routers import DefaultRouter 

from .views import ReviewViewSet
from .views import ReviewListAPI

router = DefaultRouter()
router.register(r'', ReviewViewSet, basename='review')
app_name = 'reviews'

urlpatterns = [
    # router가 생성한 모든 URL 패턴을 포함
    # router.urls가 자동으로 생성하는 URL:
    #   GET    /api/reviews/              -> list (목록 조회)
    #   POST   /api/reviews/              -> create (생성)
    #   GET    /api/reviews/{id}/         -> retrieve (상세 조회)
    #   PUT    /api/reviews/{id}/         -> update (전체 수정)
    #   PATCH  /api/reviews/{id}/         -> partial_update (부분 수정)
    #   DELETE /api/reviews/{id}/         -> destroy (삭제)
    #   GET    /api/reviews/my_reviews/   -> my_reviews (커스텀 액션)
    path('', include(router.urls)),
    path('', ReviewListAPI.as_view(), name='review-list'),
]