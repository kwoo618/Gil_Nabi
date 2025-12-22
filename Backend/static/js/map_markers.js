// map_markers.js - 마커 관리
const mapMarkers = {
    currentMarker: null,
    
    setCurrentMarker: function(marker) {
        this.currentMarker = marker;
    },
    
    getCurrentMarker: function() {
        return this.currentMarker;
    },
    
    clearAll: function() {
        mapMain.markers.forEach(marker => {
            if (marker.setMap) marker.setMap(null);
        });
        mapMain.markers = [];
        this.currentMarker = null;
        
        if (mapMain.infowindow) {
            mapMain.infowindow.close();
        }
    },
    
    addClickMarker: function(place) {
        this.clearAll();
        
        const position = new kakao.maps.LatLng(
            place.latitude || place.y,
            place.longitude || place.x
        );
        
        const marker = new kakao.maps.Marker({
            position: position,
            map: mapMain.map
        });
        
        this.currentMarker = marker;
        mapMain.markers.push(marker);
        
        // 클릭 이벤트
        kakao.maps.event.addListener(marker, 'click', function() {
            mapInfo.showPlaceInfo(place, marker);
        });
        
        return marker;
    },
    
    addSearchMarker: function(place) {
        const position = new kakao.maps.LatLng(
            place.position.lat,
            place.position.lng
        );
        
        const marker = new kakao.maps.Marker({
            position: position,
            map: mapMain.map
        });
        
        kakao.maps.event.addListener(marker, 'click', function() {
            const content = `
                <div style="padding:10px;">
                    <strong>${place.building_name}</strong><br>
                    <small>${place.matching_filters.join(', ')}</small>
                </div>
            `;
            mapMain.infowindow.setContent(content);
            mapMain.infowindow.open(mapMain.map, marker);
        });
        
        mapMain.markers.push(marker);
    },
    
    addFilterMarker: function(place) {
        const position = new kakao.maps.LatLng(
            place.position.lat,
            place.position.lng
        );
        
        const marker = new kakao.maps.Marker({
            position: position,
            map: mapMain.map
        });
        
        kakao.maps.event.addListener(marker, 'click', function() {
            const content = `
                <div style="padding:10px;">
                    <strong>${place.building_name}</strong><br>
                    <small>접근성: ${place.matching_filters.join(', ')}</small>
                </div>
            `;
            mapMain.infowindow.setContent(content);
            mapMain.infowindow.open(mapMain.map, marker);
        });
        
        mapMain.markers.push(marker);
    },
    
    addAIMarker: function(place, rank) {
        const position = new kakao.maps.LatLng(
            place.position.lat,
            place.position.lng
        );
        
        // 순위별 마커 이미지 변경 (선택사항, 여기선 기본 마커 사용)
        // const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7'];
        // const color = colors[rank - 1] || '#95a5a6';
        
        // ✨ 오버레이 생성 코드 삭제됨
        
        // 마커 생성
        const marker = new kakao.maps.Marker({
            position: position,
            map: mapMain.map
        });
        
        kakao.maps.event.addListener(marker, 'click', function() {
            const content = `
                <div style="padding:15px;">
                    <h4>🏆 AI 추천 ${rank}위</h4>
                    <strong>${place.building_name}</strong><br>
                    <div style="margin:10px 0;">
                        ⭐ ${place.score}점 | 리뷰 ${place.review_count}개
                    </div>
                    <div style="font-size:12px;">
                        ${place.accessibility.wheelchair ? '✅' : '❌'} 휠체어<br>
                        ${place.accessibility.has_elevator ? '✅' : '❌'} 엘리베이터<br>
                        ${place.accessibility.has_ramp ? '✅' : '❌'} 경사로<br>
                        ${place.accessibility.accessible_toilet ? '✅' : '❌'} 화장실
                    </div>
                    <div style="margin-top:5px; font-size:11px; color:#666;">
                        ${place.ai_reason}
                    </div>
                </div>
            `;
            mapMain.infowindow.setContent(content);
            mapMain.infowindow.open(mapMain.map, marker);
        });
        
        mapMain.markers.push(marker);
    }
};