import os
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.contrib.postgres.search import TrigramSimilarity

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend

from dotenv import load_dotenv

# 모델 및 시리얼라이저
from .models import Accessibility
from .serializers import AccessibilitySerializer, AIRecommendationSerializer

# 추천 및 필터 시스템
from .ai_recommendation import AIRecommendationSystem
from .accessibility_filter import AccessibilityFilter

load_dotenv()

# ============ 페이지 렌더링 ============

def test_page(request):
    """테스트 페이지"""
    return render(request, 'map.html')

@ensure_csrf_cookie
def show_map(request):
    """지도 페이지 렌더링"""
    places_queryset = Accessibility.objects.all()
    serializer = AccessibilitySerializer(places_queryset, many=True)
    
    kakao_key = os.getenv('KAKAO_MAP_KEY')
    
    context = {
        'places': serializer.data,
        'kakao_map_key': kakao_key
    }
    return render(request, 'map.html', context)


# ============ 기본 CRUD API ============

@method_decorator(csrf_exempt, name='dispatch')
class PlaceListCreate(ListCreateAPIView):
    """장소 목록 조회 및 생성 (검색 기능 포함)"""
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


# ============ 필터 및 AI 추천 API ============

class FilterPlacesView(APIView):
    """접근성 필터링 + 검색"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            filters = request.data.get('filters', {})
            map_bounds = request.data.get('map_bounds', {})
            search_query = request.data.get('search_query', '')
            
            print(f"[필터링] 필터: {filters}")
            print(f"[필터링] 검색어: {search_query}")
            
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


class AIRecommendView(APIView):
    """AI 추천 API"""
    # 여기에 AllowAny를 설정했습니다. 중복된 클래스가 없으므로 이것이 확실히 적용됩니다.
    permission_classes = [AllowAny] 
    
    def post(self, request):
        try:
            map_bounds = request.data.get('map_bounds', {})
            if 'filters' not in map_bounds and 'filters' in request.data:
                map_bounds['filters'] = request.data['filters']

            limit = request.data.get('limit', 5)
            
            # 사용자 정보 처리 (비로그인 대응)
            if request.user.is_authenticated:
                user = request.user
                # User 모델에 해당 필드가 없을 경우를 대비해 getattr 사용
                user_disability = getattr(user, 'disability_type', '미설정')
                has_wheelchair = getattr(user, 'has_wheelchair', False)
            else:
                # 비회원용 임시 user 객체 (AI 로직 에러 방지)
                class MockUser:
                    disability_type = 'none'
                    has_wheelchair = False
                user = MockUser()
                user_disability = '비회원'
                has_wheelchair = False

            ai_system = AIRecommendationSystem()
            recommendations = ai_system.get_ai_recommendations(
                user=user,
                map_bounds=map_bounds,
                limit=limit
            )
            
            # 결과 직렬화
            serializer = AIRecommendationSerializer(recommendations, many=True)
            
            # 프론트엔드 형식에 맞게 변환
            markers = []
            for item in serializer.data:
                place_data = item['place']
                markers.append({
                    'place_id': str(place_data['id']),
                    'building_name': place_data['building_name'],
                    'position': {
                        'lat': place_data['latitude'],
                        'lng': place_data['longitude']
                    },
                    'score': item['ai_score'],
                    'review_count': item['review_count'],
                    'avg_rating': item['avg_rating'],
                    'accessibility': {
                        'wheelchair': place_data['wheelchair'],
                        'has_elevator': place_data['has_elevator'],
                        'has_ramp': place_data['has_ramp'],
                        'accessible_toilet': place_data['accessible_toilet']
                    }
                })
            
            return Response({
                'success': True,
                'markers': markers,
                'user_info': {
                    'disability_type': user_disability,
                    'has_wheelchair': has_wheelchair
                }
            })
            
        except Exception as e:
            print(f"[AI추천 오류] {e}")
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)