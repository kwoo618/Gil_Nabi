// map_click.js - 지도 클릭 이벤트 및 장소 저장

const mapClick = {
    init: function() {
        // 지도 클릭 이벤트
        kakao.maps.event.addListener(mapMain.map, 'click', (mouseEvent) => {
            this.handleMapClick(mouseEvent.latLng);
        });
    },
    
    handleMapClick: async function(latlng) {
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
    },
    
    getAddressFromCoords: function(latlng) {
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
    },
    
    searchPlace: function(latlng, address) {
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
    },
    
    searchNearby: function(latlng, resolve) {
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
    },
    
// processPlace 메소드 수정
    processPlace: async function(placeInfo) {
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
    },
    
    saveNewPlace: async function(placeInfo) {
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
    },
    
    showPlaceDetails: function(place) {
        const marker = mapMarkers.getCurrentMarker();
        mapInfo.showPlaceInfo(place, marker);  // mapClick.showPlaceInfo 대신
    },
    
    showEditForm: function(placeId) {
        const place = mapMain.currentPlace;
        if (!place || place.id != placeId) return;
        
        const content = `
            <div style="padding:15px; min-width:300px;">
                <h4 style="margin:0 0 10px 0;">${place.building_name} - 수정</h4>
                <form id="edit-form">
                    <table style="width:100%; font-size:13px;">
                        <tr>
                            <td>휠체어:</td>
                            <td>${this.createRadioButtons('wheelchair', place.wheelchair)}</td>
                        </tr>
                        <tr>
                            <td>엘리베이터:</td>
                            <td>${this.createRadioButtons('has_elevator', place.has_elevator)}</td>
                        </tr>
                        <tr>
                            <td>경사로:</td>
                            <td>${this.createRadioButtons('has_ramp', place.has_ramp)}</td>
                        </tr>
                        <tr>
                            <td>화장실:</td>
                            <td>${this.createRadioButtons('accessible_toilet', place.accessible_toilet)}</td>
                        </tr>
                    </table>
                    <div style="margin-top:10px; display:flex; gap:5px;">
                        <button type="button" onclick="mapClick.saveEdit('${place.id}')"
                                style="flex:1; padding:5px; background:#28a745; color:white; border:none; border-radius:4px; cursor:pointer;">
                            저장
                        </button>
                        <button type="button" onclick="mapClick.showPlaceInfo(mapMain.currentPlace)"
                                style="flex:1; padding:5px; background:#6c757d; color:white; border:none; border-radius:4px; cursor:pointer;">
                            취소
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        mapMain.infowindow.setContent(content);
    },
    
    createRadioButtons: function(field, value) {
        const name = `${field}_radio`;
        return `
            <label><input type="radio" name="${name}" value="true" ${value === true ? 'checked' : ''}> O</label>
            <label><input type="radio" name="${name}" value="false" ${value === false ? 'checked' : ''}> X</label>
            <label><input type="radio" name="${name}" value="null" ${value == null ? 'checked' : ''}> ?</label>
        `;
    },
    
    saveEdit: async function(placeId) {
        const form = document.getElementById('edit-form');
        if (!form) return;
        
        const updateData = {};
        ['wheelchair', 'has_elevator', 'has_ramp', 'accessible_toilet'].forEach(field => {
            const radio = form.querySelector(`input[name="${field}_radio"]:checked`);
            if (radio) {
                updateData[field] = radio.value === 'null' ? null : (radio.value === 'true');
            }
        });
        
        try {
            const response = await fetch(`/api/places/${placeId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(updateData)
            });
            
            if (response.ok) {
                const updated = await response.json();
                mapMain.currentPlace = updated;
                this.showPlaceInfo(updated);
                mapUI.showMessage('수정되었습니다');
            } else {
                console.error('수정 실패');
                alert('수정에 실패했습니다');
            }
        } catch (error) {
            console.error('수정 오류:', error);
            alert('수정 중 오류가 발생했습니다');
        }
    },
    
    getAccessIcon: function(value) {
        if (value === true) return '✅';
        if (value === false) return '❌';
        return '❓';
    },
    
    getCSRFToken: function() {
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
};