import csv
from django.core.management.base import BaseCommand
from places.models import Accessibility

class Command(BaseCommand):
    help = 'CSV 파일로부터 장소 데이터를 데이터베이스에 저장합니다.'

    def handle(self, *args, **options):
        csv_file_path = 'places_data.csv' # 파일명 확인!

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader) # 헤더 건너뛰기

                self.stdout.write('기존 데이터를 삭제합니다...')
                Accessibility.objects.all().delete()

                for row in reader:
                    # CSV 컬럼 순서: 
                    # 0:이름, 1:ID, 2:경사로, 3:휠체어, 4:화장실, 5:엘리베이터, 6:위도, 7:경도
                    
                    Accessibility.objects.create(
                        building_name=row[0],
                        id=str(row[1]), # ID는 문자열로
                        has_ramp=row[2].upper() == 'TRUE',
                        wheelchair=row[3].upper() == 'TRUE',
                        accessible_toilet=row[4].upper() == 'TRUE',
                        has_elevator=row[5].upper() == 'TRUE',
                        latitude=float(row[6]),
                        longitude=float(row[7])
                    )

            self.stdout.write(self.style.SUCCESS('성공적으로 장소 데이터를 저장했습니다.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV 파일을 찾을 수 없습니다.'))