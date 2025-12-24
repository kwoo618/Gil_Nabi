import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
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
    actions = ['approve_requests', 'reject_requests', 'download_approved_excel']

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

    @admin.action(description='선택한 내역 중 승인된 항목만 엑셀(CSV) 다운로드')
    def download_approved_excel(self, request, queryset):
        """승인된 요청 내역을 CSV 파일로 다운로드 (엑셀 호환)"""
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        filename = f"approved_requests_{timezone.localdate()}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['장소', '사용자', '요청일시', '휠체어', '엘리베이터', '경사로', '화장실'])

        # 선택된 항목 중 승인된 것만 필터링
        approved_queryset = queryset.filter(status='approved')

        for req in approved_queryset:
            writer.writerow([
                req.place.building_name,
                str(req.user) if req.user else '알 수 없음',
                req.created_at.strftime('%Y-%m-%d %H:%M'),
                'O' if req.wheelchair is True else ('X' if req.wheelchair is False else '-'),
                'O' if req.has_elevator is True else ('X' if req.has_elevator is False else '-'),
                'O' if req.has_ramp is True else ('X' if req.has_ramp is False else '-'),
                'O' if req.accessible_toilet is True else ('X' if req.accessible_toilet is False else '-'),
            ])
        
        return response