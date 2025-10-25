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
        console.log("findPlaceInfo: 주소는 찾았으나 Places 검색으로 이어지지 못함.");
        return null;
    }

    // --- 좌표 -> 주소 검색 함수 ---
    function searchAddrFromCoords(coords, callback) {
        geocoder.coord2Address(coords.getLng(), coords.getLat(), callback);
    }

    // --- 키워드 -> 장소 검색 함수 (Promise 반환) ---
    function searchPlaceByKeyword(keyword, centerLatLng = null) { // centerLatLng를 선택적 인자로 변경
        console.log(`키워드 '${keyword}' 검색 중...` + (centerLatLng ? ` 중심:[${centerLatLng.toString()}]` : ' (전국)'));

        // ✨ 검색 옵션 객체 동적 생성
        const searchOptions = {
            // category_group_code: 'SC4' // 필요시 카테고리 필터 추가 가능
        };
        if (centerLatLng) { // 중심 좌표가 주어졌을 때만 위치 기반 옵션 추가
            searchOptions.location = centerLatLng;
            searchOptions.radius = 500; // 또는 적절한 반경
            searchOptions.sort = kakao.maps.services.SortBy.DISTANCE;
        }

        return new Promise((resolve, reject) => {
            ps.keywordSearch(keyword, function(data, status, pagination) {
                if (status === kakao.maps.services.Status.OK) { // ✨ data.length > 0 조건 제거
                    resolve(data); // ✨ 성공 시 검색된 데이터 배열 전체(data)를 resolve
                } else {
                    reject(status);
                }
            }, searchOptions);
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

    // --- 백엔드 확인 및 정보 표시/저장 함수 (수정됨: Detail API 사용) ---
    async function checkAndDisplayPlaceDetails(placeInfo) {
        if (!placeInfo || !placeInfo.id) {
            console.error("checkAndDisplayPlaceDetails: 유효하지 않은 placeInfo (ID 없음)", placeInfo);
            placeInfoDiv.innerHTML = '<p>장소 정보를 가져오는데 실패했습니다 (ID 없음).</p>';
            return;
        }
        const kakaoPlaceId = String(placeInfo.id);
        console.log(`백엔드에서 ID ${kakaoPlaceId} 확인 중...`);
        try {
            // ✨ Detail API 주소로 GET 요청 시도
            const response = await fetch(`/api/places/${kakaoPlaceId}/`); // <- Detail API 주소 사용!

            if (response.ok) {
                 // --- 장소가 DB에 이미 존재할 때 ---
                const existingPlaceData = await response.json(); // 상세 API는 객체 하나만 반환
                console.log("DB 존재:", existingPlaceData);
                currentPlaceData = existingPlaceData;
                displayMarkerAndInfo(existingPlaceData); // DB 데이터(접근성 포함)로 표시

            } else if (response.status === 404) {
                 // --- 장소가 DB에 없을 때 (신규 장소) ---
                 console.log("DB 없음 (404). 카카오 정보 사용 및 저장 시도.");
                 currentPlaceData = placeInfo;
                 displayMarkerAndInfo(placeInfo); // 카카오 정보로 표시 (접근성은 ??)
                 savePlaceData(placeInfo); // DB에 저장
            } else {
                // 기타 서버 오류 (500 등)
                console.error("백엔드 장소 확인/조회 API 오류:", response.status);
                placeInfoDiv.innerHTML = `<p>서버 장소 확인 오류 (${response.status})</p>`;
            }
        } catch (error) {
            console.error("백엔드 장소 확인/조회 중 네트워크 오류:", error);
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
        const newPlaceData = {
            building_name: placeInfo.place_name,
            id: String(placeInfo.id || `${placeInfo.address_name}_${placeInfo.place_name}`),
            latitude: parseFloat(placeInfo.y),
            longitude: parseFloat(placeInfo.x),
        };
        postNewPlace(newPlaceData);
    }

    // --- 백엔드 API POST 요청 함수 (신규 장소용) ---
    async function postNewPlace(data) {
        data.id = String(data.id);
        console.log("백엔드로 전송할 데이터 (신규):", data);
        try {
            const response = await fetch('/api/places/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(data)
            });
            if (response.ok) {
                currentPlaceData = await response.json(); // 신규 저장 후 currentPlaceData 업데이트
                console.log('백엔드 신규 저장 성공:', currentPlaceData);
            } else {
                const errorData = await response.json();
                console.warn('신규 저장 실패:', response.status, errorData);
                if (response.status === 400 && errorData.id && errorData.id.some(err => err.includes('already exists'))) {
                     console.log('이미 등록된 장소입니다.');
                     // 필요시 이미 등록된 장소 정보를 다시 로드
                     // 예: checkAndDisplayPlaceDetails({id: data.id}); // 카카오 정보 대신 ID만 넘겨 재조회
                } else {
                     let errorMessage = `저장 실패 (${response.status}):\n`;
                     for (const field in errorData) {
                         errorMessage += `${field}: ${errorData[field].join(', ')}\n`;
                     }
                     alert(errorMessage);
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
                                    좌표: ${place.latitude.toFixed(6)}, ${place.longitude.toFixed(6)}<br>
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
                } else {
                    console.error("DB 데이터 로딩 API 오류:", response.status);
                    placeInfoDiv.innerHTML = `<p>DB 데이터 로딩 중 오류 발생 (${response.status})</p>`;
                }
            } catch (error) {
                console.error("DB 데이터 로딩 중 네트워크 오류:", error);
                placeInfoDiv.innerHTML = '<p>서버 통신 오류.</p>';
            }
        });
    }

    // ==========================================================
    // ✨ 14. 장소 검색 버튼 이벤트 리스너 (수정됨: async/await 추가)
    // ==========================================================
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    console.log("검색 입력창:", searchInput);
    console.log("검색 버튼:", searchBtn);

    if (searchInput && searchBtn) {
        console.log("검색 버튼 이벤트 리스너 추가 시도...");
        searchBtn.addEventListener('click', handleSearch); // 함수 이름만 전달
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
        console.log("검색 버튼 이벤트 리스너 추가 완료.");
    } else {
        console.error("검색 입력창(#search-input) 또는 버튼(#search-btn)을 찾을 수 없습니다.");
    }

    // --- 15. 검색 실행 함수 (수정됨: 카카오 API 우선 호출) ---
    async function handleSearch() {
        console.log("Search button clicked!");
        const query = searchInput.value.trim();
        if (!query) { alert('검색어를 입력하세요.'); return; }
        console.log(`카카오맵 API '${query}' 검색 시도...`);
        placeInfoDiv.innerHTML = `<p>'${query}' 검색 중...</p>`;
        if (selectedMarker) { selectedMarker.setMap(null); selectedMarker = null; }

        try {
            // ✨ 백엔드 대신 카카오 API 검색 함수 호출 (전국 단위)
            const kakaoResults = await searchPlaceByKeyword(query); // await 사용

            if (kakaoResults && kakaoResults.length > 0) { // 카카오 결과가 있으면
                console.log("카카오 검색 결과:", kakaoResults);
                // ✨ 카카오 검색 결과를 표시하는 함수 호출 (이름 변경)
                displayKakaoSearchResults(kakaoResults, query);
            } else {
                // 카카오 API 검색 결과도 없는 경우
                console.log(`카카오맵 API '${query}' 검색 결과 없음.`);
                placeInfoDiv.innerHTML = `<p>'${query}'에 대한 검색 결과가 없습니다.</p>`;
            }
        } catch (errorStatus) {
            // 카카오 API 검색 중 오류 발생 (ZERO_RESULT 포함될 수 있음)
            console.error(`카카오 외부 검색 실패: ${errorStatus}`);
            if (errorStatus === kakao.maps.services.Status.ZERO_RESULT) {
                placeInfoDiv.innerHTML = `<p>'${query}'에 대한 검색 결과가 없습니다.</p>`;
            } else {
                placeInfoDiv.innerHTML = `<p>'${query}' 외부 검색 중 오류 발생: ${errorStatus}</p>`;
            }
        }
    }

    // --- 16. 카카오 검색 결과 목록 표시 함수 (수정됨) ---
    function displayKakaoSearchResults(kakaoResults, query) { // 이름 변경
        let htmlContent = `<h3>'${query}' 카카오맵 검색 결과</h3><ul>`;
        kakaoResults.forEach((place, index) => {
            // 각 결과를 리스트 항목으로 만들고, 클릭 시 처리할 함수 연결 준비
            htmlContent += `
                <li style="cursor: pointer;" data-place-index="${index}">
                    <strong>${place.place_name}</strong> (${place.category_name})<br>
                    <small>${place.address_name}</small>
                    <small> | 좌표: ${parseFloat(place.y).toFixed(6)}, ${parseFloat(place.x).toFixed(6)}</small>
                </li>
                <hr>
            `;
        });
        htmlContent += '</ul>';
        placeInfoDiv.innerHTML = htmlContent;

        // 각 검색 결과 항목(li)에 클릭 이벤트 리스너 추가
        placeInfoDiv.querySelectorAll('li').forEach(item => {
            item.addEventListener('click', async function() { // async 추가
                const index = parseInt(this.getAttribute('data-place-index'));
                const selectedKakaoPlace = kakaoResults[index]; // 클릭된 카카오 장소 데이터
                console.log("카카오 검색 결과 선택:", selectedKakaoPlace);

                // 지도 이동
                const moveLatLng = new kakao.maps.LatLng(selectedKakaoPlace.y, selectedKakaoPlace.x);
                map.panTo(moveLatLng);

                // ✨ 선택된 카카오 정보를 가지고 DB 확인 및 최종 표시 함수 호출
                await checkAndDisplayPlaceDetails(selectedKakaoPlace); // await 추가
            });
        });
    }

}); // kakao.maps.load() 함수의 끝