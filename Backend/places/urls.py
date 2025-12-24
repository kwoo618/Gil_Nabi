from django.urls import path
from .views import KakaoSearchProxy

from . import views

urlpatterns = [
    # 테스트 페이지
    path('test/', views.test_page, name='test'),
    # API
    path('filter/', views.FilterPlacesView.as_view(), name='filter'),
    path('ai-recommend/', views.AIRecommendView.as_view(), name='ai-recommend'),
    path('kakao/search/', KakaoSearchProxy.as_view(), name='kakao-search'),
    path('my-requests/', views.UserModificationRequestList.as_view(), name='my-requests'),
    # CRUD
    path('', views.PlaceListCreate.as_view(), name='place-list'),
    path('<str:id>/', views.PlaceRetrieveUpdateDestroy.as_view(), name='place-detail'),
]
