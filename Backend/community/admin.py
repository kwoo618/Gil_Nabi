from django.contrib import admin
from .models import Post, Comment, PostLike, CommentLike

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """게시글 관리자"""
    
    list_display = [
        'id', 
        'title', 
        'user', 
        'view_count', 
        'like_count', 
        'comment_count',
        'created_at'
    ]
    
    list_filter = ['created_at']
    search_fields = ['title', 'content', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'view_count', 'like_count', 'comment_count']
    
    ordering = ['-created_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'title', 'content')
        }),
        ('통계', {
            'fields': ('view_count', 'like_count', 'comment_count')
        }),
        ('일시', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """댓글 관리자"""
    
    list_display = [
        'id',
        'post',
        'user',
        'content_preview',
        'like_count',
        'created_at'
    ]
    
    list_filter = ['created_at']
    search_fields = ['content', 'user__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at', 'like_count']
    
    ordering = ['-created_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('post', 'user', 'content')
        }),
        ('통계', {
            'fields': ('like_count',)
        }),
        ('일시', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def content_preview(self, obj):
        """댓글 내용 미리보기 (50자)"""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    content_preview.short_description = '댓글 내용'


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    """게시글 좋아요 관리자"""
    
    list_display = [
        'id',
        'post',
        'user',
        'created_at'
    ]
    
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']
    
    ordering = ['-created_at']


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """댓글 좋아요 관리자"""
    
    list_display = [
        'id',
        'comment',
        'user',
        'created_at'
    ]
    
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    
    ordering = ['-created_at']