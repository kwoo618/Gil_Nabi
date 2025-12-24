// static/js/map_ai.js
class MapAIController {
    async getRecommendation() {
        // 로그인 확인 로직 제거됨 (비회원도 가능하게)

        mapUI.showLoading('AI 분석 중...');
        
        try {
            // 현재 지도 중심 좌표 (사용자 위치로 간주)
            const center = mapMain.map.getCenter();
            
            const params = {
                map_bounds: mapMain.getMapBounds(),
                user_location: {
                    latitude: center.getLat(),
                    longitude: center.getLng()
                },
                limit: 5
            };
            
            // ✨ 필터가 활성화되어 있으면 파라미터에 추가
            if (mapMain.hasActiveFilters()) {
                params.filters = mapMain.currentFilters;
            }
            
            const response = await fetch('/api/places/ai-recommend/', {
                method: 'POST',
                headers: {
                    // Authorization 헤더 제거됨
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });
            
            const data = await response.json();
            console.log('AI 추천 결과:', data);
            
            if (data.success && data.markers && data.markers.length > 0) {
                mapMarkers.clearAll();
                
                // AI 마커 표시 (순위 인자 전달하지만 마커 JS에서 무시함)
                data.markers.forEach((place, index) => {
                    mapMarkers.addAIMarker(place, index + 1);
                });
                
                // 결과 목록 표시 (사이드바에는 순위 표시 유지하거나 제거 가능)
                const userInfo = data.user_info || { disability_type: '비회원', has_wheelchair: false };
                mapUI.showAIResults(data.markers, userInfo);
                
                // 첫 번째 추천 장소로 이동
                const first = data.markers[0];
                mapMain.map.panTo(new kakao.maps.LatLng(
                    first.position.lat,
                    first.position.lng
                ));
            } else {
                mapUI.showMessage('조건에 맞는 AI 추천 결과가 없습니다.');
            }
        } catch (error) {
            console.error('AI 추천 오류:', error);
            mapUI.showMessage('AI 추천을 가져올 수 없습니다');
        }
    }
}

const mapAI = new MapAIController();