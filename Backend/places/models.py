from django.db import models

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