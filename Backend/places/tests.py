from django.test import TestCase
from .models import Accessibility
from .accessibility_filter import AccessibilityFilter

class AccessibilityFilterTestCase(TestCase):
    def setUp(self):
        # 테스트용 데이터 생성
        # 1. 모든 조건 만족 (범위 내, 모든 시설 O)
        Accessibility.objects.create(
            id="1",
            building_name="완벽한 건물",
            latitude=35.90, longitude=128.85,
            wheelchair=True, has_elevator=True, has_ramp=True, accessible_toilet=True
        )
        # 2. 범위 밖 (좌표가 멀리 떨어짐)
        Accessibility.objects.create(
            id="2",
            building_name="멀리 있는 건물",
            latitude=37.00, longitude=129.00,
            wheelchair=True, has_elevator=True, has_ramp=True, accessible_toilet=True
        )
        # 3. 범위 내, 휠체어만 없음
        Accessibility.objects.create(
            id="3",
            building_name="계단만 있는 건물",
            latitude=35.90, longitude=128.85,
            wheelchair=False, has_elevator=True, has_ramp=True, accessible_toilet=True
        )
        
        self.filter_system = AccessibilityFilter()
        # 테스트용 지도 범위 (대구대 근처)
        self.map_bounds = {
            'south': 35.88, 'north': 35.91,
            'west': 128.84, 'east': 128.87
        }

    def test_filter_by_bounds(self):
        """지도 범위 필터링 테스트"""
        # 필터 없이 범위만 적용
        result = self.filter_system.get_filtered_places_with_details(
            filters={}, map_bounds=self.map_bounds
        )
        # "멀리 있는 건물"은 제외되어야 함 (총 2개: 완벽한 건물, 계단만 있는 건물)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['building_name'], "완벽한 건물")

    def test_filter_by_accessibility(self):
        """접근성 필터(AND 조건) 테스트"""
        filters = {'wheelchair': True}
        
        result = self.filter_system.get_filtered_places_with_details(
            filters=filters, map_bounds=self.map_bounds
        )
        
        # "계단만 있는 건물"(wheelchair=False)은 제외되어야 함
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['building_name'], "완벽한 건물")

    def test_filter_by_search_query(self):
        """검색어 필터링 테스트"""
        result = self.filter_system.get_filtered_places_with_details(
            filters={}, map_bounds=self.map_bounds, search_query="계단"
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['building_name'], "계단만 있는 건물")

    def test_result_structure(self):
        """반환 데이터 구조 확인"""
        result = self.filter_system.get_filtered_places_with_details(
            filters={}, map_bounds=self.map_bounds
        )
        
        place = result[0]
        # 필수 키들이 존재하는지 확인
        self.assertIn('id', place)
        self.assertIn('building_name', place)
        self.assertIn('location', place)
        self.assertIn('accessibility', place)
        # location 안에 lat/lng이 있는지 확인
        self.assertIn('latitude', place['location'])
        self.assertIn('longitude', place['location'])