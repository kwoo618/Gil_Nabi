from django.contrib import admin
from django.views.generic import TemplateView # 테스트용
from django.urls import path, include # import : Django에서 URL을 관리할 때 사용하는 함수

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # users 앱의 URL 포함
    path('', TemplateView.as_view(template_name='test.html')), # 테스트용
    
]
