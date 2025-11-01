from rest_framework import serializers
from .models import Review 
from django.contrib.auth import get_user_model # Django의 인증 시스템에서 사용자 모델을 가져옴

User = get_user_model() 

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username', # Review.user.username 경로 
        read_only=True          # GET 요청에서만 반환, POST 에서 입력 불가 
    )

    user_disability_type = serializers.CharField(
        source='user.disability_type', # User 모델의 disability_type 참조 
        read_only=True
    )

    class Meta:
        model = Review 

        fields = [
            'id',                    # 리뷰 고유 ID
            'user',                  # 작성자 ID (ForeignKey)
            'username',              # 작성자 이름 (추가 필드)
            'user_disability_type',  # 작성자 장애유형 (추가 필드)
            'content',               # 리뷰 내용
            'rating',                # 별점
            'disability_type',       # 리뷰 작성 시점의 장애유형
            'created_at',            # 작성일시
            'updated_at'             # 수정일시
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    # 새로운 리뷰를 생성할때 호출됨
    def create(self, validated_data):
        # request = self.context.get('request') # 현재 로그인한 사용자 정보 확인 
        # validated_data['user'] = request.user # 현재 로그인한 사용자를 자동으로 추가

        # disability_type이 없으면 User 모델에서 자동으로 값을 가져옴 
        if not validated_data.get('disability_type'):
            validated_data['disability_type'] = requset.user.disability_type

        return super().create(validated_data)

    def validate_rating(self, value):
        if (value < 1) or (value > 5):
            raise serializers.ValidationError("벌점은 1점에서 5점 사이여야 합니다.")
        return value

class ReviewListSerializer(serializers.ModelSerializer):
    # 리뷰 목록 조회 
    username = serializers.CharField(
        source='user.username',
        read_only=True,
        required=False # 임시 추가 테스트용
    )

    class Meta:
        model = Review 
        fields = [
            'id',              # 리뷰 ID
            'username',        # 작성자 이름
            'rating',          # 별점
            'content',         # 리뷰 내용
            'disability_type', # 장애 유형
            'created_at'       # 작성일시
        ]




