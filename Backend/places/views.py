from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Accessibility
from .serializers import AccessibilitySerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.postgres.search import TrigramSimilarity # 유사성 검색 도구
from django_filters.rest_framework import DjangoFilterBackend
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from .recommendation import RecommendationEngine

from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated # 로그인 권한


class RecommendPlacesAPI(APIView):
    def get(self, request):
        """AI 기반 장소 추천"""
        permission_classes = [AllowAny]  # 임시 비활성화 
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
            'recommendations': result
        })

# List / Create API
class AccessibilityListAPI(ListCreateAPIView):
    serializer_class = AccessibilitySerializer
    filter_backends = [DjangoFilterBackend] # ID 필터링은 유지
    filterset_fields = ['id']

    # 조회는 아무나 할 수 있지만, 생성은 로그인 필요
    permission_classes = [AllowAny] # 임시 비활성화

    def get_queryset(self):
        queryset = Accessibility.objects.all()
        # URL 쿼리 파라미터에서 'search' 값을 가져옴 (예: ?search=성산)
        query = self.request.query_params.get('search', None)

        if query:
            # building_name 필드와 query 문자열 간의 유사도(similarity)를 계산
            queryset = queryset.annotate(
                similarity=TrigramSimilarity('building_name', query),
            ).filter(
                similarity__gt=0.1 # 유사도가 0.1 이상인 결과만 필터링 (값 조절 가능)
            ).order_by('-similarity') # 유사도가 높은 순서대로 정렬

        return queryset

# Detail / Update / Delete API
class AccessibilityDetailAPI(RetrieveUpdateDestroyAPIView):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer
    # 👇 URL의 'pk' 변수가 우리 모델의 'id' 필드를 가리킨다고 명시
    lookup_field = 'id'

    # 조회는 누구나 할 수 있지만, 수정 / 삭제는 로그인 필요 
    permission_classes = [AllowAny] # 임시 비활성화


def show_map(request):
    places_queryset = Accessibility.objects.all()
    serializer = AccessibilitySerializer(places_queryset, many=True)
    context = {
        'places': serializer.data,
        'kakao_map_key': os.getenv('KAKAO_MAP_KEY')
    }
    
    return render(request, 'map.html', context)
