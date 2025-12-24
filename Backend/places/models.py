
from django.db import models
from django.conf import settings

class Accessibility(models.Model):
    building_name = models.CharField(max_length=100)
    
    # ID는 CharField (이전 수정 유지)
    id = models.CharField(max_length=50, primary_key=True) 
    
    # --- 👇 null=True, blank=True 다시 추가! ---
    has_ramp = models.BooleanField(null=True, blank=True)
    wheelchair = models.BooleanField(null=True, blank=True)
    accessible_toilet = models.BooleanField(null=True, blank=True)
    has_elevator = models.BooleanField(null=True, blank=True)
    # --- ---
    
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.building_name

class ModificationRequest(models.Model):
    """일반 회원의 장소 정보 수정 요청"""
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('approved', '승인됨'),
        ('rejected', '거절됨'),
    ]

    place = models.ForeignKey(Accessibility, on_delete=models.CASCADE, related_name='modification_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # 변경 요청할 데이터 필드들
    wheelchair = models.BooleanField(null=True, blank=True)
    has_elevator = models.BooleanField(null=True, blank=True)
    has_ramp = models.BooleanField(null=True, blank=True)
    accessible_toilet = models.BooleanField(null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_status_display()}] {self.place.building_name} - {self.user}"