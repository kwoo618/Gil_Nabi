#요청/응답 로직 작성
from django.shortcuts import render
from .models import Accessibility
from .serializers import AccessibilitySerializer
from rest_framework.generics import ListCreateAPIView


def show_map(request):
    places_queryset = Accessibility.objects.all()
    serializer = AccessibilitySerializer(places_queryset, many=True)
    context = {
        'places': serializer.data,
    }
    
    return render(request, 'map.html', context)

class AccessibilityListAPI(ListCreateAPIView):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer
