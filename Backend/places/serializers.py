from rest_framework import serializers
from .models import Accessibility

class AccessibilitySerializer(serializers.ModelSerializer):
    # 접근성 필드들을 직접 정의하여 null 허용 명시
    has_ramp = serializers.BooleanField(required=False, allow_null=True)
    wheelchair = serializers.BooleanField(required=False, allow_null=True)
    accessible_toilet = serializers.BooleanField(required=False, allow_null=True)
    has_elevator = serializers.BooleanField(required=False, allow_null=True)

    class Meta:
        model = Accessibility
        fields = '__all__'

    def create(self, validated_data):
        """신규 장소 생성 시 누락된 필드는 None(null)으로 저장"""
        accessibility_fields = ['has_ramp', 'wheelchair', 'accessible_toilet', 'has_elevator']
        for field in accessibility_fields:
            if field not in validated_data:
                validated_data[field] = None
        return super().create(validated_data)

# ✨ 이 클래스가 꼭 있어야 합니다!
class AIRecommendationSerializer(serializers.Serializer):
    place = AccessibilitySerializer()
    ai_score = serializers.FloatField()
    review_count = serializers.IntegerField()
    avg_rating = serializers.FloatField()