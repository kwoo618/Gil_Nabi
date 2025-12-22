# users/admin.py
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 기본 목록 표시
    list_display = [
        'id', 'username', 'nickname', 'provider', 
        'disability_type', 'has_wheelchair', 'is_profile_complete'
    ]
    
    # 필터
    list_filter = ['provider', 'disability_type', 'is_profile_complete']
    
    # 검색
    search_fields = ['username', 'nickname', 'social_id']
    
    # 페이지당 표시 개수
    list_per_page = 20
    
    # 삭제 기능 활성화 (기본으로 활성화되어 있음)
    actions = ['delete_selected']