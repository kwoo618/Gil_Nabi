# reviews/management/commands/analyze_reviews.py
from django.core.management.base import BaseCommand
from reviews.models import Review
from reviews.ai_analysis import analyze_review_sentiment
import time

class Command(BaseCommand):
    help = '점수가 없는 리뷰들을 AI로 분석하여 감성 점수를 저장합니다.'

    def handle(self, *args, **options):
        # 점수가 없는(None) 리뷰만 가져오기
        reviews = Review.objects.filter(sentiment_score__isnull=True)
        total = reviews.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('분석할 리뷰가 없습니다.'))
            return

        self.stdout.write(f'총 {total}개의 리뷰 AI 분석을 시작합니다...')
        
        for i, review in enumerate(reviews):
            self.stdout.write(f'[{i+1}/{total}] 리뷰(ID:{review.id}) 분석 중... ', ending='')
            self.stdout.flush()
            
            # AI 분석 호출
            score = analyze_review_sentiment(review.content)
            
            if score is not None:
                review.sentiment_score = score
                review.save()
                self.stdout.write(self.style.SUCCESS(f'완료: {score}점'))
            else:
                self.stdout.write(self.style.ERROR('실패'))
            
            # API 호출 속도 조절 (너무 빠르면 차단될 수 있음)
            time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS('모든 작업이 완료되었습니다.'))