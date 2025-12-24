# Places 앱 기능 명세서

이 문서는 `places` 앱 내의 주요 파일과 함수들의 역할을 정리한 문서입니다.

## 1. models.py (데이터 모델)
* **`class Accessibility`**: 장소 정보를 저장하는 메인 모델입니다.
    * `id`: 카카오맵 장소 ID (Primary Key)
    * `building_name`: 건물/장소 이름
    * `latitude`, `longitude`: 위도, 경도 좌표
    * `wheelchair`, `has_elevator`, `has_ramp`, `accessible_toilet`: 접근성 정보 (True/False/None)

## 2. views.py (API 뷰)
* **`def test_page(request)`**: `map.html` 템플릿을 렌더링하여 지도를 보여줍니다.
* **`class PlaceListCreate`**: 장소 목록 조회 및 생성을 담당합니다.
    * `get_queryset()`: 검색어(이름)나 ID로 장소를 필터링하여 조회합니다.
    * `create()`: 새 장소를 저장합니다. 건물명이 없으면 `utils.py`를 통해 이름을 찾습니다.
* **`class PlaceRetrieveUpdateDestroy`**: 특정 장소의 상세 조회, 수정, 삭제를 담당합니다.
    * `patch()`: 장소의 접근성 정보를 부분 수정합니다.
* **`class FilterPlacesView`**: 필터링된 장소 목록을 반환합니다.
    * `post()`: 지도 범위와 필터 조건(휠체어 등)을 받아 검색 결과를 반환합니다.
* **`class KakaoSearchProxy`**: 카카오 로컬 API를 서버에서 대신 호출합니다 (CORS 방지).
* **`class AIRecommendView`**: AI 추천 기능을 처리합니다.
    * `post()`: 사용자 정보와 현재 지도 화면을 기반으로 추천 장소를 반환합니다.

## 3. ai_recommendation.py (AI 로직)
* **`class AIRecommendationSystem`**: Claude AI 연동 로직을 캡슐화한 클래스입니다.
    * `get_ai_recommendations()`: 추천 프로세스 전체를 조율합니다 (후보 선정 -> 리뷰 수집 -> AI 분석).
    * `_ask_claude()`: 실제 Claude API에 프롬프트를 보내고 응답을 파싱합니다.
    * `_fallback_result()`: AI 호출 실패 시 평점 순으로 대체 결과를 반환합니다.

## 4. accessibility_filter.py (필터 로직)
* **`class AccessibilityFilter`**: 복잡한 필터링 쿼리를 관리합니다.
    * `get_queryset()`: 지도 범위, 필터, 검색어를 조합하여 DB QuerySet을 생성합니다.
    * `get_filtered_places_with_details()`: QuerySet 결과를 프론트엔드용 JSON 형식으로 변환합니다.

## 5. serializers.py (데이터 변환)
* **`class AccessibilitySerializer`**: `Accessibility` 모델을 JSON으로 변환합니다.
* **`class AIRecommendationSerializer`**: AI 추천 결과를 클라이언트에 보낼 때 사용하는 포맷입니다.

## 6. utils.py (유틸리티)
* **`def get_kakao_building_name(lat, lng)`**: 좌표(위도, 경도)를 주면 카카오 API를 사용해 건물 이름을 찾아줍니다.

## 7. urls.py (URL 설정)
* API 엔드포인트와 뷰를 연결합니다. (`/api/places/`, `/api/places/filter/` 등)

## 8. admin.py (관리자 페이지)
* **`class AccessibilityAdmin`**: Django 관리자 페이지에서 장소 데이터를 쉽게 관리할 수 있도록 설정합니다.

## 9. tests.py (테스트)
* **`class PlacesAPITest`**: API 기능이 정상 작동하는지 검증합니다.
    * `test_get_place_list()`: 목록 조회 테스트
    * `test_create_place()`: 장소 생성 테스트
    * `test_filter_places()`: 필터링 테스트
    * `test_ai_recommendation()`: AI 추천 테스트 (Mock 사용)