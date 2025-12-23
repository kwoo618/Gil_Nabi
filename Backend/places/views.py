# places/views.py

import os
import requests 
import traceback
from dotenv import load_dotenv

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.postgres.search import TrigramSimilarity

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend

# 모델 및 시리얼라이저
from .models import Accessibility
from .serializers import AccessibilitySerializer, AIRecommendationSerializer

# 추천 및 필터 시스템
from .ai_recommendation import AIRecommendationSystem
from .accessibility_filter import AccessibilityFilter
from .utils import get_kakao_building_name

load_dotenv()

# ============ 페이지 렌더링 ============

def test_page(request):
    """테스트 페이지"""
    kakao_key = os.getenv('KAKAO_MAP_KEY')
    return render(request, 'map.html', {'kakao_map_key': kakao_key})


# ============ 장소 CRUD API ============

@method_decorator(csrf_exempt, name='dispatch')
class PlaceListCreate(ListCreateAPIView):
    """
    장소 목록 조회 및 생성 
    1. 조회: 검색 기능 포함 (Trigram Similarity)
    2. 생성: 카카오 API를 통해 좌표로 건물 이름 자동 찾기 기능 포함
    """
    serializer_class = AccessibilitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']
    permission_classes = [AllowAny] 

    def get_queryset(self):
        queryset = Accessibility.objects.all()
        
        # 1. ID로 정확한 검색
        place_id = self.request.query_params.get('id', None)
        if place_id:
            return queryset.filter(id=place_id)
            
        # 2. 이름 검색
        query = self.request.query_params.get('search', None)
        if query:
            try:
                queryset = queryset.annotate(
                    similarity=TrigramSimilarity('building_name', query),
                ).filter(similarity__gt=0.1).order_by('-similarity')
            except:
                queryset = queryset.filter(building_name__icontains=query)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        input_name = data.get('building_name', '')

        # 이름이 없거나 로딩 중이면 카카오 API로 실제 건물 이름 찾기
        if not input_name or "로딩" in input_name or "place" in input_name:
            lat = data.get('latitude')
            lng = data.get('longitude')
            
            if lat and lng:
                found_name = get_kakao_building_name(lat, lng)
                if found_name:
                    data['building_name'] = found_name

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

@method_decorator(csrf_exempt, name='dispatch')
class PlaceRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    """장소 상세 조회, 수정, 삭제"""
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer
    lookup_field = 'id'
    permission_classes = [AllowAny] 
    
    def patch(self, request, *args, **kwargs):
        try:
            place = self.get_object()
            update_fields = ['wheelchair', 'has_elevator', 'has_ramp', 'accessible_toilet']
            for field in update_fields:
                if field in request.data:
                    value = request.data[field]
                    if value is None or value == 'null':
                        setattr(place, field, None)
                    else:
                        if isinstance(value, str):
                            setattr(place, field, value.lower() == 'true')
                        else:
                            setattr(place, field, bool(value))
            place.save()
            serializer = self.get_serializer(place)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ============ 필터 및 검색 유틸리티 ============

class FilterPlacesView(APIView):
    """접근성 필터링 + 검색"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            filters = request.data.get('filters', {})
            map_bounds = request.data.get('map_bounds', {})
            search_query = request.data.get('search_query', '')
            
            filter_system = AccessibilityFilter()
            filtered_places = filter_system.get_filtered_places_with_details(
                filters=filters,
                map_bounds=map_bounds,
                search_query=search_query
            )
            
            return Response({
                'success': True,
                'markers': filtered_places,
                'count': len(filtered_places)
            })
        except Exception as e:
            print(f"[필터링 오류] {e}")
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class KakaoSearchProxy(APIView):
    """카카오 로컬 API 프록시 (전국 검색용)"""
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('query')
        if not query: return Response({'error': 'No query'}, status=400)
        
        kakao_key = os.getenv('KAKAO_RESTAPI_KEY')
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {kakao_key}"}
        
        try:
            res = requests.get(url, headers=headers, params={"query": query})
            return Response(res.json())
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ============ AI 추천 API ============

class AIRecommendView(APIView):
    """
    AI 장소 추천 API (Clean Version)
    - 중복 로직 제거 완료
    - Android 앱 호환성 데이터 매핑 완료
    - 오타 수정 완료
    """
    permission_classes = [AllowAny] 
    
    def post(self, request):
        try:
            # 1. 데이터 수신
            map_bounds = request.data.get('map_bounds', {})
            if 'filters' not in map_bounds and 'filters' in request.data:
                map_bounds['filters'] = request.data['filters']
            limit = request.data.get('limit', 5)

            # 2. 사용자 정보 처리 (비회원 대응)
            if request.user.is_authenticated:
                user = request.user
            else:
                class MockUser:
                    disability_type = '비회원'
                    has_wheelchair = False
                user = MockUser()
            
            # 3. AI 시스템 호출
            ai_system = AIRecommendationSystem()
            recommendations = ai_system.get_ai_recommendations(user, map_bounds, limit)

            # 4. 데이터 가공 (Serializer 사용)
            # recommendations는 딕셔너리 리스트 형태이므로 many=True로 처리
            serializer = AIRecommendationSerializer(recommendations, many=True)
            data_to_send = serializer.data

            # 5. 성공 응답
            return Response({ 
                "success": True,
                "markers": data_to_send
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"🔥 AI View Error: {e}")
            traceback.print_exc()
            return Response({
                "success": False, 
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)