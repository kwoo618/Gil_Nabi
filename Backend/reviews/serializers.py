from rest_framework import serializers
from .models import Review 
from django.contrib.auth import get_user_model

User = get_user_model()

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )
    
    user_disability_type = serializers.CharField(
        source='user.disability_type',
        read_only=True  # place_id 제거!
    )
    
    # place_id는 별도 필드로 추가
    place_id = serializers.CharField(
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'username',
            'user_disability_type',
            'place_id',  # 추가
            'place',     # 추가 (아직 모델에는 없지만)
            'content',
            'rating',
            'disability_type',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'place', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # place_id로 place 객체 찾기
        place_id = validated_data.pop('place_id', None)
        if place_id:
            from places.models import Accessibility
            try:
                validated_data['place'] = Accessibility.objects.get(id=place_id)
            except Accessibility.DoesNotExist:
                pass  # place가 없으면 그냥 진행
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
            
            if not validated_data.get('disability_type'):
                validated_data['disability_type'] = request.user.disability_type
        
        return super().create(validated_data)
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("별점은 1점에서 5점 사이여야 합니다.")
        return value


class ReviewListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True,
        required=False
    )
    
    class Meta:
        model = Review
        fields = [
            'id',
            'username',
            'rating',
            'content',
            'disability_type',
            'created_at'
        ]