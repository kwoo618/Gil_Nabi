from django.urls import path
from .views import AccessibilityListAPI, AccessibilityDetailAPI

urlpatterns = [
    # GET /api/places/ 로 요청하면 모든 장소 목록을 JSON으로 보여줍니다.
    path('', AccessibilityListAPI.as_view(), name='place-list-api'),
    path('<str:id>/', AccessibilityDetailAPI.as_view(), name='place-detail-api'),
]