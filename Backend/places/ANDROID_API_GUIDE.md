# Android App Integration Guide (Places API)

안드로이드 앱 개발 파트너를 위한 `places` API 연동 가이드입니다.
기존 웹 프론트엔드(JS) 로직을 안드로이드(Kotlin/Retrofit) 환경에 맞게 정리하였습니다.

## 1. Data Models (Kotlin DTO)

API 통신에 사용되는 주요 데이터 모델입니다.

### 1.1 MapBounds (지도 범위)
지도 이동/축소/확대 시 현재 보고 있는 영역의 좌표를 전달합니다.
```kotlin
data class MapBounds(
    val north: Double, // 북위
    val south: Double, // 남위
    val east: Double,  // 동경
    val west: Double   // 서경
)
```

### 1.2 PlaceFilters (접근성 필터)
사용자가 선택한 장애인 편의시설 필터 정보입니다.
```kotlin
data class PlaceFilters(
    val wheelchair: Boolean? = null,      // 휠체어 접근 가능
    val has_elevator: Boolean? = null,    // 엘리베이터 유무
    val has_ramp: Boolean? = null,        // 경사로 유무
    val accessible_toilet: Boolean? = null // 장애인 화장실 유무
)
```

### 1.3 Requests (요청 바디)

**FilterRequest (필터링 검색)**
```kotlin
data class FilterRequest(
    val map_bounds: MapBounds,
    val filters: PlaceFilters,
    val search_query: String? = null
)
```

**AIRecommendRequest (AI 추천)**
```kotlin
data class AIRecommendRequest(
    val map_bounds: MapBounds,
    val filters: PlaceFilters,
    val limit: Int = 5
)
```

---

## 2. API Interface (Retrofit Specification)

Retrofit 인터페이스 정의 예시입니다.
Base URL: `/api/places/`

### 2.1 장소 관리 (CRUD)
```kotlin
interface PlaceService {
    // 장소 목록 조회
    @GET(".")
    suspend fun getPlaces(
        @Query("search") search: String? = null,
        @Query("id") id: String? = null
    ): Response<List<PlaceResponse>>

    // 신규 장소 등록
    @POST(".")
    suspend fun createPlace(@Body place: PlaceRequest): Response<PlaceResponse>

    // 장소 상세 조회
    @GET("{id}/")
    suspend fun getPlaceDetail(@Path("id") id: String): Response<PlaceResponse>

    // 장소 정보 수정 (PATCH)
    // 일반 회원: 202 Accepted (수정 요청 생성)
    // 관리자: 200 OK (즉시 수정)
    @PATCH("{id}/")
    suspend fun updatePlace(
        @Path("id") id: String,
        @Body updates: Map<String, Any?> // 예: {"wheelchair": true}
    ): Response<Void>
}
```

### 2.2 검색 및 AI 기능
```kotlin
interface SearchService {
    // 지도 범위 내 필터링 검색
    @POST("filter/")
    suspend fun filterPlaces(@Body request: FilterRequest): Response<List<PlaceResponse>>

    // 카카오 장소 검색 (프록시)
    @GET("kakao/search/")
    suspend fun searchKakao(@Query("query") query: String): Response<KakaoSearchResponse>

    // AI 맞춤 장소 추천
    @POST("ai-recommend/")
    suspend fun getAIRecommendations(@Body request: AIRecommendRequest): Response<List<PlaceResponse>>

    // 내 수정 요청 목록 (Token 필요)
    @GET("my-requests/")
    suspend fun getMyRequests(): Response<List<RequestResponse>>
}
```