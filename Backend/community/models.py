from django.db import models # django는 프레임워크 전체를 말하는거고 뒤에 .db는 데이터베이스를 말하는 것임.
from django.conf import settings # django.conf는 설정 관련 모듈. settings는 config에 있는 settings.py을 말하는 거임.

class Post(models.Model):   # 게시글 

    # 작성자 
    user = models.ForeignKey(   
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name = 'posts',
        verbose_name = '작성자'
    )

    # 게시글 제목
    title = models.CharField(
        max_length=200,
        verbose_name='제목'
    )
    
    # 게시글 내용
    content = models.TextField(
        verbose_name='내용'
    )
    
    # 조회수
    view_count = models.IntegerField(
        default=0,
        verbose_name='조회수'
    )
    
    # 좋아요 수 (캐싱용 - 성능 최적화)
    like_count = models.IntegerField(
        default=0,
        verbose_name='좋아요 수'
    )
    
    # 댓글 수 (캐싱용 - 성능 최적화)
    comment_count = models.IntegerField(
        default=0,
        verbose_name='댓글 수'
    )
    
    # 작성 일시
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='작성일시'
    )
    
    # 수정 일시
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at'] # 최신순 정렬 
        verbose_name = '게시글'
        verbose_name_plural = '게시글 목록'
        indexes = [
            models.Index(fields=['-created_at']),  # 최신순 조회 최신화
            models.Index(fields=['user']),  # 사용자별 게시글 조회 최신화
        ]

        def __str__(self):
            return f"{self.user.username} - {self.title}" # 유저이름 - 제목 으로 보임 

class Comment(models.Model):    # 댓글 
    # Post 테이블 참조
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='게시글'
    )
    
    # User 테이블 참조 (작성자)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='작성자'
    )
    
    # 댓글 내용
    content = models.TextField(
        verbose_name='댓글 내용'
    )
    
    # 좋아요 수 (캐싱용 - 성능 최적화)
    like_count = models.IntegerField(
        default=0,
        verbose_name='좋아요 수'
    )
    
    # 작성 일시
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='작성일시'
    )
    
    # 수정 일시
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'comments'
        ordering = ['created_at'] # 오래된순 
        verbose_name = '댓글'
        verbose_name_plural = '댓글 목록'
        indexes = [
            models.Index(fields=['post', 'created_at']),  # 게시글별 댓글 조회 최신화
            models.Index(fields=['user']),  # 사용자별 댓글 조회 최신화
        ]

        def __str__(self):
            return f"{self.user.username} - {self.post.title}의 댓글"

class PostLike(models.Model):   # 게시글 좋아요 
    # Post 테이블 참조
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='게시글'
    )
    
    # User 테이블 참조
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_likes',
        verbose_name='사용자'
    )
    
    # 생성 일시
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='좋아요 일시'
    )
    
    class Meta:
        db_table = 'post_likes'
        verbose_name = '게시글 좋아요'
        verbose_name_plural = '게시글 좋아요 목록'
        unique_together = ['post', 'user']  # 한 사용자가 같은 게시글에 중복 좋아요 방지
        indexes = [
            models.Index(fields=['post', 'user']),  # 좋아요 여부 확인 최신화
            models.Index(fields=['user']),  # 사용자가 좋아요한 게시글 조회 최신화
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.post.title} 좋아요"

class CommentLike(models.Model):    # 댓글 좋아요 기능 
    # Comment 테이블 참조
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='댓글'
    )
    
    # User 테이블 참조
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_likes',
        verbose_name='사용자'
    )
    
    # 생성 일시
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='좋아요 일시'
    )
    
    class Meta:
        db_table = 'comment_likes'
        verbose_name = '댓글 좋아요'
        verbose_name_plural = '댓글 좋아요 목록'
        unique_together = ['comment', 'user']  # 한 사용자가 같은 댓글에 중복 좋아요 방지
        indexes = [
            models.Index(fields=['comment', 'user']),  # 좋아요 여부 확인 최적화
            models.Index(fields=['user']),  # 사용자가 좋아요한 댓글 조회 최적화
        ]
    
    def __str__(self):
        return f"{self.user.username} - 댓글 좋아요"