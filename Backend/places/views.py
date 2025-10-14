#요청/응답 로직 작성
from django.shortcuts import render
from rest_framework import generics
from .models import Accessibility
from .serializers import AccessibilitySerializer

class AccessibilityListCreate(generics.ListCreateAPIView):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer


def show_map(request):
    return render(request, 'map.html')
# Create your views here.
