#요청/응답 로직 작성
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Accessibility
from .serializers import AccessibilitySerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.postgres.search import TrigramSimilarity # 유사성 검색 도구
from django_filters.rest_framework import DjangoFilterBackend

# List / Create API
class AccessibilityListAPI(ListCreateAPIView):
    serializer_class = AccessibilitySerializer
    filter_backends = [DjangoFilterBackend] # ID 필터링은 유지
    filterset_fields = ['id']

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
def show_map(request):
    places_queryset = Accessibility.objects.all()
    serializer = AccessibilitySerializer(places_queryset, many=True)
    context = {
        'places': serializer.data,
    }
    
    return render(request, 'map.html', context)
