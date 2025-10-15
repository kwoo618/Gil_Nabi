from django.db import models

class Accessibility(models.Model):
    # CSV 헤더: building_name (문자열)
    building_name = models.CharField(max_length=100)
    
    # CSV 헤더: ID (숫자, 기본 키로 사용)
    id = models.BigIntegerField(primary_key=True) 
    
    # CSV 헤더: has_ramp (참/거짓)
    has_ramp = models.BooleanField(default=False)
    
    # CSV 헤더: wheelchair (참/거짓)
    wheelchair = models.BooleanField(default=False)
    
    # CSV 헤더: accessible_toilet (참/거짓)
    accessible_toilet = models.BooleanField(default=False)
    
    # CSV 헤더: has_elevator (참/거짓)
    has_elevator = models.BooleanField(default=False)
    
    # CSV 헤더: y (위도, 실수)
    latitude = models.FloatField()
    
    # CSV 헤더: x (경도, 실수)
    longitude = models.FloatField()

    def __str__(self):
        return self.building_name