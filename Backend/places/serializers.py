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

class AIRecommendationSerializer(serializers.Serializer):
    """AI 추천 결과 응답용 시리얼라이저"""
    id = serializers.CharField(source='place.id')
    name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    avg_rating = serializers.FloatField()
    ai_score = serializers.IntegerField()
    ai_reason = serializers.CharField()
    features = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj['place'].building_name or "이름 없는 장소"

    def get_category(self, obj):
        return getattr(obj['place'], 'category', '장소')

    def get_features(self, obj):
        place = obj['place']
        features = []
        if place.wheelchair: features.append("휠체어 접근 가능")
        if place.has_elevator: features.append("엘리베이터 있음")
        if place.has_ramp: features.append("경사로 있음")
        if place.accessible_toilet: features.append("장애인 화장실")
        return features
