# Backend/places/ai_recommendation.py

import os
import json
import anthropic
from django.conf import settings
from django.db.models import Avg
from reviews.models import Review
from .models import Accessibility

class AIRecommendationSystem:
    """Claude AI 기반 추천 시스템"""
    
    def __init__(self):
        # API 키 로드
        api_key = getattr(settings, 'CLAUDE_API_KEY', None)
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None
            print("⚠️ CLAUDE_API_KEY가 설정되지 않았습니다.")

    def get_ai_recommendations(self, user, map_bounds, limit=5):
        """
        1. 지도 범위 및 필터로 장소 1차 검색
        2. 후보 장소들의 리뷰 데이터 수집
        3. Claude AI에게 분석 요청
        4. 결과 반환
        """
        
        # --- 1. 후보 장소 필터링 ---
        # views.py에서 map_bounds 안에 filters를 합쳐서 보내줍니다.
        filters = map_bounds.get('filters', {})
        
        # 지도 범위 내 장소 검색
        places = Accessibility.objects.filter(
            latitude__gte=map_bounds.get('south', 35.88),
            latitude__lte=map_bounds.get('north', 35.91),
            longitude__gte=map_bounds.get('west', 128.84),
            longitude__lte=map_bounds.get('east', 128.87)
        )

        # 필터 조건 적용 (체크된 항목만 필터링)
        if filters.get('wheelchair'):
            places = places.filter(wheelchair=True)
        if filters.get('has_elevator'):
            places = places.filter(has_elevator=True)
        if filters.get('has_ramp'):
            places = places.filter(has_ramp=True)
        if filters.get('accessible_toilet'):
            places = places.filter(accessible_toilet=True)

        # 사용자 프로필 기반 필수 조건 (예: 휠체어 사용자)
        if getattr(user, 'has_wheelchair', False):
            places = places.filter(wheelchair=True)
        
        # --- 2. 리뷰 데이터 수집 ---
        candidate_places = []
        for place in places:
            # 최신 리뷰 5개 가져오기
            reviews = Review.objects.filter(place=place).order_by('-created_at')[:5]
            
            if reviews.exists():
                avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
                candidate_places.append({
                    'obj': place,
                    'reviews': [r.content for r in reviews],
                    'avg_rating': avg_rating
                })
        
        # 평점 순으로 정렬하여 상위 8개만 AI에게 보냄 (속도/비용 최적화)
        candidate_places.sort(key=lambda x: x['avg_rating'], reverse=True)
        target_candidates = candidate_places[:8] 

        if not target_candidates:
            return [] # 조건에 맞는 장소가 없음

        # --- 3. AI 분석 요청 ---
        ai_results = []
        if self.client:
            try:
                ai_results = self._ask_claude(user, target_candidates)
            except Exception as e:
                print(f"🔥 AI 호출 실패: {e}")
                return self._fallback_result(target_candidates, limit)
        else:
            return self._fallback_result(target_candidates, limit)

        # --- 4. 결과 매핑 ---
        final_recommendations = []
        
        if not ai_results:
             return self._fallback_result(target_candidates, limit)

        for res in ai_results[:limit]:
            # AI가 반환한 ID로 장소 객체 찾기
            target_place = next((p for p in target_candidates if str(p['obj'].id) == str(res.get('id'))), None)
            
            if target_place:
                place_obj = target_place['obj']
                final_recommendations.append({
                    'place': place_obj,
                    'ai_score': res.get('score', 0), 
                    'review_count': len(target_place['reviews']),
                    'avg_rating': target_place['avg_rating'],
                    'ai_reason': res.get('reason', '')
                })

        # 점수 높은 순 정렬
        final_recommendations.sort(key=lambda x: x['ai_score'], reverse=True)
        return final_recommendations

    def _ask_claude(self, user, candidates):
        """Claude에게 프롬프트를 보내고 JSON 응답을 받음"""
        
        disability_type = getattr(user, 'disability_type', '미설정')
        has_wheelchair = getattr(user, 'has_wheelchair', False)
        
        user_info_str = f"장애 유형: {disability_type}"
        if has_wheelchair:
            user_info_str += ", 휠체어 사용함"

        # 데이터 JSON 변환
        places_data_for_ai = []
        for item in candidates:
            places_data_for_ai.append({
                "id": str(item['obj'].id),
                "name": item['obj'].building_name,
                "reviews": item['reviews'],
                "accessibility": {
                    "wheelchair": item['obj'].wheelchair,
                    "elevator": item['obj'].has_elevator,
                    "ramp": item['obj'].has_ramp,
                    "toilet": item['obj'].accessible_toilet
                }
            })

        prompt = f"""
        당신은 장애인 접근성 전문가 '길나비 AI'입니다.
        
        [사용자 정보]
        {user_info_str}

        [장소 및 리뷰 데이터]
        {json.dumps(places_data_for_ai, ensure_ascii=False)}

        [목표]
        위 사용자에게 가장 적합한 장소를 추천하고 순위를 매겨주세요.
        리뷰의 내용을 분석하여 사용자의 장애 유형에 대해 긍정적인지 부정적인지 판단하여 0~100점 사이의 점수를 매기세요.

        [출력 형식]
        반드시 오직 JSON 배열 형식으로만 응답하세요. 다른 말은 하지 마세요.
        형식:
        [
            {{
                "id": "장소ID",
                "score": 85,
                "reason": "추천 이유 한 줄 요약"
            }},
            ...
        ]
        """

        # API 호출
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1000,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = message.content[0].text
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("JSON 파싱 에러, 원본 응답:", content)
            return []

    def _fallback_result(self, candidates, limit):
        """AI 실패 시 평점 순 단순 반환"""
        results = []
        for item in candidates[:limit]:
            results.append({
                'place': item['obj'],
                'ai_score': item['avg_rating'] * 20, 
                'review_count': len(item['reviews']),
                'avg_rating': item['avg_rating'],
                'ai_reason': "사용자 평점이 높은 인기 장소입니다."
            })
        return results