# places/recommendation.py
from django.db.models import Avg, Count
from .models import Accessibility
from ai_service.claude_client import ClaudeClient

class RecommendationEngine:
    def __init__(self):
        self.claude_client = ClaudeClient()
    
    def calculate_place_score(self, place, user_disability_type=None):
        """장소의 추천 점수 계산"""
        score_components = {}
        
        # 1. 접근성 기본 점수 (40%)
        accessibility_score = self._calculate_accessibility_score(place, user_disability_type)
        score_components['accessibility'] = accessibility_score * 0.4
        
        # 2. AI 감성 점수 (30%)
        ai_score = 70  # 임시값
        score_components['ai_sentiment'] = ai_score * 0.3
        
        # 3. 평균 별점 (30%)
        rating_score = 80  # 임시값
        score_components['rating'] = rating_score * 0.3
        
        total_score = sum(score_components.values())
        
        return {
            'total_score': round(total_score, 2),
            'components': score_components,
            'place_id': place.id,
            'place_name': place.building_name
        }
    
    def _calculate_accessibility_score(self, place, user_disability_type):
        """접근성 기본 점수 계산"""
        score = 50  # 기본 점수
        
        # ⚠️ 수정: 'wheelchair'가 아니라 'physical'
        if user_disability_type == 'physical':  # 팀원 User 모델과 일치
            if place.wheelchair == True:
                score += 30
            if place.has_elevator == True:
                score += 10
            if place.has_ramp == True:
                score += 10
            if place.accessible_toilet == True:
                score += 10
                
        elif user_disability_type == 'visual':
            score = 70
            
        elif user_disability_type == 'hearing':
            score = 70
            
        return min(score, 100)
    
    def get_recommended_places(self, user_disability_type=None, top_n=10):
        """추천 장소 목록 반환"""
        places = Accessibility.objects.all()
        scored_places = []
        
        for place in places:
            score_data = self.calculate_place_score(place, user_disability_type)
            scored_places.append(score_data)
        
        scored_places.sort(key=lambda x: x['total_score'], reverse=True)
        return scored_places[:top_n]
    
    # ⚠️ 메서드가 클래스 밖에 있었음 - 들여쓰기 수정
    def get_recommended_places_for_user(self, user=None, disability_type=None, has_wheelchair=False, top_n=10):
        """사용자 맞춤 추천"""
        places = Accessibility.objects.all()
        scored_places = []
        
        for place in places:
            score = 0
            
            if has_wheelchair and place.wheelchair:
                score += 40
            
            if user:
                from reviews.models import Review
                reviews = Review.objects.filter(
                    place=place,
                    user__disability_type=disability_type
                )
                if reviews.exists():
                    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
                    score += avg_rating * 10
            
            scored_places.append({
                'place_id': place.id,
                'place_name': place.building_name,
                'total_score': score
            })
        
        scored_places.sort(key=lambda x: x['total_score'], reverse=True)
        return scored_places[:top_n]