from django.db.models import Avg, Count, Q
from reviews.models import Review
from places.models import Accessibility
from users.models import User
from ai_service.claude_client import ClaudeClient
import json

class AIRecommendationSystem:
    def __init__(self):
        self.claude_client = ClaudeClient()
    
    def get_ai_recommendations(self, user, map_bounds, limit=5):  # 상위 5개로 수정
        """
        AI 기반 장소 추천 (지도 범위 내)
        """
        # 1. 지도 범위 내 장소만 필터링
        places_in_bounds = Accessibility.objects.filter(
            latitude__gte=map_bounds['south'],
            latitude__lte=map_bounds['north'],
            longitude__gte=map_bounds['west'],
            longitude__lte=map_bounds['east']
        )
        
        # 2. 같은 장애유형의 리뷰 가져오기 (범위 내 장소만)
        place_ids = places_in_bounds.values_list('id', flat=True)
        similar_reviews = Review.objects.filter(
            disability_type=user.disability_type,
            place_id__in=place_ids
        ).select_related('place', 'user')
        
        # 3. 장소별 점수 계산
        place_scores = {}
        
        for review in similar_reviews:
            if not review.place:
                continue
                
            place_id = review.place.id
            
            if place_id not in place_scores:
                place_scores[place_id] = {
                    'place': review.place,
                    'reviews': [],
                    'total_score': 0,
                    'review_count': 0,
                    'accessibility_info': {
                        'has_ramp': review.place.has_ramp,
                        'wheelchair': review.place.wheelchair,
                        'accessible_toilet': review.place.accessible_toilet,
                        'has_elevator': review.place.has_elevator
                    }
                }
            
            # AI 점수 분석
            score = self._analyze_review_score(review, user)
            
            place_scores[place_id]['reviews'].append({
                'content': review.content[:50] + '...' if len(review.content) > 50 else review.content,
                'rating': review.rating,
                'ai_score': score
            })
            place_scores[place_id]['total_score'] += score
            place_scores[place_id]['review_count'] += 1
        
        # 4. 평균 점수 계산 및 정렬
        recommendations = []
        for place_id, data in place_scores.items():
            if data['review_count'] > 0:
                avg_score = data['total_score'] / data['review_count']
                recommendations.append({
                    'place_id': place_id,
                    'place': data['place'],
                    'avg_score': round(avg_score, 1),
                    'review_count': data['review_count'],
                    'accessibility_info': data['accessibility_info'],
                    'top_review': max(data['reviews'], key=lambda x: x['ai_score'])  # 최고 리뷰 1개
                })
        
        # 5. 상위 5개 반환
        recommendations.sort(key=lambda x: x['avg_score'], reverse=True)
        return recommendations[:limit]
    
    def _analyze_review_score(self, review, user):
        """리뷰 점수 계산 (간소화)"""
        score = 0
        
        # 1. 별점 점수 (40점)
        score += (review.rating / 5) * 40
        
        # 2. AI 감성 분석 (30점) - 간단한 키워드 기반으로 변경 (API 호출 줄이기)
        positive_keywords = ['좋', '편', '쉽', '깨끗', '친절', '넓', '안전']
        negative_keywords = ['불편', '어려', '좁', '위험', '없', '힘들']
        
        content_lower = review.content.lower()
        positive_count = sum(1 for word in positive_keywords if word in content_lower)
        negative_count = sum(1 for word in negative_keywords if word in content_lower)
        
        sentiment_score = (positive_count - negative_count + 5) * 3  # -15 ~ 30점
        score += max(0, min(30, sentiment_score))
        
        # 3. 사용자 조건 일치도 (30점)
        if hasattr(review.user, 'has_wheelchair'):
            if review.user.has_wheelchair == user.has_wheelchair:
                score += 30
            else:
                score += 15
        else:
            score += 15
        
        return min(score, 100)