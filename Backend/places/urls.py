from django.urls import path
from .views import (
    AccessibilityListAPI, 
    AccessibilityDetailAPI,
    RecommendPlacesAPI,
    AIRecommendationAPI,
    AccessibilityFilterAPI
)
urlpatterns = [
    # GET /api/places/ 로 요청하면 모든 장소 목록을 JSON으로 보여줍니다.
    path('', AccessibilityListAPI.as_view(), name='place-list-api'),
    path('<str:id>/', AccessibilityDetailAPI.as_view(), name='place-detail-api'),
    path('recommend/', RecommendPlacesAPI.as_view(), name='recommend-places'),  # 추가
    path('ai-recommend/', AIRecommendationAPI.as_view(), name='ai-recommend'),
    path('filter/', AccessibilityFilterAPI.as_view(), name='accessibility-filter'),
]