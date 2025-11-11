# community/urls.py

from django.urls import path, include
from rest_framework_nested import routers
from . import views

# 1. 기본 라우터 (PostViewSet 용)

router = routers.DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')

# 2. 중첩 라우터 (CommentViewSet 용 - 목록/생성)

posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', views.CommentViewSet, basename='post-comments')

# 3. 댓글 전용 라우터 (CommentViewSet 용 - 수정/삭제/좋아요)

comment_router = routers.DefaultRouter()
comment_router.register(r'comments', views.CommentViewSet, basename='comment')


# 생성된 URL들을 모두 urlpatterns에 등록
urlpatterns = [
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
    path('', include(comment_router.urls)),
]