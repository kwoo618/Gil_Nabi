# reviews/models.py 수정
from django.db import models 
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='작성자'
    )
    
    # place 필드 추가!
    place = models.ForeignKey(
        'places.Accessibility',
        on_delete=models.CASCADE,
        related_name='place_reviews',
        verbose_name='장소',
        null=True,
        blank=True
    )
    
    content = models.TextField(
        max_length=100,
        verbose_name='리뷰 내용'
    )
    
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        verbose_name='별점'
    )

    sentiment_score = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name='AI 감성 점수',
        help_text='0(부정) ~ 100(긍정) 사이의 AI 분석 점수'
    )
    
    disability_type = models.CharField(
        max_length=50,
        verbose_name='장애 유형'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='작성일시'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    category = models.CharField(
        max_length=20, 
        default="자유", # 기본값 설정
        verbose_name="카테고리"
    )

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='liked_reviews', 
        blank=True
    )
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        verbose_name = '리뷰'
        verbose_name_plural = '리뷰 목록'
    
    def __str__(self):
        return f"{self.user.username}의 리뷰 - {self.rating}점"