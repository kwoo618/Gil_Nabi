from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Accessibility
from .serializers import AccessibilitySerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.postgres.search import TrigramSimilarity
from django_filters.rest_framework import DjangoFilterBackend
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from .recommendation import RecommendationEngine
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly

# AI 추천 기능 추가
from .ai_recommendation import AIRecommendationSystem
from .accessibility_filter import AccessibilityFilter

class RecommendPlacesAPI(APIView):
    permission_classes = [AllowAny]  # 클래스 레벨로 이동
    
    def get(self, request):
        """AI 기반 장소 추천"""
        # 인증된 사용자면 그 정보 사용
        if request.user.is_authenticated:
            user = request.user
            disability_type = user.disability_type
            has_wheelchair = user.has_wheelchair
        else:
            # 쿼리 파라미터에서 가져오기
            disability_type = request.query_params.get('disability_type', 'physical')
            has_wheelchair = request.query_params.get('has_wheelchair', 'false') == 'true'
        
        top_n = int(request.query_params.get('limit', 10))
        
        # 추천 엔진 실행
        engine = RecommendationEngine()
        recommendations = engine.get_recommended_places(
            user_disability_type=disability_type,
            top_n=top_n
        )
        
        # 상세 정보 포함해서 반환
        result = []
        for rec in recommendations:
            place = Accessibility.objects.get(id=rec['place_id'])
            place_data = AccessibilitySerializer(place).data
            place_data['recommendation_score'] = rec['total_score']
            place_data['score_components'] = rec['components']
            result.append(place_data)
        
        return Response({
            'success': True,
            'count': len(result),
            'disability_type': disability_type,
            'has_wheelchair': has_wheelchair,  # 추가
            'recommendations': result
        })

# 새로운 AI 추천 API (지도 범위 포함)
class AIRecommendationAPI(APIView):
    permission_classes = [IsAuthenticated]  # 로그인 필요
    
    def post(self, request):
        """지도 범위 내 AI 추천"""
        user = request.user
        map_bounds = request.data.get('map_bounds')
        limit = request.data.get('limit', 5)
        
        if not map_bounds:
            return Response({
                'success': False,
                'error': 'map_bounds is required'
            }, status=400)
        
        ai_system = AIRecommendationSystem()
        recommendations = ai_system.get_ai_recommendations(
            user=user,
            map_bounds=map_bounds,
            limit=limit
        )
        
        # 지도 마커용 데이터
        markers = []
        for rec in recommendations:
            place = rec['place']
            markers.append({
                'place_id': place.id,
                'building_name': place.building_name,
                'position': {
                    'lat': place.latitude,
                    'lng': place.longitude
                },
                'score': rec['avg_score'],
                'review_count': rec['review_count'],
                'top_review': rec.get('top_review'),
                'accessibility': {
                    'has_ramp': place.has_ramp,
                    'wheelchair': place.wheelchair,
                    'accessible_toilet': place.accessible_toilet,
                    'has_elevator': place.has_elevator
                }
            })
        
        return Response({
            'success': True,
            'user_info': {
                'disability_type': user.disability_type,
                'has_wheelchair': user.has_wheelchair
            },
            'count': len(markers),
            'markers': markers
        })

# 접근성 필터링 API
class AccessibilityFilterAPI(APIView):
    permission_classes = [AllowAny]  # 인증 불필요
    
    def post(self, request):
        """접근성 필터링"""
        filters = request.data.get('filters', {})
        map_bounds = request.data.get('map_bounds')
        
        filter_system = AccessibilityFilter()
        filtered_places = filter_system.get_filtered_places_with_details(
            filters=filters,
            map_bounds=map_bounds
        )
        
        markers = []
        for place in filtered_places:
            markers.append({
                'place_id': place['place_id'],
                'building_name': place['building_name'],
                'position': {
                    'lat': place['location']['latitude'],
                    'lng': place['location']['longitude']
                },
                'matching_filters': place['matching_filters'],
                'accessibility': place['accessibility']
            })
        
        return Response({
            'success': True,
            'applied_filters': filters,
            'count': len(markers),
            'markers': markers
        })

# 기존 API들
class AccessibilityListAPI(ListCreateAPIView):
    serializer_class = AccessibilitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']

    # 조회는 아무나 할 수 있지만, 생성은 로그인 필요
    permission_classes = [IsAuthenticatedOrReadOnly] # 임시 비활성화

    def get_queryset(self):
        queryset = Accessibility.objects.all()
        query = self.request.query_params.get('search', None)

        if query:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity('building_name', query),
            ).filter(
                similarity__gt=0.1
            ).order_by('-similarity')

        return queryset

class AccessibilityDetailAPI(RetrieveUpdateDestroyAPIView):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer
    lookup_field = 'id'

    # 조회는 누구나 할 수 있지만, 수정 / 삭제는 로그인 필요 
    permission_classes = [IsAuthenticatedOrReadOnly] # 임시 비활성화

def show_map(request):
    places_queryset = Accessibility.objects.all()
    serializer = AccessibilitySerializer(places_queryset, many=True)
    context = {
        'places': serializer.data,
        'kakao_map_key': os.getenv('KAKAO_MAP_KEY')
    }
    return render(request, 'map.html', context)