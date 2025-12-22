from rest_framework import serializers 
from django.contrib.auth import get_user_model
from .models import Post, Comment, PostLike

User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    """댓글 조회용"""
    nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id','user', 'nickname', 'content', 'like_count',
            'created_at', 'updated_at'
        ]

class CommentCreateSerializer(serializers.ModelSerializer):
    """댓글 생성/수정"""
    class Meta:
        model = Comment
        fields = ['content']

class PostListSerializer(serializers.ModelSerializer):
    """게시글 목록 조회"""
    
    nickname = serializers.CharField(source='user.nickname', read_only=True)

    likes = serializers.IntegerField(source='like_count', read_only=True)
    
    # SerializerMethodField로 선언
    isLiked = serializers.SerializerMethodField()

    class Meta:
        model = Post 
        fields = [
            'id',
            'user', 
            'title', 
            'content',
            'nickname', 
            'view_count', 
            'likes', 
            'comment_count', 
            'created_at',
            'isLiked',       
        ]
    
    def get_isLiked(self, obj):
        """현재 사용자의 좋아요 여부"""
        request = self.context.get('request')
        
        # 로그인 안 한 경우
        if not request or not request.user.is_authenticated:
            return False
        
        # related_name='likes' 사용
        return obj.likes.filter(user=request.user).exists()

class PostRetrieveSerializer(serializers.ModelSerializer):
    """게시글 상세 조회"""
    
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    likes = serializers.IntegerField(source='like_count', read_only=True)
    # SerializerMethodField로 선언
    isLiked = serializers.SerializerMethodField()

    class Meta:
        model = Post 
        fields = [
            'id',
            'user', 
            'title', 
            'content', 
            'nickname', 
            'view_count', 
            'likes', 
            'comment_count', 
            'created_at', 
            'updated_at', 
            'comments',
            'isLiked',
        ]
    
    def get_isLiked(self, obj):
        """현재 사용자의 좋아요 여부"""
        request = self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            return False
        
        return obj.likes.filter(user=request.user).exists()

class PostCreateSerializer(serializers.ModelSerializer):
    """게시글 생성/수정"""
    class Meta:
        model = Post 
        fields = ['title', 'content']