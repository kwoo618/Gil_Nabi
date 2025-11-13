from django.db.models import Q
from places.models import Accessibility

class AccessibilityFilter:
    """
    접근성 기반 필터링 시스템
    체크된 항목은 반드시 True여야 함
    체크 안 된 항목은 상관없음 (True/False/None 모두 가능)
    """
    
    def filter_places(self, filters, map_bounds=None):
        """
        필터 조건에 맞는 장소 반환
        
        Args:
            filters: {
                'has_ramp': bool or None,
                'wheelchair': bool or None,
                'accessible_toilet': bool or None,
                'has_elevator': bool or None
            }
            map_bounds: 지도 범위 (선택)
        """
        queryset = Accessibility.objects.all()
        
        # 1. 지도 범위 필터링
        if map_bounds:
            queryset = queryset.filter(
                latitude__gte=map_bounds['south'],
                latitude__lte=map_bounds['north'],
                longitude__gte=map_bounds['west'],
                longitude__lte=map_bounds['east']
            )
        
        # 2. 접근성 필터링 (체크된 항목만)
        filter_conditions = Q()
        
        if filters.get('has_ramp') == True:
            filter_conditions &= Q(has_ramp=True)
            
        if filters.get('wheelchair') == True:
            filter_conditions &= Q(wheelchair=True)
            
        if filters.get('accessible_toilet') == True:
            filter_conditions &= Q(accessible_toilet=True)
            
        if filters.get('has_elevator') == True:
            filter_conditions &= Q(has_elevator=True)
        
        # 필터 적용
        if filter_conditions:
            queryset = queryset.filter(filter_conditions)
        
        return queryset
    
    def get_filtered_places_with_details(self, filters, map_bounds=None):
        """
        필터링된 장소와 상세 정보 반환
        """
        places = self.filter_places(filters, map_bounds)
        
        result = []
        for place in places:
            result.append({
                'place_id': place.id,
                'building_name': place.building_name,
                'location': {
                    'latitude': place.latitude,
                    'longitude': place.longitude
                },
                'accessibility': {
                    'has_ramp': place.has_ramp,
                    'wheelchair': place.wheelchair,
                    'accessible_toilet': place.accessible_toilet,
                    'has_elevator': place.has_elevator
                },
                'matching_filters': self._get_matching_filters(place, filters)
            })
        
        return result
    
    def _get_matching_filters(self, place, filters):
        """체크된 필터 중 매칭되는 항목 반환"""
        matches = []
        
        if filters.get('has_ramp') and place.has_ramp:
            matches.append('경사로')
        if filters.get('wheelchair') and place.wheelchair:
            matches.append('휠체어 접근')
        if filters.get('accessible_toilet') and place.accessible_toilet:
            matches.append('장애인 화장실')
        if filters.get('has_elevator') and place.has_elevator:
            matches.append('엘리베이터')
        
        return matches