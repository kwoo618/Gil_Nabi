// map_filter.js - 필터링 기능
const mapFilter = {
    init: function() {
        // 필터 체크박스 이벤트
        document.querySelectorAll('.filter-item input').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateFilters());
        });
    },
    
    updateFilters: function() {
        mapMain.currentFilters = {
            wheelchair: document.getElementById('wheelchair').checked,
            has_elevator: document.getElementById('elevator').checked,
            has_ramp: document.getElementById('ramp').checked,
            accessible_toilet: document.getElementById('toilet').checked
        };
        
        // 필터 상태 표시
        const activeCount = Object.values(mapMain.currentFilters).filter(v => v).length;
        if (activeCount > 0) {
            mapUI.showMessage(`${activeCount}개 필터 활성화됨`);
        }
    },
    
    getFilteredData: async function(additionalParams = {}) {
        const params = {
            filters: mapMain.currentFilters,
            map_bounds: mapMain.getMapBounds(),
            ...additionalParams
        };
        
        try {
            const response = await fetch('/api/places/filter/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(params)
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('필터링 오류:', error);
            return null;
        }
    },
    
    applyFilters: async function() {
        mapUI.showLoading('필터링 중...');
        
        const data = await this.getFilteredData();
        
        if (data && data.success) {
            mapMarkers.clearAll();
            
            if (data.markers.length > 0) {
                data.markers.forEach(place => {
                    mapMarkers.addFilterMarker(place);
                });
                mapUI.showFilterResults(data.markers);
            } else {
                mapUI.showMessage('필터 조건에 맞는 장소가 없습니다');
            }
        } else {
            // 👈 [추가] 실패 시 로딩 화면을 없애고 에러 메시지 표시
            mapUI.showMessage('필터링 결과를 가져오지 못했습니다.');
        }
    },
    
    clearFilters: function() {
        document.querySelectorAll('.filter-item input').forEach(cb => {
            cb.checked = false;
        });
        
        mapMain.currentFilters = {
            wheelchair: false,
            has_elevator: false,
            has_ramp: false,
            accessible_toilet: false
        };
    }
};