from rest_framework import serializers
from .models import Review 
from django.contrib.auth import get_user_model
from places.models import Accessibility

User = get_user_model()

class ReviewSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    
    user_disability_type = serializers.CharField(source='user.disability_type', read_only=True)  # place_id 제거!
    
    # place_id는 별도 필드로 추가
    place_id = serializers.CharField(source='place.id', read_only=True) # 조회
    place_name = serializers.CharField(source='place.building_name', read_only=True) # 장소 이름 
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'nickname', 'user_disability_type',
            'place_id',  'place', 'place_name',
            'content', 'rating', 'disability_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'place', 'created_at', 'updated_at']

    def validate_place(self, value):
        # palce_id가 존재하는지 확인
        if not Accessibility.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("존재하지 않는 장소입니다.")
        return value

class ReviewListSerializer(serializers.ModelSerializer):
    # 목록 조회 
    nickname = serializers.SerializerMethodField()
    place_name = serializers.SerializerMethodField()  # 동적으로 가져옴
    
    class Meta:
        model = Review
        fields = [
            'id',
            'place',     
            'place_name',
            'user',
            'nickname',
            'rating',
            'content',
            'disability_type',
            'created_at'
        ]
    def get_nickname(self, obj):
        """닉네임 또는 username 반환"""
        return obj.user.nickname

    def get_place_name(self, obj):
        """place가 있으면 building_name 반환, 없으면 None"""
        if obj.place:
            return obj.place.building_name
        return None

class ReviewCreateSerializer(serializers.ModelSerializer):
    # 리뷰 작성용 
    place_id = serializers.CharField(write_only=True) # 작성시에만 사용함
    
    class Meta:
        model = Review
        fields = ['place_id', 'content', 'rating', 'disability_type']
    
    def validate_place_id(self, value):
        """장소 ID 존재 여부 확인"""
        try:
            Accessibility.objects.get(id=value)
        except Accessibility.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 장소입니다.")
        return value
    
    def create(self, validated_data):
        place_id = validated_data.pop('place_id')
        place = Accessibility.objects.get(id=place_id)
        validated_data['place'] = place
        return super().create(validated_data)
        
