from django.contrib import admin
from django.urls import path, include # import : Django에서 URL을 관리할 때 사용하는 함수
from django.conf import settings  # html 테스트
from django.conf.urls.static import static  # html 테스트
from django.views.generic import TemplateView
from places.views import show_map, test_page

urlpatterns = [
    path('admin/', admin.site.urls),

    # API 
    path('users/', include('users.urls')),  # Users 앱의 URL 포함
    path('api/reviews/', include('reviews.urls')),
    path('api/places/', include('places.urls')),
    path('api/', include('community.urls')),

    path('test/', test_page),  # 직접 연결



    # 테스트용 프론트엔드 
    # path('admin-page/', TemplateView.as_view(template_name='admin.html'), name='admin_page'), 관리자 페이지 추후 추가 예정
    path('', TemplateView.as_view(template_name='login.html'), name='home'),  
    path('login/', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup_page'), 
    path('map/', show_map, name='show-map'),
    path('reviews/', TemplateView.as_view(template_name='reviews.html'), name='review_page'),
    path('community/', TemplateView.as_view(template_name='community.html'), name='community_page'),

    path('map/', show_map, name='map'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])