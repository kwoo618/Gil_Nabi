// static/js/debug_helper.js
const debugHelper = {
    // 현재 상태 전체 체크
    checkAllSystems: function() {
        console.log("=== 시스템 체크 시작 ===");
        
        // 1. 전역 객체 확인
        console.log("1. 전역 객체:");
        console.log("   - mapMain:", typeof mapMain);
        console.log("   - mapFilter:", typeof mapFilter);
        console.log("   - mapSearch:", typeof mapSearch);
        console.log("   - mapClick:", typeof mapClick);
        console.log("   - mapAI:", typeof mapAI);
        console.log("   - mapMarkers:", typeof mapMarkers);
        console.log("   - mapInfo:", typeof mapInfo);
        console.log("   - mapUI:", typeof mapUI);
        
        // 2. 지도 상태
        console.log("2. 지도 상태:");
        console.log("   - map 객체:", mapMain.map ? "✓" : "✗");
        console.log("   - 현재 마커 수:", mapMain.markers ? mapMain.markers.length : 0);
        console.log("   - 현재 필터:", mapMain.currentFilters);
        
        // 3. 인증 상태
        console.log("3. 인증:");
        console.log("   - Access Token:", localStorage.getItem('access_token') ? "있음" : "없음");
        
        // 4. API 테스트
        this.testAPIs();
    },
    
    // API 연결 테스트
    testAPIs: async function() {
        console.log("4. API 테스트:");
        
        // Places API
        try {
            const placesRes = await fetch('/api/places/');
            console.log("   - Places API:", placesRes.ok ? "✓" : "✗");
        } catch (e) {
            console.log("   - Places API: ✗ (에러)");
        }
        
        // Reviews API
        try {
            const reviewsRes = await fetch('/api/reviews/');
            console.log("   - Reviews API:", reviewsRes.ok ? "✓" : "✗");
        } catch (e) {
            console.log("   - Reviews API: ✗ (에러)");
        }
        
        // Filter API
        try {
            const filterRes = await fetch('/api/places/filter/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    filters: {},
                    map_bounds: {north: 35.91, south: 35.88, east: 128.87, west: 128.84}
                })
            });
            console.log("   - Filter API:", filterRes.ok ? "✓" : "✗");
        } catch (e) {
            console.log("   - Filter API: ✗ (에러)");
        }
        
        console.log("=== 체크 완료 ===");
    },
    
    // 수동 리뷰 생성 (테스트용)
    createTestReview: async function(placeId) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            console.log("토큰이 없습니다. 로그인 필요");
            return;
        }
        
        const response = await fetch('/api/reviews/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                place: placeId,
                rating: 4,
                content: "테스트 리뷰입니다",
                disability_type: "physical"
            })
        });
        
        if (response.ok) {
            console.log("✅ 리뷰 생성 성공");
        } else {
            console.log("❌ 리뷰 생성 실패:", await response.text());
        }
    },

    // 🎲 테스트 데이터 자동 생성 (장소 + 리뷰)
    generateTestData: async function() {
        console.log("🎲 테스트 데이터 생성 시작...");
        
        // 1. 임의의 장소 데이터 생성
        const randomId = Math.floor(Math.random() * 10000);
        const placeData = {
            id: "test_place_" + randomId,
            building_name: "테스트 장소 " + randomId,
            latitude: 35.896 + (Math.random() * 0.01 - 0.005), // 현재 지도 중심 근처 난수
            longitude: 128.850 + (Math.random() * 0.01 - 0.005),
            wheelchair: true,
            has_elevator: Math.random() > 0.5,
            has_ramp: true,
            accessible_toilet: Math.random() > 0.5
        };

        try {
            const placeRes = await fetch('/api/places/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(placeData)
            });
            
            if (placeRes.ok) {
                const place = await placeRes.json();
                console.log("✅ 장소 생성 성공:", place.building_name);
                
                // 2. 해당 장소에 리뷰 생성 시도
                await this.createTestReview(place.id);
                
                alert(`테스트 데이터 생성 완료!\n장소: ${place.building_name}\n(리뷰 생성은 로그인이 필요합니다)`);
                
                // 지도 새로고침
                if (typeof mapMain !== 'undefined') mapMain.loadInitialData();
            } else {
                console.error("장소 생성 실패:", await placeRes.text());
                alert("장소 생성 실패");
            }
        } catch (e) {
            console.error("데이터 생성 오류:", e);
            alert("데이터 생성 중 오류 발생");
        }
    },

    getCSRFToken: function() {
        let matches = document.cookie.match(/csrftoken=([^;]+)/);
        return matches ? matches[1] : null;
    }
};

// 페이지 로드 시 자동 체크
window.addEventListener('load', () => {
    setTimeout(() => {
        debugHelper.checkAllSystems();
    }, 2000);
});