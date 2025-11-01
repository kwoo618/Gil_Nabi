# 관리자 페이지(Admin Site)

from django.contrib import admin  # 관리자 페이지 기능 
from .models import Review # Review/models에서 Review 모델

@admin.register(Review) # Review 모델을 관리자 페이지에 등록함 
class ReviewAdmin(admin.ModelAdmin):
    # 관리자 페이지에서 리뷰 어떻게 관리할지 정의 
    list_display = ['id', 'user', 'rating', 'disability_type', 'created_at'] # 목록 페이지
    list_filter = ['rating', 'disability_type', 'created_at'] # 필터 옵션 
    search_fields = ['user__username', 'content'] # 검색 기능, __ : user 테이블의 username 필드를 검색 
    readonly_fields=['created_at', 'updated_at'] # 읽기 전용 필드 (관리자도 수정 못함)
    fieldsets = ( # 상세 페이지에서 필드 그룹화
        ('기본 정보', {  # 첫 번째 그룹: 기본 정보
            'fields': ('user', 'rating', 'disability_type')
        }),
        ('리뷰 내용', {  # 두 번째 그룹: 리뷰 내용
            'fields': ('content',)
        }),
        ('날짜 정보', {  # 세 번째 그룹: 날짜 정보 ✅ 추가!
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # 기본적으로 접혀있음 (펼쳐서 볼 수 있음)
        }),
    )
