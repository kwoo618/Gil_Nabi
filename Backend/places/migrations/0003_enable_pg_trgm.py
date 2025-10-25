# places/migrations/000X_enable_pg_trgm.py
from django.db import migrations
# 👇 PostgreSQL 확장 기능 도구 import
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):

    # 👇 이전 마이그레이션 파일 이름 (0001_initial)
    dependencies = [
        ('places', '0001_initial'),
    ]

    operations = [
        # 👇 pg_trgm 확장 기능을 활성화하는 작업 추가
        TrigramExtension(),
    ]