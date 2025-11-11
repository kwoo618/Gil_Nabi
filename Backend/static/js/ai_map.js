
// AI 추천 & 필터링 지도 관리
class AIMapManager {
    constructor(mapInstance) {
        this.map = mapInstance;
        this.markers = [];
        this.infoWindows = [];
        this.currentUser = null;
    }
    
    // 현재 지도 범위 가져오기
    getMapBounds() {
        const bounds = this.map.getBounds();
        return {
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest()
        };
    }
    
    // AI 추천 장소 요청 및 표시
    async loadAIRecommendations() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('로그인이 필요합니다.');
            return;
        }
        
        try {
            const response = await fetch('/api/places/ai-recommend/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    map_bounds: this.getMapBounds(),
                    limit: 5
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.displayRecommendations(data.markers);
                this.currentUser = data.user_info;
            }
        } catch (error) {
            console.error('AI 추천 로드 실패:', error);
        }
    }
    
    // 추천 장소 마커 표시
    displayRecommendations(markers) {
        // 기존 마커 제거
        this.clearMarkers();
        
        markers.forEach((markerData, index) => {
            // 마커 생성 (점수별 색상)
            const markerColor = this.getMarkerColor(markerData.score);
            
            const marker = new kakao.maps.Marker({
                position: new kakao.maps.LatLng(
                    markerData.position.lat,
                    markerData.position.lng
                ),
                map: this.map,
                image: this.createMarkerImage(markerColor, index + 1)
            });
            
            // 정보창 생성
            const infoWindow = this.createInfoWindow(markerData);
            
            // 클릭 이벤트
            kakao.maps.event.addListener(marker, 'click', () => {
                // 다른 정보창 닫기
                this.closeAllInfoWindows();
                // 현재 정보창 열기
                infoWindow.open(this.map, marker);
            });
            
            this.markers.push(marker);
            this.infoWindows.push(infoWindow);
        });
    }
    
    // 마커 이미지 생성 (순위 표시)
    createMarkerImage(color, rank) {
        const imageSrc = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(`
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="50" viewBox="0 0 40 50">
                <path d="M20 0C9 0 0 9 0 20c0 11 20 30 20 30s20-19 20-30c0-11-9-20-20-20z" fill="${color}"/>
                <text x="20" y="25" text-anchor="middle" fill="white" font-size="16" font-weight="bold">${rank}</text>
            </svg>
        `)}`;
        
        const imageSize = new kakao.maps.Size(40, 50);
        const imageOption = {offset: new kakao.maps.Point(20, 50)};
        
        return new kakao.maps.MarkerImage(imageSrc, imageSize, imageOption);
    }
    
    // 점수별 마커 색상
    getMarkerColor(score) {
        if (score >= 80) return '#4CAF50';  // 초록 (우수)
        if (score >= 60) return '#FFC107';  // 노랑 (양호)
        return '#F44336';  // 빨강 (보통)
    }
    
    // 정보창 생성
    createInfoWindow(markerData) {
        const content = `
            <div style="padding: 15px; width: 280px; font-family: 'Noto Sans KR';">
                <h4 style="margin: 0 0 10px 0; color: #333;">
                    ${markerData.building_name}
                </h4>
                
                <div style="background: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <div style="font-size: 24px; font-weight: bold; color: ${this.getMarkerColor(markerData.score)};">
                        ★ ${markerData.score}점
                    </div>
                    <div style="font-size: 12px; color: #666;">
                        리뷰 ${markerData.review_count}개 기준
                    </div>
                </div>
                
                <div style="margin-bottom: 10px;">
                    <strong>접근성 정보:</strong>
                    <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 5px;">
                        ${markerData.accessibility.wheelchair ? 
                            '<span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">휠체어</span>' : ''}
                        ${markerData.accessibility.has_elevator ? 
                            '<span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">엘리베이터</span>' : ''}
                        ${markerData.accessibility.has_ramp ? 
                            '<span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">경사로</span>' : ''}
                        ${markerData.accessibility.accessible_toilet ? 
                            '<span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">장애인화장실</span>' : ''}
                    </div>
                </div>
                
                ${markerData.top_review ? `
                    <div style="border-top: 1px solid #ddd; padding-top: 10px;">
                        <strong>대표 리뷰:</strong>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            "${markerData.top_review.content}"
                            <span style="color: #FFC107;">★${markerData.top_review.rating}</span>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        return new kakao.maps.InfoWindow({
            content: content,
            removable: true
        });
    }
    
    // 필터링 적용
    async applyFilters(filters) {
        try {
            const response = await fetch('/api/places/filter/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filters: filters,
                    map_bounds: this.getMapBounds()
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.displayFilteredPlaces(data.markers);
            }
        } catch (error) {
            console.error('필터링 실패:', error);
        }
    }
    
    // 필터링된 장소 표시
    displayFilteredPlaces(markers) {
        this.clearMarkers();
        
        markers.forEach((markerData) => {
            const marker = new kakao.maps.Marker({
                position: new kakao.maps.LatLng(
                    markerData.position.lat,
                    markerData.position.lng
                ),
                map: this.map
            });
            
            const infoContent = `
                <div style="padding: 10px;">
                    <strong>${markerData.building_name}</strong><br>
                    <small>매칭: ${markerData.matching_filters.join(', ')}</small>
                </div>
            `;
            
            const infoWindow = new kakao.maps.InfoWindow({
                content: infoContent
            });
            
            kakao.maps.event.addListener(marker, 'click', () => {
                this.closeAllInfoWindows();
                infoWindow.open(this.map, marker);
            });
            
            this.markers.push(marker);
            this.infoWindows.push(infoWindow);
        });
    }
    
    // 마커 제거
    clearMarkers() {
        this.markers.forEach(marker => marker.setMap(null));
        this.markers = [];
        this.infoWindows = [];
    }
    
    // 모든 정보창 닫기
    closeAllInfoWindows() {
        this.infoWindows.forEach(infoWindow => infoWindow.close());
    }
}

// 지도 초기화 및 사용
document.addEventListener('DOMContentLoaded', function() {
    // 카카오맵 초기화
    const container = document.getElementById('map');
    const options = {
        center: new kakao.maps.LatLng(35.9, 128.85),
        level: 3
    };
    
    const map = new kakao.maps.Map(container, options);
    const aiMapManager = new AIMapManager(map);
    
    // AI 추천 버튼
    document.getElementById('ai-recommend-btn').addEventListener('click', () => {
        aiMapManager.loadAIRecommendations();
    });
    
    // 필터 체크박스들
    document.getElementById('apply-filter-btn').addEventListener('click', () => {
        const filters = {
            has_ramp: document.getElementById('filter-ramp').checked,
            wheelchair: document.getElementById('filter-wheelchair').checked,
            accessible_toilet: document.getElementById('filter-toilet').checked,
            has_elevator: document.getElementById('filter-elevator').checked
        };
        aiMapManager.applyFilters(filters);
    });
    
    // 지도 이동 시 자동 갱신 (선택사항)
    kakao.maps.event.addListener(map, 'idle', () => {
        // 지도 이동/줌 완료 시 재검색
        if (document.getElementById('auto-refresh').checked) {
            aiMapManager.loadAIRecommendations();
        }
    });
});