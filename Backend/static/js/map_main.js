// map_main.js - 메인 컨트롤러
class MapController {
    constructor() {
        // 상태 변수
        this.map = null;
        this.markers = [];
        this.infowindow = null;
        this.geocoder = null;
        this.places = null;
        this.currentPlace = null;
        this.currentFilters = {
            wheelchair: false,
            has_elevator: false,
            has_ramp: false,
            accessible_toilet: false
        };
    }

    // 초기화
    init() {
        kakao.maps.load(() => {
            const container = document.getElementById('map');
            const options = {
                center: new kakao.maps.LatLng(35.8959, 128.8502),
                level: 4
            };
            
            this.map = new kakao.maps.Map(container, options);
            this.geocoder = new kakao.maps.services.Geocoder();
            this.places = new kakao.maps.services.Places();
            this.infowindow = new kakao.maps.InfoWindow({zIndex: 1});
            
            // 지도 클릭 시 정보창 닫기 및 마커 제거
            kakao.maps.event.addListener(this.map, 'click', function(mouseEvent) {
                // 1. 기존 정보창 닫기
                if (mapInfo.currentInfoWindow) {
                    mapInfo.closeInfo();
                }
                            
                // 2. 기존 마커들 모두 제거
                mapMarkers.clearAll();
                            
                // 3. 지도 클릭 처리 (새로운 장소 검색 등)
                mapClick.handleMapClick(mouseEvent.latLng);
            });
            
            // 모듈 초기화
            mapFilter.init();
            this.loadInitialData();
            
            console.log('✅ 지도 초기화 완료');
        });
    }
    
    // 초기 데이터 로드
    async loadInitialData() {
        try {
            const response = await fetch('/api/places/');
            const places = await response.json();
            console.log(`📍 ${places.length}개 장소 로드`);
        } catch (error) {
            console.error('초기 데이터 로드 오류:', error);
        }
    }
    
    // 전체 초기화
    resetAll() {
        mapMarkers.clearAll();
        mapFilter.clearFilters();
        document.getElementById('search-input').value = '';
        mapUI.showMessage('초기화되었습니다');
        if (this.infowindow) this.infowindow.close();
    }
    
    // 지도 범위 가져오기
    getMapBounds() {
        const bounds = this.map.getBounds();
        const sw = bounds.getSouthWest();
        const ne = bounds.getNorthEast();
        
        return {
            north: ne.getLat(),
            south: sw.getLat(),
            east: ne.getLng(),
            west: sw.getLng()
        };
    }
    
    // 필터 적용 여부 확인
    hasActiveFilters() {
        return Object.values(this.currentFilters).some(v => v);
    }
}

// 인스턴스 생성 (기존 코드와의 호환성을 위해 mapMain 이름 유지)
const mapMain = new MapController();

// 페이지 로드 시 초기화
window.onload = function() {
    mapMain.init();
};