// static/js/map_markers.js - 마커 관리 모듈
class MapMarkerController {
    constructor() {
        this.currentMarker = null;
    }

    // 모든 마커 지우기
    clearAll() {
        if (mapMain.markers) {
            mapMain.markers.forEach(marker => marker.setMap(null));
            mapMain.markers = [];
        }
        // 현재 선택된 마커(클릭 마커)도 제거
        if (this.currentMarker) {
            this.currentMarker.setMap(null);
            this.currentMarker = null;
        }
    }

    // 현재 선택된 마커 설정 (정보창 띄울 때 사용)
    setCurrentMarker(marker) {
        this.currentMarker = marker;
    }

    getCurrentMarker() {
        return this.currentMarker;
    }

    // 클릭한 위치에 마커 추가
    addClickMarker(place) {
        const position = new kakao.maps.LatLng(place.latitude, place.longitude);
        const marker = new kakao.maps.Marker({
            position: position,
            map: mapMain.map
        });
        
        this.setCurrentMarker(marker);
        return marker;
    }

    // 필터링 결과 마커 추가
    addFilterMarker(place) {
        const position = new kakao.maps.LatLng(place.location.latitude, place.location.longitude);
        const marker = new kakao.maps.Marker({
            position: position,
            map: mapMain.map,
            title: place.building_name
        });

        // 클릭 이벤트 연결
        kakao.maps.event.addListener(marker, 'click', () => {
            mapInfo.showPlaceInfo(place, marker);
        });

        mapMain.markers.push(marker);
        return marker;
    }

    // AI 추천 마커 추가 (순위 표시 등 커스텀 가능)
    addAIMarker(place, rank) {
        const position = new kakao.maps.LatLng(place.position.lat, place.position.lng);
        
        // 기본 마커 사용 (추후 이미지 마커로 변경 가능)
        const marker = new kakao.maps.Marker({
            position: position,
            map: mapMain.map,
            title: `${rank}위. ${place.building_name}`
        });

        // 클릭 이벤트 연결
        kakao.maps.event.addListener(marker, 'click', () => {
            mapInfo.showPlaceInfo(place, marker);
        });

        mapMain.markers.push(marker);
        return marker;
    }
}

const mapMarkers = new MapMarkerController();