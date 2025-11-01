# reviews/views.py

from rest_framework import viewsets, permissions, status  # viewsets : CRUD 기능을 한번에 제공함 ㄷㄷㄷㄷ 지린다.
from rest_framework.decorators import action  # 함수나 메서드에 추가 기능을 부여해줌
from rest_framework.response import Response  # API 응답 클래스
from django.utils.decorators import method_decorator  
from django.views.decorators.csrf import csrf_exempt  

from .models import Review 
from .serializers import ReviewSerializer, ReviewListSerializer


@method_decorator(csrf_exempt, name='dispatch')  # CSRF 면제 추가 / 테스트용
class ReviewViewSet(viewsets.ModelViewSet):
    """리뷰에 대한 모든 CRUD 작업을 처리하는 ViewSet"""
    
    queryset = Review.objects.all()  # 모든 리뷰
    
    # 테스트용: 인증 완전 비활성화
    # 나중에 프론트엔드 갈때 JWT + Redis 사용해서 구축해야됨 (User 모델, Review모델, Community 모델 싹 다)
    permission_classes = []
    authentication_classes = []

    def get_serializer_class(self):
        """목록 조회 시 간단한 시리얼라이저 사용"""
        if self.action == 'list':
            return ReviewListSerializer  # 목록 조회 시 
        return ReviewSerializer          # 그 외 나머지 

    def get_queryset(self):
        """필터링된 쿼리셋 반환"""
        queryset = Review.objects.select_related('user')
        
        # URL 쿼리 파라미터로 필터링
        disability_type = self.request.query_params.get('disability_type', None)
        rating = self.request.query_params.get('rating', None)

        # 파라미터가 있으면 해당 조건으로 필터링
        if disability_type:
            queryset = queryset.filter(disability_type=disability_type)  # 장애 유형이 일치하는 리뷰만 필터링 

        if rating: 
            queryset = queryset.filter(rating=rating)  # 별점 점수로 필터링 

        return queryset
    
    def perform_create(self, serializer):
        """
        리뷰 생성 시 호출
        테스트용: user_id로 사용자 찾기
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # URL 파라미터 또는 body에서 user_id 가져오기
        user_id = self.request.query_params.get('user_id') or self.request.data.get('user_id')
        
        print(f"[DEBUG] 받은 user_id: {user_id}")
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                print(f"[SUCCESS] 사용자 찾음: {user.username} (ID: {user.id})")
                serializer.save(user=user)
                return
            except User.DoesNotExist:
                print(f"[ERROR] user_id {user_id}에 해당하는 사용자 없음")
        
        # user_id 없으면 첫 번째 사용자 사용 (테스트용)
        user = User.objects.first()
        if user:
            print(f"[INFO] 기본 사용자 사용: {user.username}")
            serializer.save(user=user)
        else:
            print("[ERROR] 사용 가능한 사용자가 없음")

    def create(self, request, *args, **kwargs):
        """리뷰 생성 - user_id로 사용자 찾아서 저장"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        print(f"\n[DEBUG] 리뷰 생성 요청")
        print(f"[DEBUG] URL 파라미터: {dict(request.query_params)}")
        print(f"[DEBUG] Body 데이터: {request.data}")
        
        # 1. user_id 가져오기
        user_id = request.query_params.get('user_id') or request.data.get('user_id')
        print(f"[DEBUG] 받은 user_id: {user_id}")
        
        if not user_id:
            return Response(
                {"detail": "user_id가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 사용자 찾기
        try:
            user = User.objects.get(id=user_id)
            print(f"[SUCCESS] 사용자 찾음: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            print(f"[ERROR] user_id {user_id}에 해당하는 사용자 없음")
            return Response(
                {"detail": f"user_id {user_id}에 해당하는 사용자가 없습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. 시리얼라이저로 데이터 검증
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"[ERROR] 데이터 검증 실패: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"[SUCCESS] 데이터 검증 통과")
        
        # 4. user를 설정하고 저장
        serializer.save(
            user=user,
        )
        
        print(f"[SUCCESS] 리뷰 저장 완료!\n")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        리뷰 수정 (PUT/PATCH)
        본인이 작성한 리뷰만 수정 가능하도록 
        """
        review = self.get_object() 
        
        if request.user.is_authenticated and review.user != request.user:
            return Response(
                {"detail": "본인이 작성한 리뷰만 수정할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN 
            )

        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):  
        """
        리뷰 삭제 (DELETE)
        본인이 작성한 리뷰만 삭제 가능하도록 
        """
        review = self.get_object() 
        
        if request.user.is_authenticated and review.user != request.user:
            return Response(
                {"detail": "본인이 작성한 리뷰만 삭제할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN 
            )

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """현재 로그인한 사용자가 작성한 리뷰만 조회"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "로그인이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 현재 사용자가 작성한 리뷰만 필터링
        reviews = self.get_queryset().filter(user=request.user)
        # 여러 객체 한번에 직렬화 
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)