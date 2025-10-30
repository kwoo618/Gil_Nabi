''' 
==================================================================================
1. UserManager: 사용자를 생성/관리하는 헬퍼 클래스
2. User: 실제 사용자 정보를 담는 모델 (DB 테이블)
==================================================================================

models.py의 목적 
- 카카오/구글 소셜 로그인으로 가입한 사용자 정보를 DB에 저장
- 사용자 정보 관리

주요 구성:
1. UserManager: 사용자를 생성/관리하는 헬퍼 클래스
2. User: 실제 사용자 정보를 담는 모델 (DB 테이블)
''' 

# ==================== Import 부분 ====================================================
from django.db import models # Django가 제공하는 기본 모델 기능 가져오기

# 사용자 인증 시스템 관련 클래스들
from django.contrib.auth.models import (
    AbstractBaseUser,                   # 기본 로그인 기능 
    BaseUserManager,                    # 사용자 생성/관리 기능
    PermissionsMixin,                   # 권한/그룹 기능, superuser 기능 제공
    Group,                              # 권한 그룹 (ex: 관리자, 일반회원)
    Permission                          # 세부 권한 (ex: 게시글 작성, 삭제 권한)
)

# =================== UserManeger =====================================================

# 사용자 관리자 클래스 정의
class UserManager(BaseUserManager): # User 객체를 DB에 생성/관리하는 클래스

    # 일반 사용자 생성
        # social_id = 소셜 로그인에서 제공하는 고유 ID
        # provider = 소셜 로그인 제공자 (kakao, naver) [Kakao, Naver 등 로그인 서비스 이름]
        # username = 앱 내에서 표시할 닉네임
        # extra_fields = 프로필 이미지 등 추가 정보 

    def create_user(self, social_id, provider, username, password=None, **extra_fields): 
        if not social_id:                                   # social_id 는 필수값이라 없으면 안됨.
            raise ValueError("Social ID가 필요합니다.")       # 없으면 필요하다고 출력
        user = self.model(
            social_id=social_id, 
            provider=provider, 
            username=username, 
            **extra_fields) # User 모델 객체 생성
        user.save(using=self._db) # DB에 사용자 저장

        if password:
            user.set_password(password)  # ✅ 있어야 함!
        else:
            user.set_unusable_password()
            
        return user
        
        # 관리자 생성 
        # 강제로 is_staff=True, is_superuser=True 설정
    def create_superuser(self, social_id, provider, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True) # Django 관리 사이트(Admin)에 로그인할 수 있는 권한
        extra_fields.setdefault('is_superuser', True) # 모든 권한(읽기/쓰기/삭제 등)을 가진 최고 관리자 계정
        extra_fields.setdefault('is_active', True) 

        # 권한 검증 추가
        if extra_fields.get('is_staff') is not True:
            raise ValueError('슈퍼유저는 is_staff=True여야 합니다.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('슈퍼유저는 is_superuser=True여야 합니다.')

        # 관리자는 비밀번호 필수!
        if not password:
            raise ValueError('관리자 계정은 비밀번호가 필요합니다.')

        return self.create_user(social_id, provider, username, password, **extra_fields)

# ================== User 모델 클래스 ======================================
# 사용자 모델 정의
class User(AbstractBaseUser, PermissionsMixin): # AbstractBaseUser: 기본 로그인 기능, PermissionsMixin: 권한 시스템 제공
    SOCIAL_PROVIDERS = ( # 소셜 로그인 제공자 선택지 (DB 컬럼에서 choices로 제한 가능)
        ('kakao', 'Kakao'), 
        ('google', 'Google'),
    )
    
    # ============== 필수 입력 필드 ========================================
    social_id = models.CharField(
        max_length=255,        # 최대 255자 (카카오/구글 ID는 보통 10~20자)
        unique=True,           # 중복 불가! DB에 UNIQUE 제약조건 생성
        verbose_name='소셜 고유 ID',
        help_text='카카오/구글에서 제공하는 사용자 고유 번호'
    )

    provider = models.CharField(
        max_length=20,
        choices=SOCIAL_PROVIDERS,  # 'kakao' 또는 'google'만 허용
        verbose_name='로그인 제공자',
        help_text='카카오 또는 구글'
    )

    username = models.CharField(
        max_length=50,
        verbose_name='사용자 이름',
        help_text='앱에서 표시될 이름'
    )

    profile_image = models.URLField(
        blank=True,            # 폼에서 비워도 됨 (필수 아님)
        null=True,             # DB에 NULL 허용
        verbose_name='프로필 이미지',
        help_text='카카오/구글 프로필 사진 URL'
    )
    
    # ============== 장애인 앱 선택 필드 ===================

    nickname = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='닉네임',
        help_text='사용자가 직접 설정한 닉네임'
    )
    # 장애 유형 선택지
    DISABILITY_CHOICES = [
        ('physical', '지체장애'),
        ('visual', '시각장애'),
        ('hearing', '청각장애'),
        ('language', '언어장애'),
    ]
    disability_type = models.CharField(
        max_length=20, 
        choices=DISABILITY_CHOICES, 
        blank=True, 
        null=True
    )
    
    has_wheelchair = models.BooleanField(
        default=False,         # 기본값: 휠체어 없음
        null=True,             # 정보 입력 안 함 = NULL
    )

    is_profile_complete = models.BooleanField(
        default=False,
        verbose_name='프로필 완성 여부',
        help_text='추가 정보 입력 완료 여부'
    )

    # ================= Django 기본 권한 필드 ========================================
    is_active = models.BooleanField(default=True) # 활성 사용자 여부    
    is_staff = models.BooleanField(default=False) # 관리자 여부

    # ================= 권한 시스템 =====================================
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # 기본 auth.User와 충돌 방지
        blank=True,
    )

    user_permissions = models.ManyToManyField(  
        Permission,
        related_name='custom_user_permissions_set',  # 기본 auth.User와 충돌 방지
        blank=True,
    )

    # ================= UserManager 연결 =========================================
    objects = UserManager() # 사용자 관리자 객체

    # ============ Django 인증 시스템 설정 ============
    USERNAME_FIELD = 'social_id' # 소셜 로그인 고유 ID로 로그인
    REQUIRED_FIELDS = ['provider', 'username'] # 관리자 계정 생성 시 필수 입력 필드
 
    # ============ 문자열 표현 메서드 ============
    def __str__(self):
        return f"{self.provider}:{self.username}" # 객체 문자열 표현 (예: "kakao: 권동철")

    # ============ 헬퍼 메서드 (유틸리티 함수) ============
    def get_full_name(self):
        return self.nickname if self.nickname else self.username 
    def get_short_name(self):
        return self.username
    def has_completed_profile(self):
        return self.is_profile_complete
