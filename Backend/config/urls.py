from django.contrib import admin
from places.views import show_map
from django.urls import path, include # import : Django에서 URL을 관리할 때 사용하는 함수
from django.conf import settings  # html 테스트
from django.conf.urls.static import static  # html 테스트
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # Users 앱의 URL 포함
    path('api/reviews/', include('reviews.urls')), # Reviews 앱의 URL 포함
    path('api/places/', include('places.urls')),
    path('', show_map, name='show-map'),
    path('', TemplateView.as_view(template_name='login.html'), name='home'),   
    path('reviews.html', TemplateView.as_view(template_name='reviews.html'), name='review_page'),
    path('login.html', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('signup.html', TemplateView.as_view(template_name='signup.html'), name='signup_page'),
    path('success.html', TemplateView.as_view(template_name='success.html'), name='success_page'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])