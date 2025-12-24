# Places API 명세서

`places` 앱에서 제공하는 REST API 엔드포인트 목록입니다.

## 1. 장소 관리 (CRUD)

| Method | Endpoint | 기능 설명 | 요청 파라미터 (Body/Query) | 비고 |
| :---: | :--- | :--- | :--- | :--- |
| **GET** | `/api/places/` | 장소 목록 조회 | `search`: 검색어 (선택)<br>`id`: 특정 장소 ID (선택) | 이름 유사도 검색 지원 |
| **POST** | `/api/places/` | 신규 장소 등록 | `id`: 카카오 장소 ID (필수)<br>`building_name`: 건물명<br>`latitude`: 위도<br>`longitude`: 경도<br>`wheelchair`: 휠체어 여부 (T/F/Null)<br>...기타 접근성 필드 | 건물명 누락 시 좌표로 자동 검색 |
| **GET** | `/api/places/<id>/` | 장소 상세 조회 | - | |
| **PATCH** | `/api/places/<id>/` | 장소 정보 수정 | `wheelchair`, `has_elevator`, `has_ramp`, `accessible_toilet` 중 수정할 필드 | 부분 수정 가능 |
| **DELETE** | `/api/places/<id>/` | 장소 삭제 | - | |

## 2. 검색 및 필터링

| Method | Endpoint | 기능 설명 | 요청 파라미터 (JSON Body) | 비고 |
| :---: | :--- | :--- | :--- | :--- |
| **POST** | `/api/places/filter/` | 지도 범위 내 필터링 검색 | `map_bounds`: {north, south, east, west}<br>`filters`: {wheelchair: true, ...}<br>`search_query`: 검색어 | 지도 이동/확대/축소 시 호출 |
| **GET** | `/api/places/kakao/search/` | 카카오 장소 검색 (프록시) | `query`: 검색어 (Query Param) | CORS 문제 해결용 서버 프록시 |

## 3. AI 추천

| Method | Endpoint | 기능 설명 | 요청 파라미터 (JSON Body) | 비고 |
| :---: | :--- | :--- | :--- | :--- |
| **POST** | `/api/places/ai-recommend/` | AI 기반 맞춤 장소 추천 | `map_bounds`: 지도 범위<br>`limit`: 추천 개수 (기본 5)<br>`filters`: 현재 적용된 필터 | Claude AI 연동<br>사용자 장애 유형 반영 |

## 4. 기타

| Method | Endpoint | 기능 설명 | 비고 |
| :---: | :--- | :--- | :--- |
| **GET** | `/api/places/test/` | 지도 테스트 페이지 | HTML 렌더링 (API 아님) |

---

### 💡 주요 데이터 구조 예시

**1. `map_bounds` (지도 범위)**
```json
{
    "north": 35.91,
    "south": 35.88,
    "east": 128.87,
    "west": 128.84
}
```

**2. `filters` (접근성 필터)**
```json
{
    "wheelchair": true,
    "has_elevator": false,
    "has_ramp": true,
    "accessible_toilet": null
}
```