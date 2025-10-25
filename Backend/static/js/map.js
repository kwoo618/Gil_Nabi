// kakao.maps.load(): 카카오맵 SDK 로딩 및 초기화가 완료되면 이 함수 안의 코드를 실행합니다.
kakao.maps.load(function() {

    // --- 지도 생성 기본 설정 ---
    const container = document.getElementById('map');
    const options = {
        center: new kakao.maps.LatLng(35.900, 128.852), // 초기 지도 중심 좌표
        level: 3 // 초기 지도 확대 레벨
    };
    const map = new kakao.maps.Map(container, options);

    // --- 초기 DB 마커 표시 로직은 제거됨 ---

    // --- Geocoder와 Places 객체 생성 ---
    const geocoder = new kakao.maps.services.Geocoder();
    const ps = new kakao.maps.services.Places();
    let selectedMarker = null;
    const placeInfoDiv = document.getElementById('place-info'); // 정보 표시 영역
    let currentPlaceData = null; // 현재 선택된 장소 데이터

    // --- 지도 클릭 이벤트 처리 ---
    kakao.maps.event.addListener(map, 'click', async function(mouseEvent) { // async 추가
        const latlng = mouseEvent.latLng;
        console.log("클릭 좌표:", latlng.toString());

        // 이전 마커 제거 및 정보창 초기화
        if (selectedMarker) { selectedMarker.setMap(null); selectedMarker = null; }
        placeInfoDiv.innerHTML = '<p>장소 정보를 검색 중입니다...</p>';

        try {
            // Geocoder와 Places 검색 로직 실행
            const placeInfo = await findPlaceInfo(latlng);

            if (placeInfo) {
                console.log("최종 찾은 장소:", placeInfo);
                await checkAndDisplayPlaceDetails(placeInfo); // await 추가
            } else {
                console.log("최종적으로 장소를 찾지 못함.");
                placeInfoDiv.innerHTML = '<p>클릭한 위치에서 장소를 찾을 수 없습니다.</p>';
            }
        } catch (error) {
            console.error("장소 검색/처리 중 오류:", error);
            placeInfoDiv.innerHTML = '<p>장소 검색 중 오류가 발생했습니다.</p>';
        }
    });

    // --- Geocoder/Places 검색 로직 함수 (Promise 반환) ---
    async function findPlaceInfo(latlng) {
        // 1단계: Geocoder 시도
        try {
            const geocodeResult = await new Promise((resolve, reject) => {
                searchAddrFromCoords(latlng, (result, status) => {
                    if (status === kakao.maps.services.Status.OK) resolve(result);
                    else reject(status);
                });
            });

            const roadAddr = geocodeResult[0].road_address;
            const jibunAddr = geocodeResult[0].address;

            if (roadAddr && roadAddr.building_name) { // 건물명 찾음 -> 이름으로 Places 검색
                console.log(`Geocoder 성공(건물명:${roadAddr.building_name}). Places 검색 실행...`);
                return await searchPlaceByKeyword(roadAddr.building_name, latlng);
            } else { // 주소만 찾음 -> 주소로 Places 검색
                const searchKeyword = roadAddr ? roadAddr.address_name : (jibunAddr ? jibunAddr.address_name : null);
                if (searchKeyword) {
                    console.log(`Geocoder 성공(주소:${searchKeyword}). Places 검색 실행...`);
                    return await searchPlaceByKeyword(searchKeyword, latlng);
                }
            }
        } catch (geocodeStatus) {
            // Geocoder 실패 또는 주소 없음 -> Places 주변 검색 시도
            console.log(`Geocoder 실패 (${geocodeStatus}). Places 주변 검색 실행...`);
            try {
                return await searchPlaceNearBy(latlng);
            } catch(placeStatus) {
                console.log(`Places 주변 검색도 실패 (${placeStatus}).`);
                return null;
            }
        }
        // Geocoder 성공했지만 키워드 못 찾은 경우 등 예외 처리
        console.log("findPlaceInfo: 주소는 찾았으나 Places 검색으로 이어지지 못함.");
        return null;
    }

    // --- 좌표 -> 주소 검색 함수 ---
    function searchAddrFromCoords(coords, callback) {
        geocoder.coord2Address(coords.getLng(), coords.getLat(), callback);
    }

    // --- 키워드 -> 장소 검색 함수 (Promise 반환) ---
    function searchPlaceByKeyword(keyword, clickLatLng) {
        console.log(`키워드 '${keyword}' 검색 중...`);
        return new Promise((resolve, reject) => {
            ps.keywordSearch(keyword, function(data, status, pagination) {
                if (status === kakao.maps.services.Status.OK && data.length > 0) {
                    resolve(data[0]); // 성공 시 첫 번째 결과 resolve
                } else {
                    reject(status); // 실패 시 상태 reject (ZERO_RESULT 등)
                }
            }, { location: clickLatLng, radius: 500, sort: kakao.maps.services.SortBy.DISTANCE });
        });
    }

    // --- 좌표 주변 장소 검색 함수 (Promise 반환) ---
    function searchPlaceNearBy(coords) {
        console.log("좌표 주변 검색 중...");
        return new Promise((resolve, reject) => {
            ps.keywordSearch('', function(data, status, pagination) {
                if (status === kakao.maps.services.Status.OK && data.length > 0 && data[0].place_name) {
                    resolve(data[0]);
                } else {
                     if (status === kakao.maps.services.Status.OK) {
                         console.warn('주변 검색 성공했으나 place_name 없음:', data[0]);
                         reject('NO_PLACE_NAME');
                     } else {
                         reject(status);
                     }
                }
            }, { location: coords, radius: 200, sort: kakao.maps.services.SortBy.DISTANCE });
        });
    }

    // --- 백엔드 확인 및 정보 표시/저장 함수 ---
    async function checkAndDisplayPlaceDetails(placeInfo) {
        if (!placeInfo || !placeInfo.id) { /* ... */ return; }
        const kakaoPlaceId = String(placeInfo.id);
        console.log(`백엔드에서 ID ${kakaoPlaceId} 확인 중 (Search)...`); // 로그 수정
        try {
            const response = await fetch(`/api/places/?search=${kakaoPlaceId}`);
            if (response.ok) {
                const results = await response.json();
                if (results.length > 0) { // DB 존재
                    currentPlaceData = results[0];
                    console.log("DB 존재:", currentPlaceData);
                    displayMarkerAndInfo(currentPlaceData);
                } else { // 신규
                    currentPlaceData = placeInfo;
                    console.log("DB 없음. 카카오 정보 사용 및 저장 시도.");
                    displayMarkerAndInfo(placeInfo);
                    savePlaceData(placeInfo);
                }
            } else {
                 console.error("백엔드 장소 확인 API 오류:", response.status);
                 placeInfoDiv.innerHTML = `<p>서버 장소 확인 오류 (${response.status})</p>`;
            }
        } catch (error) {
            console.error("백엔드 장소 확인 중 네트워크 오류:", error);
            placeInfoDiv.innerHTML = '<p>서버 통신 오류.</p>';
        }
    }

    // --- 마커 표시 및 정보창 업데이트 함수 ---
    function displayMarkerAndInfo(placeData) {
        // 유효성 검사
        if (!placeData || !(placeData.y || placeData.latitude) || !(placeData.x || placeData.longitude) || !(placeData.place_name || placeData.building_name)) {
             console.error("displayMarkerAndInfo: 유효하지 않음", placeData);
             placeInfoDiv.innerHTML = '<p>장소 정보 표시 불가.</p>';
             return;
        }
        const placeName = placeData.place_name || placeData.building_name;
        const latitude = parseFloat(placeData.y || placeData.latitude);
        const longitude = parseFloat(placeData.x || placeData.longitude);
        if (isNaN(latitude) || isNaN(longitude)) {
            console.error("displayMarkerAndInfo: 좌표 오류", placeData);
            placeInfoDiv.innerHTML = '<p>장소 정보 표시 불가 (좌표 오류).</p>';
            return;
        }

        console.log("마커 및 정보 표시:", placeData);

        // 마커 생성 및 표시
        selectedMarker = new kakao.maps.Marker({
             position: new kakao.maps.LatLng(latitude, longitude),
             title: placeName
        });
        selectedMarker.setMap(map);

        // 접근성 정보 raw 값 표시 함수
        function getAccessibilityRawValue(value) {
            if (value === true) return 'true';
            if (value === false) return 'false';
            return 'null';
        }

        // 정보창 업데이트
        placeInfoDiv.innerHTML = `
            <h3>${placeName}</h3>
            <p><strong>주소:</strong> ${placeData.address_name || placeData.address || '정보 없음'}</p>
            <p><strong>ID:</strong> ${placeData.id || '정보 없음'}</p>
            <hr>
            <h4>접근성 정보: <button id="edit-btn">수정</button></h4>
            <div id="accessibility-info">
                <p>경사로: ${getAccessibilityRawValue(placeData.has_ramp)}</p>
                <p>휠체어: ${getAccessibilityRawValue(placeData.wheelchair)}</p>
                <p>화장실: ${getAccessibilityRawValue(placeData.accessible_toilet)}</p>
                <p>엘리베이터: ${getAccessibilityRawValue(placeData.has_elevator)}</p>
            </div>
        `;
        document.getElementById('edit-btn').addEventListener('click', showEditForm);
    }

    // --- 수정 폼 보여주는 함수 ---
    function showEditForm() {
        if (!currentPlaceData) return;
        console.log("수정 폼 표시 (현재 데이터):", currentPlaceData);

        // 라디오 버튼 생성 함수
        function createRadioButtons(fieldName, currentValue) {
            const isTrue = currentValue === true;
            const isFalse = currentValue === false;
            const isNull = currentValue === null || typeof currentValue === 'undefined';

            return `
                <label><input type="radio" name="${fieldName}" value="true" ${isTrue ? 'checked' : ''}> O </label>
                <label><input type="radio" name="${fieldName}" value="false" ${isFalse ? 'checked' : ''}> X </label>
                <label><input type="radio" name="${fieldName}" value="null" ${isNull ? 'checked' : ''}> ? </label>
            `;
        }

        // 수정 폼 HTML
        placeInfoDiv.innerHTML = `
            <h3>${currentPlaceData.place_name || currentPlaceData.building_name} - 수정</h3>
            <form id="edit-form">
                <p>경사로: ${createRadioButtons('has_ramp', currentPlaceData.has_ramp)}</p>
                <p>휠체어: ${createRadioButtons('wheelchair', currentPlaceData.wheelchair)}</p>
                <p>화장실: ${createRadioButtons('accessible_toilet', currentPlaceData.accessible_toilet)}</p>
                <p>엘리베이터: ${createRadioButtons('has_elevator', currentPlaceData.has_elevator)}</p>
                <button type="button" id="save-btn">저장</button>
                <button type="button" id="cancel-btn">취소</button>
            </form>
        `;
        document.getElementById('save-btn').addEventListener('click', handleSaveClick);
        document.getElementById('cancel-btn').addEventListener('click', () => displayMarkerAndInfo(currentPlaceData));
    }

    // --- 저장 버튼 클릭 처리 함수 (PATCH 요청) ---
    async function handleSaveClick() {
        if (!currentPlaceData || !currentPlaceData.id) { return; }
        const form = document.getElementById('edit-form');
        const updateData = {};
        const fields = ['has_ramp', 'wheelchair', 'accessible_toilet', 'has_elevator'];
        fields.forEach(field => {
            const selectedValue = form.elements[field].value;
            updateData[field] = selectedValue === 'null' ? null : (selectedValue === 'true');
        });

        console.log("저장할 데이터:", updateData);
        const placeId = String(currentPlaceData.id);

        try {
            const response = await fetch(`/api/places/${placeId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(updateData)
            });
            if (response.ok) {
                const savedData = await response.json();
                console.log('백엔드 업데이트 성공:', savedData);
                alert('업데이트 성공!');
                currentPlaceData = savedData;
                displayMarkerAndInfo(currentPlaceData);
            } else {
                 const errorData = await response.json();
                 console.error('백엔드 업데이트 실패:', response.status, errorData);
                 alert(`업데이트 실패: ${JSON.stringify(errorData)}`);
            }
        } catch (error) {
            console.error('업데이트 중 네트워크 오류:', error);
            alert('서버 통신 오류.');
        }
    }


    // --- 백엔드 데이터 저장 함수 (신규 장소용) ---
function savePlaceData(placeInfo){
     // 🚨 placeInfo 객체 자체와 내부 속성이 유효한지 다시 한번 확인
     if (!placeInfo || !placeInfo.id || !placeInfo.place_name || !placeInfo.y || !placeInfo.x) {
         console.error("savePlaceData: placeInfo 객체에 필수 정보가 부족합니다.", placeInfo);
         alert("장소 정보를 DB에 저장할 수 없습니다 (정보 부족).");
         return; // 저장 시도 중단
     }

     const newPlaceData = {
        // building_name 필드 확인
        building_name: placeInfo.place_name,
        // id 필드 확인 (문자열로)
        id: String(placeInfo.id), // 대체 ID 로직은 잠시 제거하고 카카오 ID만 사용
        // latitude 필드 확인 (숫자로)
        latitude: parseFloat(placeInfo.y),
        // longitude 필드 확인 (숫자로)
        longitude: parseFloat(placeInfo.x),
        // 🚨 접근성 필드는 보내지 않음 (백엔드 기본값 null 사용)
    };

    // 🚨 전송 전 데이터 유효성 재확인 (특히 숫자 변환 후 NaN이 아닌지)
    if (isNaN(newPlaceData.latitude) || isNaN(newPlaceData.longitude)) {
        console.error("savePlaceData: 위도 또는 경도 변환 실패.", placeInfo);
        alert("좌표값이 올바르지 않아 저장할 수 없습니다.");
        return;
    }
    // 🚨 ID가 빈 문자열이 아닌지 확인
    if (!newPlaceData.id) {
         console.error("savePlaceData: ID 값이 비어있습니다.", placeInfo);
         alert("장소 ID가 없어 저장할 수 없습니다.");
         return;
    }

    // 데이터 전송 함수 호출
    postNewPlace(newPlaceData);
}

// --- 백엔드 API POST 요청 함수 (신규 장소용) ---
async function postNewPlace(data) {
    // 🚨 data 객체 자체 확인
    if (!data || !data.id || !data.building_name || data.latitude == null || data.longitude == null ) {
         console.error("postNewPlace: 전송할 데이터 객체가 유효하지 않습니다.", data);
         alert("저장할 데이터가 올바르지 않습니다.");
         return;
    }

    // ID는 문자열로 전송 (백엔드 CharField 가정)
    data.id = String(data.id);

    console.log("백엔드로 전송할 최종 데이터:", data); // 최종 데이터 확인 로그

    try {
        const response = await fetch('/api/places/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            // 🚨 JSON 변환 확인
            body: JSON.stringify(data)
        });

        if (response.ok) {
            currentPlaceData = await response.json();
            console.log('백엔드 신규 저장 성공:', currentPlaceData);
        } else {
            const errorData = await response.json(); // 에러 응답 내용 확인
            console.warn('신규 저장 실패:', response.status, errorData); // 상태 코드와 내용 함께 출력

            // 에러 메시지를 alert로 보여주기 (더 상세하게)
            let errorMessage = `저장 실패 (${response.status}):\n`;
            for (const field in errorData) {
                errorMessage += `${field}: ${errorData[field].join(', ')}\n`;
            }
            alert(errorMessage);

            if (response.status === 400 && errorData.id && errorData.id.some(err => err.includes('already exists'))) {
                 console.log('이미 등록된 장소입니다.');
                 // 필요시 이미 등록된 장소 정보를 다시 로드하는 로직 추가
                 // fetch(`/api/places/?id=${data.id}`).then(...)
            }
        }
    } catch (error) {
        console.error('네트워크 오류:', error);
        alert('서버와 통신 중 오류가 발생했습니다.');
    }
}

    // --- CSRF 토큰 함수 ---
    function getCSRFToken() {
        let csrftoken = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(cookie => {
                let parts = cookie.trim().split('=');
                if (parts[0] === 'csrftoken') {
                    csrftoken = parts[1];
                }
            });
        }
        return csrftoken;
    }

    // --- DB 데이터 보기 버튼 이벤트 리스너 ---
    const showDbBtn = document.getElementById('show-db-btn');
    if (showDbBtn) {
        // 접근성 정보 O, X, ? 변환 함수
        function getAccessibilitySymbol(value) {
            if (value === true) return '✅';
            if (value === false) return '❌';
            return '❓';
        }

        showDbBtn.addEventListener('click', async function() {
            console.log("DB 데이터 로딩 시도...");
            placeInfoDiv.innerHTML = '<p>DB 데이터를 불러오는 중...</p>';
            try {
                const response = await fetch('/api/places/');
                if (response.ok) {
                    const allPlaces = await response.json();
                    if (allPlaces.length > 0) {
                        let htmlContent = '<h3>데이터베이스 장소 목록</h3><ul>';
                        allPlaces.forEach(place => {
                            htmlContent += `
                                <li>
                                    <strong>${place.building_name}</strong> (ID: ${place.id})<br>
                                    좌표: ${place.latitude}, ${place.longitude}<br>
                                    접근성:
                                    R:${getAccessibilitySymbol(place.has_ramp)} |
                                    W:${getAccessibilitySymbol(place.wheelchair)} |
                                    T:${getAccessibilitySymbol(place.accessible_toilet)} |
                                    E:${getAccessibilitySymbol(place.has_elevator)}
                                </li>
                                <hr>
                            `;
                        });
                        htmlContent += '</ul>';
                        placeInfoDiv.innerHTML = htmlContent;
                    } else { placeInfoDiv.innerHTML = '<p>DB에 저장된 장소가 없습니다.</p>'; }
                } else { /* ... API 오류 처리 ... */ }
            } catch (error) { /* ... 네트워크 오류 처리 ... */ }
        });
    }

}); // kakao.maps.load() 함수의 끝