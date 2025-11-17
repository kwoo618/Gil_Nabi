# fix_review_connection.py
"""
리뷰와 장소 연결 완전 수정
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reviews.models import Review
from places.models import Accessibility
from django.db import connection

def fix_all_reviews():
    print("=" * 50)
    print("리뷰 연결 수정 시작")
    print("=" * 50)
    
    # 직접 SQL로 업데이트
    with connection.cursor() as cursor:
        # 모든 리뷰의 place_id 확인
        cursor.execute("""
            SELECT r.id, r.place_id, a.building_name
            FROM reviews r
            LEFT JOIN places_accessibility a ON r.place_id = a.id
            WHERE a.id IS NULL
        """)
        
        unmatched = cursor.fetchall()
        print(f"연결 안 된 리뷰: {len(unmatched)}개")
        
        if unmatched:
            # 첫 번째 장소 가져오기
            first_place = Accessibility.objects.first()
            if first_place:
                # 연결 안 된 리뷰를 첫 번째 장소로 업데이트
                cursor.execute("""
                    UPDATE reviews 
                    SET place_id = %s 
                    WHERE place_id NOT IN (SELECT id FROM places_accessibility)
                """, [first_place.id])
                
                print(f"✅ {len(unmatched)}개 리뷰를 {first_place.building_name}으로 재연결")
    
    # 결과 확인
    print("\n장소별 리뷰 현황:")
    for place in Accessibility.objects.all()[:10]:
        count = Review.objects.filter(place_id=place.id).count()
        if count > 0:
            from django.db.models import Avg
            avg = Review.objects.filter(place_id=place.id).aggregate(Avg('rating'))['rating__avg']
            print(f"  {place.building_name}: {count}개 (평균 {avg:.1f}점)")

if __name__ == "__main__":
    fix_all_reviews()