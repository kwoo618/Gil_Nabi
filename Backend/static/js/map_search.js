// map_search.js - 검색 기능 개선
class MapSearchController {
    async search() {
        const query = document.getElementById('search-input').value.trim();
        
        if (!query) {
            alert('검색어를 입력하세요');
            return;
        }
        
        mapUI.showLoading('검색 중...');
        mapMarkers.clearAll();
        
        // 현재 화면 범위 가져오기
        const bounds = mapMain.getMapBounds();
        
        // 필터가 활성화되어 있으면 필터 API 사용
        if (mapMain.hasActiveFilters()) {
            const data = await mapFilter.getFilteredData({
                search_query: query,
                map_bounds: bounds  // 화면 범위 추가
            });
            
            if (data && data.success && data.markers.length > 0) {
                this.displayFilteredResults(data.markers, query, '필터+DB');
            } else {
                mapUI.showMessage(`현재 화면에서 "${query}" 검색 결과가 없습니다`);
            }
        } else {
            // DB 검색 (화면 범위 내)
            try {
                const response = await fetch('/api/places/filter/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        filters: {},
                        map_bounds: bounds,
                        search_query: query
                    })
                });
                
                const data = await response.json();
                
                if (data.success && data.markers.length > 0) {
                    this.displayFilteredResults(data.markers, query, 'DB');
                } else {
                    // 카카오맵 검색 (화면 범위 내)
                    this.searchKakaoInBounds(query, bounds);
                }
            } catch (error) {
                console.error('검색 오류:', error);
                this.searchKakaoInBounds(query, bounds);
            }
        }
    }

    searchKakaoInBounds(query, bounds) {
        const center = new kakao.maps.LatLng(
            (bounds.north + bounds.south) / 2,
            (bounds.east + bounds.west) / 2
        );
        
        mapMain.places.keywordSearch(query, (data, status) => {
            if (status === kakao.maps.services.Status.OK) {
                // 화면 범위 내 결과만 필터링
                const filteredData = data.filter(place => {
                    const lat = parseFloat(place.y);
                    const lng = parseFloat(place.x);
                    return lat >= bounds.south && lat <= bounds.north &&
                        lng >= bounds.west && lng <= bounds.east;
                });
                
                if (filteredData.length > 0) {
                    this.displayKakaoResults(filteredData, query);
                } else {
                    mapUI.showMessage(`현재 화면에서 "${query}" 검색 결과가 없습니다`);
                }
            } else {
                mapUI.showMessage(`"${query}"에 대한 검색 결과가 없습니다`);
            }
        }, {
            location: center,
            radius: 5000  // 5km 반경
        });
    }
    
    displayFilteredResults(results, query, source) {
        results.forEach((place, index) => {
            const position = new kakao.maps.LatLng(
                place.position.lat,
                place.position.lng
            );
            
            const marker = new kakao.maps.Marker({
                position: position,
                map: mapMain.map
            });
            
            // 마커 클릭 이벤트
            kakao.maps.event.addListener(marker, 'click', function() {
                mapMarkers.setCurrentMarker(marker);  // 현재 마커 설정
                mapInfo.showPlaceInfo(place, marker);
            });
            
            mapMain.markers.push(marker);
            
            // 첫 번째 마커 정보 표시
            if (index === 0) {
                mapMarkers.setCurrentMarker(marker);
                mapInfo.showPlaceInfo(place, marker);
                mapMain.map.panTo(position);
            }
        });
        
        // 결과 목록 표시
        mapUI.showSearchResults(results, query, source);
    }
    
    displayKakaoResults(results, query) {
        results.forEach((place, index) => {
            const position = new kakao.maps.LatLng(place.y, place.x);
            
            const marker = new kakao.maps.Marker({
                position: position,
                map: mapMain.map
            });
            
            // 마커 클릭 이벤트
            kakao.maps.event.addListener(marker, 'click', function() {
                // 카카오 데이터를 DB 형식으로 변환
                const placeData = {
                    id: place.id,
                    place_name: place.place_name,
                    address_name: place.address_name,
                    y: place.y,
                    x: place.x
                };
                mapInfo.showPlaceInfo(placeData, marker);
            });
            
            mapMain.markers.push(marker);
            
            // 첫 번째 마커로 이동
            if (index === 0) {
                mapMain.map.panTo(position);
            }
        });
        
        // 결과 목록 표시
        mapUI.showSearchResults(results, query, '카카오맵');
    }
}

const mapSearch = new MapSearchController();