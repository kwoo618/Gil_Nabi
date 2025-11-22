import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from places.models import Accessibility
from reviews.models import Review

User = get_user_model()

class Command(BaseCommand):
    help = 'CSV 파일로부터 리뷰 데이터를 데이터베이스에 저장합니다.'

    def handle(self, *args, **options):
        csv_file_path = 'review_data.csv'

        # 1. 사용자 자동 생성 (없으면 만듦)
        users = ['user1', 'user2', 'user3', 'user4', 'user5']
        for username in users:
            social_id = f'test_{username}'
            
            # username이나 social_id 중 하나라도 이미 존재하면 건너뜁니다.
            if User.objects.filter(username=username).exists() or User.objects.filter(social_id=social_id).exists():
                self.stdout.write(self.style.WARNING(f'사용자 {username} (social_id: {social_id})은(는) 이미 존재하므로 건너뜁니다.'))
                continue

            try:
                User.objects.create_user(
                    username=username, 
                    password='password123', 
                    nickname=f'닉네임_{username}',
                    social_id=social_id, # 임시 ID
                    provider='local'     # 임시 제공자
                )
                self.stdout.write(self.style.SUCCESS(f'사용자 {username} 생성 완료'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'사용자 {username} 생성 중 오류 발생: {e}'))