from django.contrib import admin
from .models import Accessibility, ModificationRequest

@admin.register(Accessibility)
class AccessibilityAdmin(admin.ModelAdmin):
    # 목록에 보여질 필드들
    list_display = ('building_name', 'id', 'latitude', 'longitude')
    # 검색창 추가 (건물명, ID로 검색 가능)
    search_fields = ('building_name', 'id')
    # 필터 추가 (접근성 여부로 필터링)
    list_filter = ('has_ramp', 'wheelchair', 'has_elevator', 'accessible_toilet')

@admin.register(ModificationRequest)
class ModificationRequestAdmin(admin.ModelAdmin):
    list_display = ('place', 'user', 'status', 'created_at', 'wheelchair', 'has_elevator')
    list_filter = ('status', 'place', 'user') # 장소별, 사용자별, 상태별 필터링
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description='선택한 요청 승인 및 데이터 반영')
    def approve_requests(self, request, queryset):
        for req in queryset:
            if req.status != 'pending':
                continue
            
            # 실제 장소 데이터 업데이트
            place = req.place
            place.wheelchair = req.wheelchair
            place.has_elevator = req.has_elevator
            place.has_ramp = req.has_ramp
            place.accessible_toilet = req.accessible_toilet
            place.save()

            # 요청 상태 변경
            req.status = 'approved'
            req.save()
        self.message_user(request, "선택한 요청이 승인되고 데이터가 업데이트되었습니다.")

    @admin.action(description='선택한 요청 거절')
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')