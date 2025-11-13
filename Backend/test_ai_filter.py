# test_ai_filter.py
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from places.ai_recommendation import AIRecommendationSystem
from places.accessibility_filter import AccessibilityFilter
from users.models import User
from places.models import Accessibility
from reviews.models import Review

def test_ai_recommendation():
    """AI 추천 테스트"""
    print("=" * 50)
    print("AI 추천 시스템 테스트")
    print("=" * 50)
    
    # 테스트 사용자 생성 또는 가져오기
    user, created = User.objects.get_or_create(
        social_id='test_ai_user',
        provider='kakao',
        defaults={
            'nickname': 'AI테스터',
            'disability_type': 'physical',
            'has_wheelchair': True
        }
    )
    
    if created:
        print(f"✅ 테스트 사용자 생성: {user.nickname}")
    else:
        print(f"✅ 기존 사용자 사용: {user.nickname}")
    
    # 지도 범위 설정 (대구대 주변)
    map_bounds = {
        'north': 35.910,
        'south': 35.880,
        'east': 128.870,
        'west': 128.830
    }
    
    # AI 추천 실행
    try:
        ai_system = AIRecommendationSystem()
        recommendations = ai_system.get_ai_recommendations(
            user=user,
            map_bounds=map_bounds,
            limit=5
        )
        
        print(f"\n📍 추천 결과: {len(recommendations)}개")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['place'].building_name}")
            print(f"   점수: {rec['avg_score']}점")
            print(f"   리뷰: {rec['review_count']}개")
            print(f"   위치: ({rec['place'].latitude}, {rec['place'].longitude})")
        
        return True
        
    except Exception as e:
        print(f"❌ AI 추천 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_accessibility_filter():
    """필터링 테스트"""
    print("\n" + "=" * 50)
    print("접근성 필터 테스트")
    print("=" * 50)
    
    # 필터 설정
    filters = {
        'wheelchair': True,
        'has_elevator': True,
        'has_ramp': False,
        'accessible_toilet': False
    }
    
    map_bounds = {
        'north': 35.910,
        'south': 35.880,
        'east': 128.870,
        'west': 128.830
    }
    
    try:
        filter_system = AccessibilityFilter()
        filtered_places = filter_system.get_filtered_places_with_details(
            filters=filters,
            map_bounds=map_bounds
        )
        
        print(f"\n📍 필터 결과: {len(filtered_places)}개")
        print("적용 필터: 휠체어(O), 엘리베이터(O)")
        
        for i, place in enumerate(filtered_places[:5], 1):
            print(f"\n{i}. {place['building_name']}")
            print(f"   매칭: {', '.join(place['matching_filters'])}")
            print(f"   위치: ({place['location']['latitude']}, {place['location']['longitude']})")
        
        return True
        
    except Exception as e:
        print(f"❌ 필터링 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_check():
    """데이터 확인"""
    print("\n" + "=" * 50)
    print("데이터베이스 상태 확인")
    print("=" * 50)
    
    # 장소 데이터
    places_count = Accessibility.objects.count()
    print(f"✅ 등록된 장소: {places_count}개")
    
    # 휠체어 접근 가능 장소
    wheelchair_places = Accessibility.objects.filter(wheelchair=True).count()
    print(f"✅ 휠체어 접근 가능: {wheelchair_places}개")
    
    # 리뷰 데이터
    reviews_count = Review.objects.count()
    print(f"✅ 등록된 리뷰: {reviews_count}개")
    
    # 사용자 데이터
    users_count = User.objects.count()
    print(f"✅ 등록된 사용자: {users_count}명")
    
    # 샘플 장소 출력
    sample_places = Accessibility.objects.all()[:3]
    print("\n📍 샘플 장소:")
    for place in sample_places:
        print(f"  - {place.building_name} (ID: {place.id})")

if __name__ == "__main__":
    print("🚀 길나비 AI/필터 시스템 테스트 시작\n")
    
    # 데이터 확인
    test_data_check()
    
    # AI 추천 테스트
    ai_result = test_ai_recommendation()
    
    # 필터링 테스트
    filter_result = test_accessibility_filter()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    print(f"AI 추천: {'✅ 성공' if ai_result else '❌ 실패'}")
    print(f"필터링: {'✅ 성공' if filter_result else '❌ 실패'}")