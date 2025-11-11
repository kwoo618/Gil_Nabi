// static/js/map.js - 완전 통합 버전
const API_BASE_URL = 'http://localhost:8000';

kakao.maps.load(function() {
    // ============ 변수 선언 ============
    const NEARBY_SEARCH_RADIUS = 5;
    const KEYWORD_SEARCH_RADIUS = 500;
    
    const container = document.getElementById('map');
    const options = {
        center: new kakao.maps.LatLng(35.8959, 128.8502), // 대구대 기본 위치
        level: 3
    };
    const map = new kakao.maps.Map(container, options);
    
    const geocoder = new kakao.maps.services.Geocoder();
    const ps = new kakao.maps.services.Places();
    let selectedMarker = null;
    const placeInfoDiv = document.getElementById('place-info');
    let currentPlaceData = null;
    let categoryMarkers = [];
    let aiMarkers = [];
    let filterMarkers = [];
    let currentMode = 'normal';
    let currentLocationMarker = null;
    
    // ============ 현재 위치 기능 ============
    function getCurrentLocation() {
        console.log('📍 현재 위치 가져오기 시작');
        
        // 기존 현재위치 마커 제거
        if (currentLocationMarker) {
            currentLocationMarker.setMap(null);
            currentLocationMarker = null;
        }
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    const currentPos = new kakao.maps.LatLng(lat, lng);
                    
                    map.setCenter(currentPos);
                    
                    // 현재 위치 마커
                    currentLocationMarker = new kakao.maps.Marker({
                        position: currentPos,
                        map: map,
                        title: '현재 위치',
                        image: new kakao.maps.MarkerImage(
                            'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
                            new kakao.maps.Size(24, 35)
                        )
                    });
                    
                    console.log('✅ 현재 위치 설정:', lat, lng);
                    placeInfoDiv.innerHTML = '<p>📍 현재 위치로 이동했습니다.</p>';
                },
                function(error) {
                    console.warn('❌ 위치 정보 실패, 대구대로 이동');
                    map.setCenter(new kakao.maps.LatLng(35.8959, 128.8502));
                    placeInfoDiv.innerHTML = '<p>위치 정보를 가져올 수 없어 대구대로 이동했습니다.</p>';
                },
                {
                    enableHighAccuracy: true,
                    timeout: 5000,
                    maximumAge: 0
                }
            );
        } else {
            alert('브라우저가 위치 정보를 지원하지 않습니다.');
        }
    }
    
    // ============ AI 추천 기능 ============
    async function loadAIRecommendations() {
        console.log('🤖 AI 추천 시작');
        
        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('AI 추천은 로그인이 필요합니다.');
            window.location.href = '/login/';
            return;
        }
        
        const bounds = map.getBounds();
        const mapBounds = {
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest()
        };
        
        console.log('📍 지도 범위:', mapBounds);
        
        placeInfoDiv.innerHTML = '<p>🤖 AI 추천 분석 중...</p>';
        clearAllMarkers();
        currentMode = 'ai';
        
        try {
            const response = await fetch('/api/places/ai-recommend/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    map_bounds: mapBounds,
                    limit: 5
                })
            });
            
            console.log('📡 응답 상태:', response.status);
            
            if (!response.ok) {
                throw new Error(`서버 오류: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ AI 추천 데이터:', data);
            
            if (data.success && data.markers && data.markers.length > 0) {
                displayAIRecommendations(data.markers);
                showAIResultsList(data);
            } else {
                placeInfoDiv.innerHTML = '<p>추천할 장소가 없습니다. 지도를 이동해보세요.</p>';
            }
            
        } catch (error) {
            console.error('❌ AI 추천 오류:', error);
            placeInfoDiv.innerHTML = `<p style="color: red;">AI 추천 중 오류: ${error.message}</p>`;
        }
    }
    
    // AI 추천 결과 목록 표시
    function showAIResultsList(data) {
        let html = `
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <h3 style="margin: 0;">🤖 AI 추천 Top 5</h3>
                <p style="margin: 5px 0; font-size: 14px;">
                    ${data.user_info.disability_type || '정보없음'} | 
                    휠체어: ${data.user_info.has_wheelchair ? 'O' : 'X'}
                </p>
            </div>
            <ul style="list-style: none; padding: 0; margin: 0;">
        `;
        
        data.markers.forEach((marker, index) => {
            html += `
                <li style="padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; hover: background: #f5f5f5;" 
                    onclick="focusAIMarker(${index})"
                    onmouseover="this.style.background='#f5f5f5'" 
                    onmouseout="this.style.background='white'">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>${index + 1}. ${marker.building_name}</strong>
                        <span style="color: ${getScoreColor(marker.score)}; font-weight: bold;">
                            ★ ${marker.score}점
                        </span>
                    </div>
                    <small style="color: #666;">리뷰 ${marker.review_count}개</small>
                </li>
            `;
        });
        html += '</ul>';
        placeInfoDiv.innerHTML = html;
    }
    
    // AI 마커 표시
    function displayAIRecommendations(markers) {
        clearAIMarkers();
        
        markers.forEach((markerData, index) => {
            const position = new kakao.maps.LatLng(
                markerData.position.lat,
                markerData.position.lng
            );
            
            // 순위 오버레이
            const content = `<div class="marker-overlay ${getScoreClass(markerData.score)}">${index + 1}</div>`;
            const overlay = new kakao.maps.CustomOverlay({
                position: position,
                content: content,
                yAnchor: 1,
                zIndex: 10
            });
            overlay.setMap(map);
            aiMarkers.push(overlay);
            
            // 클릭 가능한 마커
            const marker = new kakao.maps.Marker({
                position: position,
                map: map
            });
            
            kakao.maps.event.addListener(marker, 'click', () => {
                showAIPlaceInfo(markerData, index);
            });
            
            aiMarkers.push(marker);
        });
    }
    
    // ============ 필터링 기능 ============
    async function applyAccessibilityFilter() {
        console.log('🔍 필터링 시작');
        
        const filters = {
            has_ramp: document.getElementById('filter-ramp').checked,
            wheelchair: document.getElementById('filter-wheelchair').checked,
            accessible_toilet: document.getElementById('filter-toilet').checked,
            has_elevator: document.getElementById('filter-elevator').checked
        };
        
        console.log('선택된 필터:', filters);
        
        if (!Object.values(filters).some(v => v)) {
            alert('최소 하나의 필터를 선택하세요.');
            return;
        }
        
        const bounds = map.getBounds();
        const mapBounds = {
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest()
        };
        
        placeInfoDiv.innerHTML = '<p>🔍 필터링 중...</p>';
        clearAllMarkers();
        currentMode = 'filter';
        
        try {
            const response = await fetch('/api/places/filter/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    filters: filters,
                    map_bounds: mapBounds
                })
            });
            
            console.log('📡 필터 응답:', response.status);
            
            const data = await response.json();
            console.log('✅ 필터 데이터:', data);
            
            if (data.success && data.markers && data.markers.length > 0) {
                displayFilteredPlaces(data.markers);
                showFilterResultsList(data, filters);
            } else {
                placeInfoDiv.innerHTML = '<p>조건에 맞는 장소가 없습니다.</p>';
            }
            
        } catch (error) {
            console.error('❌ 필터링 오류:', error);
            placeInfoDiv.innerHTML = `<p style="color: red;">필터링 중 오류: ${error.message}</p>`;
        }
    }
    
    // 필터 결과 목록 표시
    function showFilterResultsList(data, filters) {
        const activeFilters = Object.keys(filters).filter(k => filters[k]);
        
        let html = `
            <div style="background: #667eea; color: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <h3 style="margin: 0;">🔍 필터링 결과</h3>
                <p style="margin: 5px 0; font-size: 14px;">
                    ${data.count}개 장소 | 
                    필터: ${activeFilters.map(f => getFilterName(f)).join(', ')}
                </p>
            </div>
            <ul style="list-style: none; padding: 0; margin: 0; max-height: 400px; overflow-y: auto;">
        `;
        
        data.markers.slice(0, 10).forEach(marker => {
            html += `
                <li style="padding: 10px; border-bottom: 1px solid #eee;">
                    <strong>${marker.building_name}</strong><br>
                    <small style="color: #4CAF50;">✓ ${marker.matching_filters.join(', ')}</small>
                </li>
            `;
        });
        
        if (data.count > 10) {
            html += `<li style="padding: 10px; text-align: center; color: #666;">
                ... 외 ${data.count - 10}개
            </li>`;
        }
        
        html += '</ul>';
        placeInfoDiv.innerHTML = html;
    }
    
    // 필터 결과 마커 표시
    function displayFilteredPlaces(markers) {
        clearFilterMarkers();
        
        markers.forEach(markerData => {
            const marker = new kakao.maps.Marker({
                position: new kakao.maps.LatLng(
                    markerData.position.lat,
                    markerData.position.lng
                ),
                map: map
            });
            
            kakao.maps.event.addListener(marker, 'click', () => {
                showFilteredPlaceInfo(markerData);
            });
            
            filterMarkers.push(marker);
        });
    }
    
    // 필터된 장소 정보 표시
    function showFilteredPlaceInfo(markerData) {
        placeInfoDiv.innerHTML = `
            <div style="padding: 15px;">
                <h3>${markerData.building_name}</h3>
                <div style="background: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <strong>매칭 필터:</strong><br>
                    ${markerData.matching_filters.map(f => 
                        `<span style="background: #4CAF50; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 2px; display: inline-block;">${f}</span>`
                    ).join(' ')}
                </div>
                <button class="write-review-btn" onclick="openReviewModal('${markerData.place_id}', '${markerData.building_name}')">
                    📝 리뷰 작성
                </button>
            </div>
        `;
    }
    
    // AI 장소 상세 정보
    function showAIPlaceInfo(markerData, rank) {
        placeInfoDiv.innerHTML = `
            <div style="padding: 15px;">
                <h3 style="color: #667eea;">🏆 ${rank + 1}위. ${markerData.building_name}</h3>
                <div style="padding: 10px; background: #f5f5f5; border-radius: 5px; margin: 10px 0;">
                    <div style="font-size: 24px; color: ${getScoreColor(markerData.score)};">
                        ★ ${markerData.score}점
                    </div>
                    <small>리뷰 ${markerData.review_count}개 기준</small>
                </div>
                
                <h4>접근성 정보</h4>
                <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                    ${markerData.accessibility.wheelchair ? 
                        '<span style="background: #4CAF50; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">휠체어</span>' : ''}
                    ${markerData.accessibility.has_elevator ? 
                        '<span style="background: #4CAF50; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">엘리베이터</span>' : ''}
                    ${markerData.accessibility.has_ramp ? 
                        '<span style="background: #4CAF50; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">경사로</span>' : ''}
                    ${markerData.accessibility.accessible_toilet ? 
                        '<span style="background: #4CAF50; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">장애인화장실</span>' : ''}
                </div>
                
                <button class="write-review-btn" style="margin-top: 15px;" 
                        onclick="openReviewModal('${markerData.place_id}', '${markerData.building_name}')">
                    📝 리뷰 작성
                </button>
            </div>
        `;
        
        map.panTo(new kakao.maps.LatLng(markerData.position.lat, markerData.position.lng));
    }
    
    // ============ 유틸리티 함수 ============
    function clearAIMarkers() {
        aiMarkers.forEach(marker => {
            if (marker.setMap) marker.setMap(null);
        });
        aiMarkers = [];
    }
    
    function clearFilterMarkers() {
        filterMarkers.forEach(marker => marker.setMap(null));
        filterMarkers = [];
    }
    
    function clearAllMarkers() {
        clearAIMarkers();
        clearFilterMarkers();
        clearCategoryMarkers();
        if (selectedMarker) {
            selectedMarker.setMap(null);
            selectedMarker = null;
        }
    }
    
    function getScoreColor(score) {
        if (score >= 80) return '#4CAF50';
        if (score >= 60) return '#FFC107';
        return '#F44336';
    }
    
    function getScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        return 'normal';
    }
    
    function getFilterName(filter) {
        const names = {
            'has_ramp': '경사로',
            'wheelchair': '휠체어',
            'accessible_toilet': '장애인화장실',
            'has_elevator': '엘리베이터'
        };
        return names[filter] || filter;
    }
    
    window.focusAIMarker = function(index) {
        if (aiMarkers[index * 2 + 1]) {
            const marker = aiMarkers[index * 2 + 1];
            const position = marker.getPosition();
            map.panTo(position);
            
            // 마커 클릭 이벤트 트리거
            kakao.maps.event.trigger(marker, 'click');
        }
    };
    
    // ============ 이벤트 리스너 등록 ============
    // 버튼 이벤트 등록 전 요소 확인
    setTimeout(() => {
        // 현재 위치 버튼
        const currentLocationBtn = document.getElementById('current-location-btn');
        if (currentLocationBtn) {
            currentLocationBtn.addEventListener('click', getCurrentLocation);
            console.log('✅ 현재 위치 버튼 등록');
        }
        
        // AI 추천 버튼
        const aiRecommendBtn = document.getElementById('ai-recommend-btn');
        if (aiRecommendBtn) {
            aiRecommendBtn.addEventListener('click', loadAIRecommendations);
            console.log('✅ AI 추천 버튼 등록');
        }
        
        // 필터 적용 버튼
        const applyFilterBtn = document.getElementById('apply-filter-btn');
        if (applyFilterBtn) {
            applyFilterBtn.addEventListener('click', applyAccessibilityFilter);
            console.log('✅ 필터 적용 버튼 등록');
        }
        
        // 필터 초기화 버튼
        const clearFilterBtn = document.getElementById('clear-filter-btn');
        if (clearFilterBtn) {
            clearFilterBtn.addEventListener('click', () => {
                document.querySelectorAll('.filter-section input[type="checkbox"]').forEach(cb => {
                    cb.checked = false;
                });
                clearAllMarkers();
                currentMode = 'normal';
                placeInfoDiv.innerHTML = '<p>필터가 초기화되었습니다.</p>';
            });
            console.log('✅ 필터 초기화 버튼 등록');
        }
        
        // 자동 갱신 기능
        kakao.maps.event.addListener(map, 'idle', () => {
            const autoRefresh = document.getElementById('auto-refresh');
            if (autoRefresh && autoRefresh.checked && currentMode === 'ai') {
                console.log('🔄 자동 갱신 실행');
                loadAIRecommendations();
            }
        });
    }, 100);
    
    // 페이지 로드 시 현재 위치로 이동
    getCurrentLocation();
    
    // 여기 아래는 기존 지도 클릭, 검색 등의 코드...
    // (기존 코드 유지)
});