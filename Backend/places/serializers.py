# locations/serializers.py (새 파일)
from rest_framework import serializers
from .models import Accessibility

class AccessibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Accessibility
        fields = '__all__'