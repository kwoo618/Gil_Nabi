from django.urls import path
from .views import AccessibilityListAPI # 새로 만든 API 뷰를 불러옵니다.

urlpatterns = [
    # GET /api/places/ 로 요청하면 모든 장소 목록을 JSON으로 보여줍니다.
    path('', AccessibilityListAPI.as_view(), name='place-list-api'),
]