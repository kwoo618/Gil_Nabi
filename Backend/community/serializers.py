from rest_framework import serializers 
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    # 댓글 조회용
    nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id','user', 'nickname', 'content', 'like_count',
            'created_at', 'updated_at'
        ]

class CommentCreateSerializer(serializers.ModelSerializer):
    # 댓글 생성/수정 
    class Meta:
        model = Comment
        fields = ['content']

class PostListSerializer(serializers.ModelSerializer):
    # 게시글 목록 조회
    nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Post 
        fields = [
            'id','user', 'title', 'nickname',
            'view_count', 'like_count', 'comment_count', 'created_at',
        ]

class PostRetrieveSerializer(serializers.ModelSerializer):
    # 게시글 상세 조회 
    nickname = serializers.CharField(source='user.nickname', read_only=True)

    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post 
        fields = [
            'id','user', 'title', 'content', 
            'nickname', 'view_count', 'like_count', 
            'comment_count', 'created_at', 'updated_at', 'comments',
        ]

class PostCreateSerializer(serializers.ModelSerializer):
    # 게시글 생성/수정 
    class Meta:
        model = Post 
        fields = ['title', 'content']