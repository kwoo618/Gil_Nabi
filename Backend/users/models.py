# 데이터베이스 설계도
# User(사용자) 정보를 어떻게 저장할지 결정
# 소셜 로그인을 해야됨 (카카오, 구글)

# User 테이블 구조 
# social_id: 카카오/구글에서 받은 고유 ID (중복 불가)
# provider: 'kakao' 또는 'google'
# username: 앱에서 표시할 닉네임
# profile_image: 프로필 사진 URL
# is_active: 활성 사용자 여부
# is_staff: 관리자 권한 여부


from django.db import models # Django 모델과 권한 관련 클래스 불러옴
from django.contrib.auth.models import (
    AbstractBaseUser, # 로그인 기능 , 소셜 로그인만 사용할 때도 권한 시스템과 호환 가능
    BaseUserManager, # 사용자 생성/관리 기능, 사용자 생성 함수(create_user, create_superuser)를 만들 때 사용
    PermissionsMixin, # 권한 그룹, superuser 기능 제공
    Group, # Django에서 권한 그룹을 나타내는 모델, ex) 관리자, 회원, 운영자 같은 그룹.
    Permission # Django의 권한(permission) 모델
)

# 사용자 관리자 클래스 정의
class UserManager(BaseUserManager): # User 객체를 DB에 생성/관리하는 클래스

    # 일반 사용자 생성
        # social_id = 소셜 로그인에서 제공하는 고유 ID
        # provider = 소셜 로그인 제공자 (kakao, naver) [Kakao, Naver 등 로그인 서비스 이름]
        # username = 앱 내에서 표시할 닉네임
        # extra_fields = 프로필 이미지 등 추가 정보 

    def create_user(self, social_id, provider, username, **extra_fields): 
        if not social_id:
            raise ValueError("Social ID가 필요합니다.")
        user = self.model(social_id=social_id, provider=provider, username=username, **extra_fields) # User 모델 객체 생성
        user.save(using=self._db) # DB에 사용자 저장
        return user
        
        # 관리자 생성 
            # 강제로 is_staff=True, is_superuser=True 설정
    def create_superuser(self, social_id, provider, username, **extra_fields):
        extra_fields.setdefault('is_staff', True) # Django 관리 사이트(Admin)에 로그인할 수 있는 권한
        extra_fields.setdefault('is_superuser', True) # 모든 권한(읽기/쓰기/삭제 등)을 가진 최고 관리자 계정
        
        # create_user를 직접 호출하지 않고, 모델을 직접 생성
        # 이렇게 해야 is_staff, is_superuser 값이 올바르게 저장됨
        user = self.model(
            social_id=social_id,
            provider=provider,
            username=username,
            **extra_fields
        )
        user.save(using=self._db)
        return user


# 사용자 모델 정의
class User(AbstractBaseUser, PermissionsMixin): # AbstractBaseUser + PermissionsMixin 상속 → Django 인증/권한 기능 사용 가능
    SOCIAL_PROVIDERS = ( # 소셜 로그인 제공자 선택지 (DB 컬럼에서 choices로 제한 가능)
        ('kakao', 'Kakao'), 
        ('google', 'Google'),
    )
    
    social_id = models.CharField(max_length=255, unique=True) # 소셜 로그인 고유 ID (중복 불가 (unique=True))
    provider = models.CharField(max_length=20, choices=SOCIAL_PROVIDERS) # 어떤 소셜 로그인인지 저장
    username = models.CharField(max_length=50) # 앱 내 표시 닉네임 
    profile_image = models.URLField(blank=True, null=True) # 프로필 이미지, upload_to='profiles/': 업로드 경로
    #  "blank=True": 폼/Serializer에서 값이 없어도 허용. 즉, 사용자 등록 시 프로필 이미지 없이 가입 가능
    #  "null=True": DB에서 NULL 값 허용. 즉, 사용자 등록 시 프로필 이미지가 없어도 가입 가능

    nickname = models.CharField(max_length=50, blank=True, null=True)
    
    DISABILITY_CHOICES = [
        ('physical', '지체장애'),
        ('visual', '시각장애'),
        ('hearing', '청각장애'),
        ('other', '기타'),
    ]
    disability_type = models.CharField(
        max_length=20, 
        choices=DISABILITY_CHOICES, 
        blank=True, 
        null=True
    )
    
    has_wheelchair = models.BooleanField(default=False, null=True)
    is_profile_complete = models.BooleanField(default=False)

    # Django 권한용
    is_active = models.BooleanField(default=True) # 활성 사용자 여부    
    is_staff = models.BooleanField(default=False) # 관리자 여부

    # 충돌 방지용 related_name
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # 기본 auth.User와 충돌 방지
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(  
        Permission,
        related_name='custom_user_permissions_set',  # 기본 auth.User와 충돌 방지
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = UserManager() # 사용자 관리자 객체

    # 로그인 시 사용하는 필드 
    USERNAME_FIELD = 'social_id' # 소셜 로그인 고유 ID로 로그인
    REQUIRED_FIELDS = ['provider', 'username'] # 관리자 계정 생성 시 필수 입력 필드
 
    def __str__(self):
        return f"{self.provider}:{self.username}" # 객체 문자열 표현 (예: "kakao: 권동철")
