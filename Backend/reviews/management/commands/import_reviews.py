import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from places.models import Accessibility
from reviews.models import Review

User = get_user_model()

class Command(BaseCommand):
    help = 'CSV 파일로부터 리뷰 데이터를 데이터베이스에 저장합니다.'

    def handle(self, *args, **options):
        csv_file_path = 'reviews_data.csv'

        # 1. 사용자 자동 생성 (없으면 만듦)
        users = ['user1', 'user2', 'user3', 'user4', 'user5']
        for username in users:
            # social_id가 있는지 먼저 확인 (username이 아니라 식별자로 확인)
            social_id = f"social_{username}"
            
            if not User.objects.filter(social_id=social_id).exists():
                try:
                    # ✨ 수정된 부분: social_id와 provider 필수값 추가
                    User.objects.create_user(
                        social_id=social_id,       # 필수: 소셜 ID (임의값)
                        provider='local',          # 필수: 가입 경로 (임의값)
                        username=username, 
                        password='password123', 
                        nickname=f'닉네임_{username}',
                        disability_type='none' 
                    )
                    self.stdout.write(f'사용자 {username} 생성 완료')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'사용자 {username} 생성 중 오류: {e}'))

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # 기존 리뷰 삭제 (선택사항 - 중복 방지)
                Review.objects.all().delete()
                
                count = 0
                for row in reader:
                    try:
                        place_id = row['place_id']
                        username = row['username']
                        
                        # 장소 찾기
                        place = Accessibility.objects.get(id=place_id)
                        
                        # 사용자 찾기 (social_id로 생성했으므로 username으로 필터링하거나 social_id로 찾기)
                        # 여기서는 편의상 username 필드로 찾습니다.
                        user = User.objects.get(username=username)
                        
                        # 리뷰 생성
                        Review.objects.create(
                            place=place,
                            user=user,
                            rating=int(row['rating']),
                            content=row['content'],
                            disability_type=row['disability_type']
                        )
                        count += 1
                    except Accessibility.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'장소 ID {place_id}를 찾을 수 없어 건너뜁니다.'))
                    except User.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'사용자 {username}를 찾을 수 없어 건너뜁니다.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'리뷰 저장 중 오류 발생: {e}'))

            self.stdout.write(self.style.SUCCESS(f'총 {count}개의 리뷰를 성공적으로 저장했습니다.'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'{csv_file_path} 파일을 찾을 수 없습니다. Backend 폴더에 파일이 있는지 확인해주세요.'))