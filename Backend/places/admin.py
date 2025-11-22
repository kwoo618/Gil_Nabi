from django.contrib import admin
from .models import Accessibility

@admin.register(Accessibility)
class AccessibilityAdmin(admin.ModelAdmin):
    # 목록에 보여질 필드들
    list_display = ('building_name', 'id', 'latitude', 'longitude')
    # 검색창 추가 (건물명, ID로 검색 가능)
    search_fields = ('building_name', 'id')
    # 필터 추가 (접근성 여부로 필터링)
    list_filter = ('has_ramp', 'wheelchair', 'has_elevator', 'accessible_toilet')