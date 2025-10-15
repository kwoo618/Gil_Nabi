#요청/응답 로직 작성
from django.shortcuts import render
from rest_framework import generics
from .models import Accessibility
from .serializers import AccessibilitySerializer
from rest_framework.generics import ListCreateAPIView

class AccessibilityListCreate(generics.ListCreateAPIView):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer

def show_map(request):
    # 2. 냉장고(DB)에서 날것의 재료(QuerySet)를 꺼냅니다.
    places_queryset = Accessibility.objects.all()

    # 3. 요리사(Serializer)에게 재료를 주고 "여러 개니까 잘 처리해줘(many=True)"라고 말합니다.
    serializer = AccessibilitySerializer(places_queryset, many=True)

    # 4. 요리사가 완성한 요리(serializer.data)를 context 상자에 담습니다.
    # serializer.data는 이제 JavaScript가 아주 좋아하는 깔끔한 리스트 형태입니다.
    context = {
        'places': serializer.data,
    }
    
    # 5. 완성된 요리가 담긴 상자를 서빙 직원에게 전달합니다.
    return render(request, 'map.html', context)
class AccessibilityListAPI(ListCreateAPIView):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer
