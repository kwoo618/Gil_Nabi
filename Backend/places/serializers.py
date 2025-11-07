# places/serializers.py

from rest_framework import serializers
from .models import Accessibility

class AccessibilitySerializer(serializers.ModelSerializer):
    # 접근성 필드들을 직접 정의하여 null 허용 명시 (required=False 필수)
    has_ramp = serializers.BooleanField(required=False, allow_null=True)
    wheelchair = serializers.BooleanField(required=False, allow_null=True)
    accessible_toilet = serializers.BooleanField(required=False, allow_null=True)
    has_elevator = serializers.BooleanField(required=False, allow_null=True)

    class Meta:
        model = Accessibility
        fields = '__all__' # 모든 필드를 포함

    # --- 👇 create 메서드 오버라이드 추가 ---
    def create(self, validated_data):
        """
        신규 장소 생성 시, 접근성 정보 필드가 요청 데이터에 없으면
        None(null)으로 설정하여 저장합니다.
        """
        # 접근성 필드 목록
        accessibility_fields = ['has_ramp', 'wheelchair', 'accessible_toilet', 'has_elevator']
        
        # validated_data에 없는 접근성 필드를 찾아 None으로 설정
        for field in accessibility_fields:
            if field not in validated_data:
                validated_data[field] = None
        
        # 부모 클래스(ModelSerializer)의 원래 create 메서드를 호출하여 저장 실행
        return super().create(validated_data)

    # --- (update 메서드는 기본 동작으로도 null 처리가 잘 될 수 있음, 필요시 추가) ---
    # def update(self, instance, validated_data):
    #     # PATCH 요청 시 null 값이 올바르게 반영되도록 보장 (선택 사항)
    #     instance.has_ramp = validated_data.get('has_ramp', instance.has_ramp)
    #     instance.wheelchair = validated_data.get('wheelchair', instance.wheelchair)
    #     instance.accessible_toilet = validated_data.get('accessible_toilet', instance.accessible_toilet)
    #     instance.has_elevator = validated_data.get('has_elevator', instance.has_elevator)
    #     # 다른 필드는 부모 메서드가 처리하도록 함
    #     return super().update(instance, validated_data)