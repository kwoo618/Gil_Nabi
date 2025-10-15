import csv
from django.core.management.base import BaseCommand
from places.models import Accessibility

class Command(BaseCommand):
    help = 'CSV 파일로부터 장소 데이터를 데이터베이스에 저장합니다.'

    def handle(self, *args, **options):
        csv_file_path = 'places_data.csv'

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            Accessibility.objects.all().delete()

            for row in reader:
                # CSV 헤더와 models.py 필드 이름에 정확히 맞춰줍니다.
                has_ramp_bool = row[2].upper() == 'TRUE'
                wheelchair_bool = row[3].upper() == 'TRUE'
                accessible_toilet_bool = row[4].upper() == 'TRUE'
                has_elevator_bool = row[5].upper() == 'TRUE'

                Accessibility.objects.create(
                    building_name=row[0],
                    id=int(float(row[1])),  # ID를 정수로 변환
                    has_ramp=has_ramp_bool, # 'ramp'가 아닌 'has_ramp'
                    wheelchair=wheelchair_bool,
                    accessible_toilet=accessible_toilet_bool,
                    has_elevator=has_elevator_bool,
                    latitude=row[6],
                    longitude=row[7]
                )

        self.stdout.write(self.style.SUCCESS('성공적으로 장소 데이터를 저장했습니다.'))