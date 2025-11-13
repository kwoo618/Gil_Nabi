# create_test_reviews.py
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from places.models import Accessibility
from reviews.models import Review

def create_test_reviews():
    """테스트 리뷰 데이터 생성"""
    print("=" * 50)
    print("테스트 리뷰 데이터 생성")
    print("=" * 50)
    
    # 1. 테스트 사용자 생성
    test_users = []
    
    user1, _ = User.objects.get_or_create(
        social_id='test_user1',
        provider='kakao',
        defaults={
            'nickname': '휠체어사용자',
            'disability_type': 'physical',
            'has_wheelchair': True
        }
    )
    test_users.append(user1)
    
    user2, _ = User.objects.get_or_create(
        social_id='test_user2',
        provider='google',
        defaults={
            'nickname': '시각장애인',
            'disability_type': 'visual',
            'has_wheelchair': False
        }
    )
    test_users.append(user2)
    
    user3, _ = User.objects.get_or_create(
        social_id='test_user3',
        provider='kakao',
        defaults={
            'nickname': '지체장애인',
            'disability_type': 'physical',
            'has_wheelchair': False
        }
    )
    test_users.append(user3)
    
    print(f"✅ 테스트 사용자 {len(test_users)}명 준비 완료")
    
    # 2. 장소 가져오기
    places = Accessibility.objects.filter(
        id__in=['17561073', '17565571', '1984484431', '17564806', '17561071']
    )
    
    if not places.exists():
        # ID가 없으면 아무거나 5개
        places = Accessibility.objects.all()[:5]
    
    print(f"✅ 테스트 장소 {places.count()}개 준비 완료")
    
    # 3. 리뷰 데이터 생성
    reviews_data = [
        {
            'place': places[0],  # 성산홀
            'user': user1,
            'rating': 5,
            'content': '휠체어 접근이 매우 편리합니다. 엘리베이터가 넓고 경사로도 완만해서 이동하기 좋아요. 장애인 화장실도 깨끗하게 관리되고 있습니다.',
            'disability_type': 'physical'
        },
        {
            'place': places[0],  # 성산홀
            'user': user3,
            'rating': 4,
            'content': '전반적으로 접근성이 좋은 편입니다. 입구의 경사로가 조금 가파르긴 하지만 혼자서도 충분히 올라갈 수 있었어요.',
            'disability_type': 'physical'
        },
        {
            'place': places[1] if places.count() > 1 else places[0],  # 경영 1관
            'user': user2,
            'rating': 3,
            'content': '점자 안내판이 없어서 찾기 어려웠습니다. 엘리베이터에 음성 안내가 있었으면 좋겠어요.',
            'disability_type': 'visual'
        },
        {
            'place': places[2] if places.count() > 2 else places[0],  # 경영 2관
            'user': user1,
            'rating': 5,
            'content': '휠체어 이용자에게 최고의 건물입니다! 자동문이 있고 복도도 넓어서 이동이 자유로워요. 강력 추천합니다.',
            'disability_type': 'physical'
        },
        {
            'place': places[3] if places.count() > 3 else places[0],  # 교수학습지원관
            'user': user3,
            'rating': 2,
            'content': '엘리베이터가 자주 고장나고 경사로가 미끄러워서 위험합니다. 개선이 필요해 보입니다.',
            'disability_type': 'physical'
        }
    ]
    
    # 4. 리뷰 저장
    created_reviews = []
    for review_data in reviews_data:
        review, created = Review.objects.get_or_create(
            user=review_data['user'],
            place=review_data['place'],
            defaults={
                'rating': review_data['rating'],
                'content': review_data['content'],
                'disability_type': review_data['disability_type']
            }
        )
        
        if created:
            # 생성 시간 랜덤 설정 (최근 30일 이내)
            days_ago = random.randint(1, 30)
            review.created_at = datetime.now() - timedelta(days=days_ago)
            review.save()
            created_reviews.append(review)
            print(f"✅ 리뷰 생성: {review.user.nickname} → {review.place.building_name} ({review.rating}점)")
        else:
            print(f"⚠️ 이미 존재: {review.user.nickname} → {review.place.building_name}")
    
    print(f"\n📊 총 {len(created_reviews)}개의 리뷰가 생성되었습니다.")
    
    # 5. 통계 출력
    total_reviews = Review.objects.count()
    print(f"\n📈 전체 리뷰 통계:")
    print(f"  - 총 리뷰 수: {total_reviews}개")
    
    # 장애 유형별 리뷰 수
    physical_reviews = Review.objects.filter(disability_type='physical').count()
    visual_reviews = Review.objects.filter(disability_type='visual').count()
    hearing_reviews = Review.objects.filter(disability_type='hearing').count()
    
    print(f"  - 지체장애: {physical_reviews}개")
    print(f"  - 시각장애: {visual_reviews}개")
    print(f"  - 청각장애: {hearing_reviews}개")
    
    # 평균 평점
    from django.db.models import Avg
    avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        print(f"  - 평균 평점: {avg_rating:.2f}점")
    
    return created_reviews

def view_reviews():
    """생성된 리뷰 확인"""
    print("\n" + "=" * 50)
    print("생성된 리뷰 목록")
    print("=" * 50)
    
    reviews = Review.objects.all().select_related('user', 'place').order_by('-created_at')[:10]
    
    for review in reviews:
        print(f"\n📝 리뷰 ID: {review.id}")
        print(f"   작성자: {review.user.nickname} ({review.user.disability_type})")
        print(f"   장소: {review.place.building_name if review.place else '장소 없음'}")
        print(f"   평점: {'⭐' * review.rating} ({review.rating}점)")
        print(f"   내용: {review.content[:50]}...")
        print(f"   작성일: {review.created_at.strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    print("🚀 테스트 리뷰 생성 시작\n")
    
    # 리뷰 생성
    create_test_reviews()
    
    # 생성된 리뷰 확인
    view_reviews()
    
    print("\n✅ 완료!")