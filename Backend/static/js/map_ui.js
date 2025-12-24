// map_ui.js - UI 헬퍼
class MapUIController {
    showLoading(message = '로딩 중...') {
        document.getElementById('results').innerHTML = `
            <div style="text-align:center; padding:20px;">
                <div style="font-size:24px; margin-bottom:10px;">⏳</div>
                <div>${message}</div>
            </div>
        `;
    }
    
    showMessage(message) {
        document.getElementById('results').innerHTML = `
            <div style="text-align:center; padding:20px; color:#6c757d;">
                ${message}
            </div>
        `;
    }
    
    // 통합 검색 결과 표시 (필터, 검색, 카카오 등)
    showSearchResults(places, query, source = '검색') {
        let html = `<h4>🔍 "${query}" ${source} 결과</h4>`;
        html += `<p style="color:#666; font-size:12px;">${places.length}개 발견</p>`;
        
        places.forEach((place, i) => {
            const name = place.building_name || place.place_name;
            const address = place.address || place.address_name || '';
            const info = place.matching_filters ? place.matching_filters.join(' • ') : address;

            html += `
                <div class="result-item" style="padding:10px; border-bottom:1px solid #eee; cursor:pointer;"
                     onclick="mapUI.triggerMarkerClick(${i})">
                    <strong>${i + 1}. ${name}</strong><br>
                    <small style="color:#666;">${info}</small>
                </div>
            `;
        });
        
        document.getElementById('results').innerHTML = html;
    }

    showFilterResults(places) {
        let html = '<h4>📍 필터 결과</h4>';
        html += `<p style="color:#666; font-size:12px;">${places.length}개 장소</p>`;
        
        places.forEach((place, i) => {
            html += `
                <div class="result-item" style="padding:10px; border-bottom:1px solid #eee; cursor:pointer;"
                     onclick="mapUI.triggerMarkerClick(${i})">
                    <strong>${i + 1}. ${place.building_name}</strong><br>
                    <small style="color:#666;">${place.matching_filters.join(' • ')}</small>
                </div>
            `;
        });
        
        document.getElementById('results').innerHTML = html;
    }
    
    showAIResults(places, userInfo) {
        let html = '<h4>🤖 AI 추천 Top 5</h4>';
        html += `<p style="color:#666; font-size:12px;">
            사용자: ${userInfo.disability_type} | 휠체어: ${userInfo.has_wheelchair ? 'O' : 'X'}
        </p>`;
        
        places.forEach((place, i) => {
            const rank = i + 1;
            const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '🏅';
            
            html += `
                <div class="result-item" style="padding:12px; border-bottom:1px solid #eee; cursor:pointer;"
                     onclick="mapUI.triggerMarkerClick(${i})">
                    <div style="display:flex; align-items:center;">
                        <span style="font-size:24px; margin-right:10px;">${medal}</span>
                        <div>
                            <strong>${rank}. ${place.building_name}</strong><br>
                            <small style="color:#666;">
                                ⭐ ${place.score}점 | 리뷰 ${place.review_count}개
                            </small>
                        </div>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('results').innerHTML = html;
    }
    
    async showDBInfo() {
        this.showLoading('DB 정보 로딩 중...');
        
        try {
            // 장소 정보
            let places = [];
            try {
                const placesRes = await fetch('/api/places/');
                const placesData = await placesRes.json();
                places = Array.isArray(placesData) ? placesData : (placesData.results || []);
            } catch (e) { console.warn("장소 로드 실패", e); }
            
            // 리뷰 정보
            let reviews = [];
            try {
                const reviewsRes = await fetch('/api/reviews/');
                const reviewsData = await reviewsRes.json();
                reviews = Array.isArray(reviewsData) ? reviewsData : (reviewsData.results || []);
            } catch (e) { console.warn("리뷰 로드 실패 (데이터가 없거나 API 오류)", e); }
            
            let html = '<h4>📊 데이터베이스 현황</h4>';
            html += `<p>총 ${places.length}개 장소 | ${reviews.length}개 리뷰</p>`;
            html += '<div style="max-height:400px; overflow-y:auto;">';
            
            // 장소별 정보
            places.forEach((place, i) => {
                // 해당 장소의 리뷰 필터링
                const placeReviews = reviews.filter(r => r.place === place.id);
                const avgRating = placeReviews.length > 0 
                    ? (placeReviews.reduce((sum, r) => sum + r.rating, 0) / placeReviews.length).toFixed(1)
                    : '없음';
                
                html += `
                    <div style="padding:10px; border-bottom:1px solid #eee;">
                        <strong>${i + 1}. ${place.building_name}</strong>
                        <div style="font-size:12px; color:#666; margin:5px 0;">
                            접근성: 
                            ${place.wheelchair ? '✅' : place.wheelchair === false ? '❌' : '❓'} 휠체어 |
                            ${place.has_elevator ? '✅' : place.has_elevator === false ? '❌' : '❓'} 엘리베이터 |
                            ${place.has_ramp ? '✅' : place.has_ramp === false ? '❌' : '❓'} 경사로 |
                            ${place.accessible_toilet ? '✅' : place.accessible_toilet === false ? '❌' : '❓'} 화장실
                        </div>
                        <div style="font-size:12px; color:#0066cc;">
                            리뷰: ${placeReviews.length}개 | 평균: ${avgRating}점
                        </div>`;
                
                // 최근 리뷰 2개 표시
                if (placeReviews.length > 0) {
                    html += '<div style="margin-left:10px; font-size:11px; color:#888;">';
                    placeReviews.slice(0, 2).forEach(review => {
                        html += `<div>• ${review.rating}점: ${review.content.substring(0, 30)}...</div>`;
                    });
                    html += '</div>';
                }
                
                html += '</div>';
            });
            
            html += '</div>';
            document.getElementById('results').innerHTML = html;
            
        } catch (error) {
            console.error('DB 정보 로드 오류:', error);
            this.showMessage('DB 정보를 불러올 수 없습니다');
        }
    }

    // 마커 클릭 트리거 (리스트 클릭 시 지도 마커 클릭 효과)
    triggerMarkerClick(index) {
        const marker = mapMain.markers[index];
        if (marker) {
            kakao.maps.event.trigger(marker, 'click');
            mapMain.map.panTo(marker.getPosition());
        }
    }
}

const mapUI = new MapUIController();