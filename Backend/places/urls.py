from django.urls import path, include
from .views import AccessibilityListCreate

urlpatterns = [
    path('api/places/', AccessibilityListCreate.as_view(), name='accessibility-list-create'),
]