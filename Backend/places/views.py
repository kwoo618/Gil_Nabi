#요청/응답 로직 작성
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Accessibility
from .serializers import AccessibilitySerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

# List / Create API
class AccessibilityListAPI(ListCreateAPIView):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer
    # 👇 필터링 방식을 SearchFilter로 변경
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['id']
    filter_backends = [SearchFilter] # SearchFilter 사용
    search_fields = ['id']          # 'id' 필드를 기준으로 검색 (=?search=<id>)

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
