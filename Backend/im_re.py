"""
리뷰 데이터 CSV 임포트 스크립트 (수정 버전)
"""

import os
import sys
import django
import csv
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reviews.models import Review
from places.models import Accessibility
from users.models import User
from django.db import models

def import_reviews():
    """CSV 파일에서 리뷰 데이터 임포트"""
    
    csv_file = 'review_data.csv'
    
    # 파일 확인
    if not os.path.exists(csv_file):
        print(f"❌ {csv_file} 파일이 없습니다")
        return
    
    print("=" * 50)
    print("📝 리뷰 데이터 임포트 시작")
    print("=" * 50)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    # UTF-8 BOM 처리
    with open(csv_file, 'r', encoding='utf-8-sig') as file:  # utf-8-sig로 BOM 제거
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                # 장소 확인 (id 필드로 매칭)
                place_id = row['place_id'].strip()
                try:
                    place = Accessibility.objects.get(id=place_id)
                except Accessibility.DoesNotExist:
                    print(f"⚠️  장소 ID {place_id} 없음 - 스킵")
                    skip_count += 1
                    continue
                
                # 사용자 확인
                user_id = row['user_id'].strip()
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    print(f"⚠️  사용자 ID {user_id} 없음 - 스킵")
                    skip_count += 1
                    continue
                
                # 중복 체크
                if Review.objects.filter(place=place, user=user).exists():
                    print(f"⏭️  이미 존재: {place.building_name} - {user.nickname}")
                    skip_count += 1
                    continue
                
                # 리뷰 생성
                review = Review.objects.create(
                    place=place,
                    user=user,
                    rating=int(row['rating'].strip()),
                    content=row['content'].strip(),
                    disability_type=row['disability_type'].strip()
                )
                
                success_count += 1
                print(f"✅ 추가: {place.building_name} - {user.nickname} ({review.rating}점)")
                
            except Exception as e:
                error_count += 1
                print(f"❌ 오류: {e}")
                print(f"   문제 데이터: place_id={row.get('place_id')}, user_id={row.get('user_id')}")
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 임포트 결과")
    print("=" * 50)
    print(f"✅ 성공: {success_count}개")
    print(f"⏭️  스킵: {skip_count}개")
    print(f"❌ 오류: {error_count}개")
    print(f"📝 총 리뷰: {Review.objects.count()}개")
    
    # 장소별 리뷰 통계
    print("\n📍 장소별 리뷰 현황:")
    from django.db.models import Avg
    for place in Accessibility.objects.all()[:10]:
        reviews = Review.objects.filter(place=place)
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
            print(f"  - {place.building_name}: {reviews.count()}개 (평균 {avg_rating:.1f}점)")

if __name__ == "__main__":
    import_reviews()