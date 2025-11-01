# review 모델 파일 

from django.db import models 
from django.conf import settings # config/settings.py 정보 가져옴 - AUTH_USER_MODEL 참조
from django.core.validators import MinValueValidator, MaxValueValidator # 데이터가 올바른 범위 내에 있는지 확인

class Review(models.Model):

    ''' 
    리뷰 모델 클래스 
    - 사용자가 작성한 리뷰 정보를 데이터 베이스에 저장 
    - models.Model을 상속받아서 ORM 기능을 사용할 수 있게함
    '''

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # User모델을 config/setting.py에서 가져온 것 
        on_delete=models.CASCADE, # 사용자 삭제 시 리뷰 삭제
        related_name='reviews',
        verbose_name='작성자'
    )

    content = models.TextField(
        max_length=100,
        verbose_name='리뷰 내용'
    )

    rating = models.IntegerField(
        validators=[
            MinValueValidator(1), # 별점 최소 1 ~ 5점
            MaxValueValidator(5)
        ],
        verbose_name='별점'
    )

    disability_type = models.CharField(
        max_length=50,
        verbose_name='장애 유형'
    )

    created_at = models.DateTimeField(
        auto_now_add=True, # 생성 시 자동으로 현재 시간 입력 
        verbose_name='작성일시'
    )

    updated_at = models.DateTimeField(
        auto_now=True, # 수정 할 떄 자동으로 현재 시간으로 업데이트함
        verbose_name='수정일시'
    )

    # 데이터 베이스 테이블 이름, 정렬 순서 등 정의
    class Meta:
        db_table = 'reviews'        # 실제 생성될 테이블 이름 
        ordering = ['-created_at']  # 기본 정렬 : 작성일시 내림차순 
        verbose_name = '리뷰'              # 관리자 페이지 단수형 이름
        verbose_name_plural = '리뷰 목록'   # 관리자 페이지 복수형 이름

    def __str__(self):
        return f"{self.user.username}의 리뷰 - {self.rating}점"
        