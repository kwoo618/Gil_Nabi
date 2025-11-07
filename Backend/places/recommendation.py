# places/recommendation.py
from django.db.models import Avg, Count
from .models import Accessibility
from ai_service.claude_client import ClaudeClient

class RecommendationEngine:
    def __init__(self):
        self.claude_client = ClaudeClient()
    
    def calculate_place_score(self, place, user_disability_type=None):
        """
        장소의 추천 점수 계산
        1. 접근성 기본 점수 (40%)
        2. AI 감성 분석 점수 (30%)
        3. 평균 별점 (30%)
        """
        score_components = {}
        
        # 1. 접근성 기본 점수 (규칙 기반)
        accessibility_score = self._calculate_accessibility_score(place, user_disability_type)
        score_components['accessibility'] = accessibility_score * 0.4
        
        # 2. AI 감성 점수 (나중에 리뷰 연동)
        # 현재는 목업 데이터로 테스트
        ai_score = 70  # 임시값, 나중에 실제 리뷰 분석
        score_components['ai_sentiment'] = ai_score * 0.3
        
        # 3. 평균 별점 (나중에 리뷰 연동)
        rating_score = 80  # 임시값, 나중에 실제 평점
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
        
        if user_disability_type == 'wheelchair':
            if place.wheelchair == True:
                score += 30
            if place.has_elevator == True:
                score += 10
            if place.has_ramp == True:
                score += 10
            if place.accessible_toilet == True:
                score += 10
                
        elif user_disability_type == 'visual':
            # 시각 장애인용 점수 (추후 필드 추가)
            score = 70
            
        elif user_disability_type == 'hearing':
            # 청각 장애인용 점수 (추후 필드 추가)
            score = 70
            
        return min(score, 100)  # 최대 100점
    
    def get_recommended_places(self, user_disability_type=None, top_n=10):
        """추천 장소 목록 반환"""
        places = Accessibility.objects.all()
        scored_places = []
        
        for place in places:
            score_data = self.calculate_place_score(place, user_disability_type)
            scored_places.append(score_data)
        
        # 점수 높은 순 정렬
        scored_places.sort(key=lambda x: x['total_score'], reverse=True)
        
        return scored_places[:top_n]