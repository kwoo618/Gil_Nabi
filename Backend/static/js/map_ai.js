// static/js/map_ai.js

const mapAI = {
    getRecommendation: async function() {
        // 1. 로그인(토큰) 확인 로직 제거됨

        mapUI.showLoading('AI 분석 중...');
        
        try {
            const params = {
                map_bounds: mapMain.getMapBounds(),
                limit: 5
                filters: mapMain.currentFilters
            };
            
            const response = await fetch('/api/places/ai-recommend/', {
                method: 'POST',
                headers: {
                    // 2. Authorization 헤더 제거됨
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });
            
            // 3. 401(인증 실패) 처리 로직 제거됨
            
            const data = await response.json();
            console.log('AI 추천 결과:', data);
            
            if (data.success && data.markers && data.markers.length > 0) {
                mapMarkers.clearAll();
                
                // AI 마커 표시
                data.markers.forEach((place, index) => {
                    const position = new kakao.maps.LatLng(
                        place.position.lat,
                        place.position.lng
                    );
                    
                    const marker = new kakao.maps.Marker({
                        position: position,
                        map: mapMain.map
                    });
                    
                    // 순위 오버레이
                    const content = `
                        <div style="
                            padding: 8px 12px;
                            background: ${index === 0 ? '#ff6b6b' : '#4ecdc4'};
                            color: white;
                            border-radius: 20px;
                            font-weight: bold;
                            position: absolute;
                            transform: translate(-50%, -150%);
                            white-space: nowrap;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                        ">${index + 1}위</div>
                    `;
                    
                    const customOverlay = new kakao.maps.CustomOverlay({
                        position: position,
                        content: content,
                        yAnchor: 1
                    });
                    
                    customOverlay.setMap(mapMain.map);
                    mapMain.markers.push(customOverlay);
                    mapMain.markers.push(marker);
                    
                    // 클릭 이벤트
                    kakao.maps.event.addListener(marker, 'click', function() {
                        // place 객체를 mapInfo가 이해할 수 있는 형태로 변환하여 전달해야 할 수도 있음
                        // 백엔드에서 오는 데이터 구조에 따라 building_name 등을 매핑
                        mapInfo.showPlaceInfo(place, marker);
                    });
                });
                
                // 결과 표시 (user_info가 없을 수 있으므로 기본값 처리 필요할 수 있음)
                const userInfo = data.user_info || { disability_type: '비회원', has_wheelchair: false };
                mapUI.showAIResults(data.markers, userInfo);
                
                // 첫 번째 추천으로 이동
                const first = data.markers[0];
                mapMain.map.panTo(new kakao.maps.LatLng(
                    first.position.lat,
                    first.position.lng
                ));
            } else {
                mapUI.showMessage('AI 추천 결과가 없습니다');
            }
        } catch (error) {
            console.error('AI 추천 오류:', error);
            mapUI.showMessage('AI 추천을 가져올 수 없습니다');
        }
    }
};