#데이터베이스 모델 정의
from django.db import models

class Accessibility(models.Model):
    kakao_place_id = models.CharField(max_length=50, primary_key=True, unique=True)
    name = models.CharField(max_length=100, blank=True) # 장소 이름도 저장
    has_ramp = models.BooleanField(null=True, blank=True)
    wheelchair_accessible = models.BooleanField(null=True, blank=True)
    accessible_restroom = models.BooleanField(null=True, blank=True)
    has_elevator = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or f"Place (ID: {self.kakao_place_id})"