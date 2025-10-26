# Django admin에서 user관리 # 관리자 페이지(Admin Site)
# admin.py는 각 앱의 모델을 관리자 페이지에 등록해서
# 웹 브라우저로 쉽게 데이터를 관리할 수 있게 하는 파일

from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'username', 'nickname', 'provider', 
        'disability_type', 'has_wheelchair', 'is_profile_complete'
    ]
    list_filter = ['provider', 'disability_type', 'is_profile_complete']
    search_fields = ['username', 'nickname', 'social_id']