from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from .models import Accessibility
from reviews.models import Review

# User 모델 가져오기
User = get_user_model()

class PlacesAPITest(TestCase):
    """
    장소 관련 API 테스트
    1. 장소 목록 조회 및 생성 (CRUD)
    2. 필터링 기능
    3. AI 추천 시스템 (Mocking 사용)
    """

    def setUp(self):
        """테스트 전 초기 데이터 설정"""
        self.client = APIClient()
        
        # 1. 테스트용 장소 데이터 생성
        self.place1 = Accessibility.objects.create(
            id="111",
            building_name="테스트 카페",
            latitude=35.900,
            longitude=128.850,
            wheelchair=True,
            has_elevator=True,
            has_ramp=True,
            accessible_toilet=True
        )
        self.place2 = Accessibility.objects.create(
            id="222",
            building_name="테스트 식당",
            latitude=35.901,
            longitude=128.851,
            wheelchair=False,
            has_elevator=False,
            has_ramp=False,
            accessible_toilet=False
        )
        
        # 2. 테스트용 유저 생성
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            disability_type="지체장애",
            has_wheelchair=True,
            social_id="test_social_id",  # 임의의 소셜 ID 추가
            provider="kakao"             # 임의의 제공자 추가
        )
        
        # 3. 테스트용 리뷰 생성 (AI 추천 시스템은 리뷰가 있는 장소만 대상으로 함)
        Review.objects.create(
            place=self.place1,
            user=self.user,
            rating=5,
            content="접근성이 좋습니다.",
            disability_type="지체장애"
        )

    def test_get_place_list(self):
        """GET /api/places/ - 장소 목록 조회 테스트"""
        url = reverse('place-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 2) # 최소 2개 이상 있어야 함

    def test_create_place(self):
        """POST /api/places/ - 장소 생성 테스트"""
        url = reverse('place-list')
        data = {
            "id": "333",
            "building_name": "새로운 장소",
            "latitude": 35.902,
            "longitude": 128.852,
            "wheelchair": True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Accessibility.objects.count(), 3) # 2개 -> 3개

    def test_filter_places(self):
        """POST /api/places/filter/ - 필터링 테스트"""
        url = reverse('filter')
        data = {
            "filters": {"wheelchair": True}, # 휠체어 가능한 곳만 필터
            "map_bounds": {
                "north": 36.0, "south": 35.0,
                "east": 129.0, "west": 128.0
            }
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 결과 검증: place1은 포함, place2는 미포함이어야 함
        found_ids = [p['id'] for p in response.data['markers']]
        self.assertIn("111", found_ids)
        self.assertNotIn("222", found_ids)

    @patch('places.ai_recommendation.AIRecommendationSystem._ask_claude')
    def test_ai_recommendation(self, mock_ask_claude):
        """POST /api/places/ai-recommend/ - AI 추천 테스트 (Mocking)"""
        
        # Claude API 호출을 가로채서 가짜 응답을 반환하도록 설정
        mock_ask_claude.return_value = [
            {"id": "111", "score": 95, "reason": "휠체어 접근성이 매우 우수합니다."}
        ]
        
        url = reverse('ai-recommend')
        self.client.force_authenticate(user=self.user) # 로그인 상태 시뮬레이션
        
        data = {
            "map_bounds": {
                "north": 36.0, "south": 35.0,
                "east": 129.0, "west": 128.0
            },
            "filters": {}
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 결과 검증
        markers = response.data['markers']
        self.assertEqual(len(markers), 1)
        self.assertEqual(markers[0]['name'], "테스트 카페")
        self.assertEqual(markers[0]['ai_score'], 95)
        self.assertIn("휠체어 접근 가능", markers[0]['features'])
