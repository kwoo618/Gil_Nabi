# Server Deployment Guide (Docker & AWS)

안드로이드 앱 출시를 위한 백엔드 서버(Django) 배포 가이드입니다.
로컬 개발 환경에서 AWS 프로덕션 환경으로 이전하기 위해 필요한 절차를 정리했습니다.

## 1. 프로젝트 루트 설정 (파일 생성)

`manage.py`가 있는 최상위 폴더(`Backend/`)에 다음 파일들을 생성해야 합니다.

### 1.1 requirements.txt 업데이트
배포 환경에서는 `gunicorn`이 필수입니다.
```bash
pip install gunicorn
pip freeze > requirements.txt
```

### 1.2 Dockerfile
서버 이미지를 빌드하기 위한 명세서입니다.
```dockerfile
# Python 3.9 ~ 3.11 중 사용 중인 버전 선택
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 환경 변수 설정 (Python 버퍼링 비활성화 등)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 의존성 설치
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 소스 코드 복사
COPY . /app/

# Gunicorn 실행 (8000번 포트)
# config.wsgi:application 부분은 프로젝트명에 따라 수정 필요 (예: Gil_NaBi.wsgi:application)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

### 1.3 docker-compose.yml
컨테이너 실행을 관리합니다.
```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 config.wsgi:application
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
```

---

## 2. Django 설정 변경 (settings.py)

배포 전 `settings.py`에서 보안 관련 설정을 반드시 변경해야 합니다.

1.  **DEBUG 모드 끄기**
    ```python
    DEBUG = False
    ```
2.  **ALLOWED_HOSTS 설정**
    AWS EC2의 퍼블릭 IP 또는 도메인을 추가해야 합니다.
    ```python
    ALLOWED_HOSTS = ['3.12.34.56', 'your-domain.com', 'localhost']
    ```
3.  **SECRET_KEY 분리**
    소스코드에 노출되지 않도록 `.env` 파일이나 환경변수로 관리하세요.

---

## 3. AWS EC2 배포 절차

1.  **EC2 인스턴스 생성**
    *   OS: Ubuntu 22.04 LTS 추천
    *   보안 그룹(Security Group):
        *   SSH (22): 내 IP에서만 허용
        *   HTTP (80) / HTTPS (443): 전체 허용 (0.0.0.0/0)
        *   Custom TCP (8000): 테스트용 (나중에 Nginx 연동 시 80으로 통합)

2.  **Docker 설치 (EC2 접속 후)**
    ```bash
    sudo apt update
    sudo apt install docker.io docker-compose -y
    sudo usermod -aG docker $USER
    # (재접속 필요)
    ```

3.  **코드 배포 및 실행**
    *   Github 등을 통해 코드를 EC2로 `git clone` 합니다.
    *   프로젝트 폴더로 이동하여 실행:
        ```bash
        docker-compose up -d --build
        ```

---

## 4. 안드로이드 앱 수정 (Retrofit)

서버 배포가 완료되면 안드로이드 앱이 바라보는 주소를 변경해야 합니다.

**Retrofit Client 설정 파일:**
```kotlin
// 기존 (로컬)
// private const val BASE_URL = "http://10.0.2.2:8000/api/places/"

// 변경 (AWS 배포 후)
private const val BASE_URL = "http://[AWS_EC2_PUBLIC_IP]:8000/api/places/"
```

> **주의:** 안드로이드 9(Pie) 이상부터는 기본적으로 `http` 통신을 차단합니다.
> `AndroidManifest.xml`에 `android:usesCleartextTraffic="true"`를 추가하거나, AWS 로드밸런서 등을 통해 `https`를 적용해야 합니다.