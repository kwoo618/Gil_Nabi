from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from django.db.models import F

from datetime import datetime, timedelta, timezone # 날짜 계산

from .models import Post, Comment, PostLike, CommentLike
from .serializers import (
    PostListSerializer, 
    PostRetrieveSerializer, 
    PostCreateSerializer,
    CommentSerializer, 
    CommentCreateSerializer
)




class PostViewSet(viewsets.ModelViewSet):
    # 게시글에 대한 CRUD 및 '좋아요' 기능을 처리하는 ViewSet
    
    # 쿼리 최적화
    queryset = Post.objects.select_related('user').prefetch_related('comments', 'comments__user').all()
    
    def get_permissions(self):
        """
        액션별로 권한 다르게 설정 (reviews 앱 스타일)
        - list, retrieve는 누구나
        - 나머지는 인증된 사용자만
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """액션에 따라 다른 Serializer 반환"""
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'retrieve':
            return PostRetrieveSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return super().get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        # Serializer에 request context 전달 좋아요 토글을 프론트에 전달하기 위해 
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        """
        상세 조회 시, 조회수(view_count) 1 증가
        - F() 표현식을 사용해 race condition을 방지합니다.
        """
        instance = self.get_object()

        cookie_name = f'post_view_{instance.pk}'

        if cookie_name not in request.COOKIES:
        # F()를 사용해 현재 DB 값을 기준으로 1 증가
            Post.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
            instance.refresh_from_db() # 업데이트된 인스턴스를 다시 가져옴 (새로고침)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

        if cookie_name not in request.COOKIES:
            # 하루 뒤(24시간) 만료 하도록 
            expires = datetime.now() + timedelta(days=1) 
            response.set_cookie(
                key=cookie_name,
                value='true',
                expires=expires,
                httponly=True
            )
        return response

    def create(self, request, *args, **kwargs):
        """게시글 생성 (reviews 앱 스타일)"""
        print(f"\n[DEBUG] 게시글 생성 요청")
        print(f"[DEBUG] 사용자: {request.user} (ID: {request.user.id})")
        print(f"[DEBUG] Body 데이터: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"[ERROR] 데이터 검증 실패: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"[SUCCESS] 데이터 검증 통과")
        
        # 작성자를 현재 로그인한 사용자로 자동 설정
        serializer.save(user=self.request.user)
        
        print(f"[SUCCESS] 게시글 저장 완료!\n")
        
        # 생성된 정보를 반환
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """게시글 수정 (reviews 앱 스타일 - 소유자 검사)"""
        post = self.get_object()
        
        # 소유자 검사
        if post.user != request.user:
            return Response(
                {"detail": "본인이 작성한 게시글만 수정할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """게시글 삭제 (reviews 앱 스타일 - 소유자 검사)"""
        post = self.get_object()
        
        # 소유자 검사
        if post.user != request.user:
            return Response(
                {"detail": "본인이 작성한 게시글만 삭제할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like_post(self, request, pk=None):
        # 게시글 좋아요 기능

        post = self.get_object()
        user = request.user

        # 좋아요 상태와 개수를 담을 변수 
        if_liked = False 

        try:
            # 이미 좋아요 존재하면 -> 취소
            like = PostLike.objects.get(post=post, user=user)
            like.delete()

            # DB에 반영 (-1)
            Post.objects.filter(pk=post.pk).update(like_count=F('like_count') - 1)
            is_liked = False

        except PostLike.DoesNotExist:
            # 좋아요 존재하지 않으면 -> 생성
            PostLike.objects.create(post=post, user=user)

            # DB에 반영 (+1)
            Post.objects.filter(pk=post.pk).update(like_count=F('like_count') + 1)
            is_liked = True
        
        # DB에서 계산된 최신 값을 가져오기 (새로고침)
        post.refresh_from_db()

        return Response({
            "likes": post.like_count,
            "isLiked": is_liked
        }, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    # 댓글에 대한 CRUD 및 '좋아요' 기능을 처리하는 ViewSet
    
    queryset = Comment.objects.select_related('user').all()

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        # 생성/수정 시
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        # 게시글에 종속된 댓글만 필터링
        queryset = super().get_queryset()
        
        post_pk = self.kwargs.get('post_pk')
        if post_pk:
            queryset = queryset.filter(post_id=post_pk)
        
        return queryset

    def create(self, request, *args, **kwargs):
        # 댓글 생성

        print(f"\n[DEBUG] 댓글 생성 요청")
        print(f"[DEBUG] 사용자: {request.user} (ID: {request.user.id})")
        print(f"[DEBUG] Body 데이터: {request.data}")
        
        post_pk = self.kwargs.get('post_pk')
        if not post_pk:
            raise NotFound("게시글을 찾을 수 없습니다 (URL에 post_pk 누락).")
            
        post = get_object_or_404(Post, pk=post_pk)
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"[ERROR] 데이터 검증 실패: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # user와 post를 자동으로 주입
        serializer.save(user=self.request.user, post=post)
        
        # Post의 comment_count 1 증가
        Post.objects.filter(pk=post_pk).update(comment_count=F('comment_count') + 1)
        
        print(f"[SUCCESS] 댓글 저장 완료!\n")
        
        # CommentCreateSerializer는 'content'만 있으므로,
        # 'reviews' 앱처럼 생성된 객체의 전체 정보를 반환하려면 CommentSerializer를 사용
        response_serializer = CommentSerializer(serializer.instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """댓글 수정 (reviews 앱 스타일 - 소유자 검사)"""
        comment = self.get_object()
        
        # 소유자 검사
        if comment.user != request.user:
            return Response(
                {"detail": "본인이 작성한 댓글만 수정할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """댓글 삭제 (reviews 앱 스타일 - 소유자 검사)"""
        comment = self.get_object()
        
        # 소유자 검사
        if comment.user != request.user:
            return Response(
                {"detail": "본인이 작성한 댓글만 삭제할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        post = comment.post # 삭제되기 전에 post 객체를 가져옴
        
        # 댓글 삭제
        response = super().destroy(request, *args, **kwargs)
        
        # Post의 comment_count 1 감소
        Post.objects.filter(pk=post.pk).update(comment_count=F('comment_count') - 1)
        
        return response

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like_comment(self, request, pk=None):
        # 댓글 좋아요 기능
        comment = self.get_object()
        user = request.user

        try:
            like = CommentLike.objects.get(comment=comment, user=user)
            # 존재하면 -> 삭제 
            like.delete()
            Comment.objects.filter(pk=comment.pk).update(like_count=F('like_count') - 1)
            return Response({"detail": "좋아요가 취소되었습니다."}, status=status.HTTP_204_NO_CONTENT)

        except CommentLike.DoesNotExist:
            # 존재하지 않으면 -> 생성 
            CommentLike.objects.create(comment=comment, user=user)
            Comment.objects.filter(pk=comment.pk).update(like_count=F('like_count') + 1)
            return Response({"detail": "좋아요를 눌렀습니다."}, status=status.HTTP_201_CREATED)