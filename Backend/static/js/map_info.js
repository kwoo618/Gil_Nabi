// static/js/map_info.js - 통합 장소 정보 표시
const mapInfo = {
    currentInfoWindow: null,
    
    // 정보창 표시
    showPlaceInfo: function(place, marker) {
        if (this.currentInfoWindow) {
            this.currentInfoWindow.close();
        }
        
        const normalizedPlace = this.normalizePlace(place);
        const content = this.createInfoContent(normalizedPlace);
        
        mapMain.infowindow.setContent(content);
        mapMain.infowindow.open(mapMain.map, marker);
        
        this.currentInfoWindow = mapMain.infowindow;
        mapMain.currentPlace = normalizedPlace;
        mapMarkers.setCurrentMarker(marker);
    },
    
    closeInfo: function() {
        if (this.currentInfoWindow) {
            this.currentInfoWindow.close();
            this.currentInfoWindow = null;
        }
        mapMain.currentPlace = null;
    },
    
    // 데이터 정규화
    normalizePlace: function(place) {
        return {
            id: place.id || place.place_id,
            building_name: place.building_name || place.place_name,
            latitude: place.latitude || place.position?.lat || place.y,
            longitude: place.longitude || place.position?.lng || place.x,
            address: place.address || place.address_name || place.road_address_name || '주소 없음',
            wheelchair: place.wheelchair ?? place.accessibility?.wheelchair,
            has_elevator: place.has_elevator ?? place.accessibility?.has_elevator,
            has_ramp: place.has_ramp ?? place.accessibility?.has_ramp,
            accessible_toilet: place.accessible_toilet ?? place.accessibility?.accessible_toilet,
            score: place.score,
            review_count: place.review_count
        };
    },
    
    // 정보창 내용 생성
    createInfoContent: function(place) {
        let content = `
            <div style="padding:15px; min-width:300px; max-width:400px;">
                <h4 style="margin:0 0 10px 0; color:#333;">${place.building_name}</h4>
                <p style="margin:5px 0; font-size:12px; color:#666;">
                    📍 ${place.address}
                </p>`;
        
        if (place.score) {
            content += `
                <div style="margin:10px 0; padding:8px; background:#f0f8ff; border-radius:4px;">
                    ⭐ AI 점수: ${place.score}점 | 리뷰 ${place.review_count}개
                </div>`;
        }
        
        content += `
                <hr style="margin:10px 0; border:none; border-top:1px solid #eee;">
                <h5 style="margin:10px 0; color:#555;">접근성 정보</h5>
                <table style="width:100%; font-size:13px;">
                    <tr style="height:28px;">
                        <td width="25%">♿ 휠체어:</td>
                        <td width="25%">${this.getAccessIcon(place.wheelchair)}</td>
                        <td width="25%">🛗 엘리베이터:</td>
                        <td width="25%">${this.getAccessIcon(place.has_elevator)}</td>
                    </tr>
                    <tr style="height:28px;">
                        <td>📐 경사로:</td>
                        <td>${this.getAccessIcon(place.has_ramp)}</td>
                        <td>🚻 화장실:</td>
                        <td>${this.getAccessIcon(place.accessible_toilet)}</td>
                    </tr>
                </table>`;
        
        if (place.id) {
            content += `
                <button onclick="mapInfo.showEditForm()" 
                        style="margin-top:12px; width:100%; padding:8px; 
                               background:linear-gradient(135deg, #667eea, #764ba2); 
                               color:white; border:none; border-radius:6px; 
                               cursor:pointer; font-weight:bold;">
                    접근성 정보 수정
                </button>`;
        }
        
        content += `</div>`;
        return content;
    },
    
    // 수정 폼 표시
    showEditForm: function() {
        const place = mapMain.currentPlace;
        if (!place) return;
        
        const content = `
            <div style="padding:15px; min-width:300px;">
                <h4 style="margin:0 0 10px 0; color:#333;">
                    ${place.building_name} - 수정
                </h4>
                <form id="edit-form">
                    <table style="width:100%; font-size:13px;">
                        <tr style="height:35px;">
                            <td width="35%">♿ 휠체어:</td>
                            <td>${this.createRadioButtons('wheelchair', place.wheelchair)}</td>
                        </tr>
                        <tr style="height:35px;">
                            <td>🛗 엘리베이터:</td>
                            <td>${this.createRadioButtons('has_elevator', place.has_elevator)}</td>
                        </tr>
                        <tr style="height:35px;">
                            <td>📐 경사로:</td>
                            <td>${this.createRadioButtons('has_ramp', place.has_ramp)}</td>
                        </tr>
                        <tr style="height:35px;">
                            <td>🚻 화장실:</td>
                            <td>${this.createRadioButtons('accessible_toilet', place.accessible_toilet)}</td>
                        </tr>
                    </table>
                    <div style="margin-top:12px; display:flex; gap:8px;">
                        <button type="button" onclick="mapInfo.saveEdit()"
                                style="flex:1; padding:8px; background:#28a745; 
                                       color:white; border:none; border-radius:4px; 
                                       cursor:pointer; font-weight:bold;">
                            저장
                        </button>
                        <button type="button" onclick="mapInfo.cancelEdit()"
                                style="flex:1; padding:8px; background:#6c757d; 
                                       color:white; border:none; border-radius:4px; 
                                       cursor:pointer;">
                            취소
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        mapMain.infowindow.setContent(content);
    },
    
    // 라디오 버튼 생성 (여기 수정됨)
    createRadioButtons: function(field, value) {
        const name = `${field}_radio`;
        // value가 정확히 false일 때만 checked
        const isFalse = value === false;
        const isTrue = value === true;
        const isNull = value === null || value === undefined;

        return `
            <label style="margin-right:10px; cursor:pointer;">
                <input type="radio" name="${name}" value="true" 
                       ${isTrue ? 'checked' : ''}> O
            </label>
            <label style="margin-right:10px; cursor:pointer;">
                <input type="radio" name="${name}" value="false" 
                       ${isFalse ? 'checked' : ''}> X
            </label>
            <label style="cursor:pointer;">
                <input type="radio" name="${name}" value="null" 
                       ${isNull ? 'checked' : ''}> ?
            </label>
        `;
    },
    
    getAccessIcon: function(value) {
        if (value === true) return '<span style="color:#28a745;">✅</span>';
        if (value === false) return '<span style="color:#dc3545;">❌</span>';
        return '<span style="color:#ffc107;">❓</span>';
    },
    
    // 수정 내용 저장 (여기 수정됨)
    saveEdit: async function() {
        const form = document.getElementById('edit-form');
        if (!form || !mapMain.currentPlace) return;
        
        const updateData = {};
        const fields = ['wheelchair', 'has_elevator', 'has_ramp', 'accessible_toilet'];
        
        fields.forEach(field => {
            const radio = form.querySelector(`input[name="${field}_radio"]:checked`);
            if (radio) {
                // 문자열 'true', 'false', 'null'을 실제 값으로 변환
                if (radio.value === 'true') updateData[field] = true;
                else if (radio.value === 'false') updateData[field] = false;
                else updateData[field] = null;
            }
        });
        
        try {
            const placeId = mapMain.currentPlace.id;
            console.log('수정 요청:', placeId, updateData);
            
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
                console.log('수정 성공:', updated);
                
                Object.assign(mapMain.currentPlace, updated);
                
                const marker = mapMarkers.getCurrentMarker();
                if (marker) {
                    this.showPlaceInfo(mapMain.currentPlace, marker);
                }
                
                mapUI.showMessage('✅ 수정되었습니다');
            } else {
                const error = await response.text();
                console.error('수정 실패:', error);
                alert('수정에 실패했습니다');
            }
        } catch (error) {
            console.error('수정 오류:', error);
            alert('수정 중 오류가 발생했습니다');
        }
    },
    
    cancelEdit: function() {
        const marker = mapMarkers.getCurrentMarker();
        if (mapMain.currentPlace && marker) {
            this.showPlaceInfo(mapMain.currentPlace, marker);
        }
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