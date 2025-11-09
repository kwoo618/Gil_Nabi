# reviews/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg, Count

from .models import Review 

from .serializers import ReviewSerializer, ReviewListSerializer, ReviewCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """리뷰에 대한 모든 CRUD 작업을 처리하는 ViewSet"""
    
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    def get_permissions(self):
        """액션별로 권한 다르게 설정"""
        if self.action in ['list', 'retrieve', 'by_place']:
            # 목록 조회, 상세 조회는 누구나 가능
            return [AllowAny()]
        else:
            # 작성, 수정, 삭제는 인증 필요
            return [IsAuthenticated()]

    def get_serializer_class(self):
        """목록 조회 시 간단한 시리얼라이저 사용"""
        if self.action == 'list':
            return ReviewListSerializer
        return ReviewSerializer

    def get_queryset(self):
        """필터링된 쿼리셋 반환"""
        queryset = Review.objects.select_related('user')
        
        # 특정 장소의 리뷰만 조회
        place_id = self.request.query_params.get('place_id')
        if place_id:
            queryset = queryset.filter(place_id=place_id)

        # 장애 유형별 필터
        disability_type = self.request.query_params.get('disability_type')
        if disability_type:
            queryset = queryset.filter(disability_type=disability_type)

        # 별점 필터
        rating = self.request.query_params.get('rating')
        if rating: 
            queryset = queryset.filter(rating=rating)

        return queryset
    
    def create(self, request, *args, **kwargs):
        """리뷰 생성"""
        print(f"\n[DEBUG] 리뷰 생성 요청")
        print(f"[DEBUG] 사용자: {request.user} (ID: {request.user.id})")
        print(f"[DEBUG] Body 데이터: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"[ERROR] 데이터 검증 실패: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"[SUCCESS] 데이터 검증 통과")
        
        # 현재 로그인한 사용자로 저장
        serializer.save(user=request.user)
        
        print(f"[SUCCESS] 리뷰 저장 완료!\n")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """리뷰 수정 - 본인이 작성한 리뷰만 수정 가능"""
        review = self.get_object()
        
        if review.user != request.user:
            return Response(
                {"detail": "본인이 작성한 리뷰만 수정할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """리뷰 삭제 - 본인이 작성한 리뷰만 삭제 가능"""
        review = self.get_object()

        # 익명 사용자 체크 추가
        if not request.user.is_authenticated:
            return Response(
                {"detail": "로그인이 필요합니다."},
            status=status.HTTP_401_UNAUTHORIZED
        )
        
        if review.user != request.user:
            return Response(
                {"detail": "본인이 작성한 리뷰만 삭제할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        """현재 로그인한 사용자가 작성한 리뷰만 조회"""
        reviews = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def by_place(self, request):
        """특정 장소의 모든 리뷰 + 통계 조회"""
        place_id = request.query_params.get('place_id')
        
        if not place_id:
            return Response(
                {"error": "place_id가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = self.get_queryset().filter(place_id=place_id)
        serializer = ReviewListSerializer(reviews, many=True)
        
        # 통계 정보
        stats = reviews.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating')
        )
        
        # 장애 유형별 리뷰 수
        disability_stats = reviews.values('disability_type').annotate(
            count=Count('id')
        )
        
        return Response({
            'place_id': place_id,
            'reviews': serializer.data,
            'stats': {
                'total_reviews': stats['total_reviews'] or 0,
                'average_rating': round(stats['average_rating'] or 0, 1),
                'by_disability_type': list(disability_stats)
            }
        })