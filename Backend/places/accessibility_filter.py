# places/accessibility_filter.py
from .models import Accessibility

class AccessibilityFilter:
    """접근성 필터링 + 검색"""
    
    def get_queryset(self, filters, map_bounds=None, search_query=None):
        """공통 필터링 로직 (QuerySet 반환)"""
        queryset = Accessibility.objects.all()
        
        # 1. 지도 범위
        if map_bounds:
            queryset = queryset.filter(
                latitude__gte=map_bounds.get('south', 35.88),
                latitude__lte=map_bounds.get('north', 35.91),
                longitude__gte=map_bounds.get('west', 128.84),
                longitude__lte=map_bounds.get('east', 128.87)
            )
        
        # 2. 접근성 필터 (AND 조건)
        if filters.get('wheelchair'):
            queryset = queryset.filter(wheelchair=True)
        if filters.get('has_elevator'):
            queryset = queryset.filter(has_elevator=True)
        if filters.get('has_ramp'):
            queryset = queryset.filter(has_ramp=True)
        if filters.get('accessible_toilet'):
            queryset = queryset.filter(accessible_toilet=True)
        
        # 3. 검색어 필터
        if search_query and search_query.strip():
            queryset = queryset.filter(building_name__icontains=search_query.strip())
        
        return queryset

    def get_filtered_places_with_details(self, filters, map_bounds=None, search_query=None):
        """필터링 + 검색 결과 포맷팅"""
        
        queryset = self.get_queryset(filters, map_bounds, search_query)
        
        # 결과 생성
        filtered = []
        for place in queryset:
            matches = []
            if place.wheelchair: matches.append('휠체어')
            if place.has_elevator: matches.append('엘리베이터')
            if place.has_ramp: matches.append('경사로')
            if place.accessible_toilet: matches.append('화장실')
            
            filtered.append({
                'id': str(place.id),
                'place_id': str(place.id),
                'building_name': place.building_name,
                'location': {
                    'latitude': float(place.latitude),
                    'longitude': float(place.longitude)
                },
                'matching_filters': matches,
                'accessibility': {
                    'wheelchair': place.wheelchair,
                    'has_elevator': place.has_elevator,
                    'has_ramp': place.has_ramp,
                    'accessible_toilet': place.accessible_toilet
                }
            })
        
        return filtered