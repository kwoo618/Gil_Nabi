// map_click.js - 지도 클릭 이벤트 및 장소 저장
class MapClickController {
    init() {
        // 지도 클릭 이벤트
        kakao.maps.event.addListener(mapMain.map, 'click', (mouseEvent) => {
            this.handleMapClick(mouseEvent.latLng);
        });
    }
    
    async handleMapClick(latlng) {
        console.log('🖱️ 클릭 좌표:', latlng.toString());
        mapUI.showLoading('장소 검색 중...');
        
        try {
            // 1. 좌표로 주소 검색
            const address = await this.getAddressFromCoords(latlng);
            
            // 2. 카카오 Places API로 장소 검색
            const placeInfo = await this.searchPlace(latlng, address);
            
            if (placeInfo) {
                console.log('📍 찾은 장소:', placeInfo.place_name);
                await this.processPlace(placeInfo);
            } else {
                mapUI.showMessage('해당 위치에 장소가 없습니다');
            }
        } catch (error) {
            console.error('장소 검색 오류:', error);
            mapUI.showMessage('장소 검색 중 오류가 발생했습니다');
        }
    }
    
    getAddressFromCoords(latlng) {
        return new Promise((resolve) => {
            mapMain.geocoder.coord2Address(latlng.getLng(), latlng.getLat(), (result, status) => {
                if (status === kakao.maps.services.Status.OK) {
                    const address = result[0].address.address_name;
                    resolve(address);
                } else {
                    resolve(null);
                }
            });
        });
    }
    
    searchPlace(latlng, address) {
        return new Promise((resolve) => {
            // 주소가 있으면 주소로 검색
            if (address) {
                mapMain.places.keywordSearch(address, (data, status) => {
                    if (status === kakao.maps.services.Status.OK && data.length > 0) {
                        resolve(data[0]);
                    } else {
                        // 주변 검색
                        this.searchNearby(latlng, resolve);
                    }
                }, {
                    location: latlng,
                    radius: 20
                });
            } else {
                // 주변 검색
                this.searchNearby(latlng, resolve);
            }
        });
    }
    
    searchNearby(latlng, resolve) {
        // 카테고리 검색 대신 키워드 검색 사용 (빈 키워드 + 좌표 기반)
        // 또는 특정 카테고리 지정 (예: 편의시설 등)
        mapMain.places.keywordSearch('건물', (data, status) => { 
            if (status === kakao.maps.services.Status.OK && data.length > 0) {
                resolve(data[0]);
            } else {
                resolve(null);
            }
        }, {
            location: latlng,
            radius: 50,
            sort: kakao.maps.services.SortBy.DISTANCE
        });
    }
    
// processPlace 메소드 수정
    async processPlace(placeInfo) {
        const kakaoId = String(placeInfo.id);
        
        try {
            // DB 확인 - id 파라미터로 정확한 검색
            const response = await fetch(`/api/places/?id=${kakaoId}`);
            const results = await response.json();
            
            if (results && results.length > 0) {
                // 이미 DB에 존재
                const place = results[0];
                mapMain.currentPlace = place;
                const marker = mapMarkers.addClickMarker(place);
                mapInfo.showPlaceInfo(place, marker);
                mapUI.showMessage('기존 장소 정보를 불러왔습니다');
            } else {
                // 신규 저장
                const newPlace = await this.saveNewPlace(placeInfo);
                if (newPlace) {
                    mapMain.currentPlace = newPlace;
                    const marker = mapMarkers.addClickMarker(newPlace);
                    mapInfo.showPlaceInfo(newPlace, marker);
                    mapUI.showMessage('새 장소가 저장되었습니다');
                }
            }
        } catch (error) {
            console.error('DB 처리 오류:', error);
            
            // 오류 시에도 마커는 표시
            const tempPlace = {
                id: kakaoId,
                building_name: placeInfo.place_name,
                latitude: parseFloat(placeInfo.y),
                longitude: parseFloat(placeInfo.x),
                address: placeInfo.address_name
            };
            
            const marker = mapMarkers.addClickMarker(tempPlace);
            mapInfo.showPlaceInfo(tempPlace, marker);
            mapUI.showMessage('DB 연결 오류 - 임시 표시');
        }
    }
    
    async saveNewPlace(placeInfo) {
        const newPlace = {
            id: String(placeInfo.id),
            building_name: placeInfo.place_name,
            latitude: parseFloat(placeInfo.y),
            longitude: parseFloat(placeInfo.x),
            address: placeInfo.address_name || placeInfo.road_address_name || '주소 없음',
            wheelchair: null,
            has_elevator: null,
            has_ramp: null,
            accessible_toilet: null
        };
        
        try {
            const response = await fetch('/api/places/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(newPlace)
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                const error = await response.json();
                console.error('저장 실패:', error);
                return null;
            }
        } catch (error) {
            console.error('저장 오류:', error);
            return null;
        }
    }

    getCSRFToken() {
        let csrftoken = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(cookie => {
                const parts = cookie.trim().split('=');
                if (parts[0] === 'csrftoken') {
                    csrftoken = parts[1];
                }
            });
        }
        return csrftoken;
    }
}

const mapClick = new MapClickController();