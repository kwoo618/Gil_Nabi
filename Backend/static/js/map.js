// Django 템플릿 태그로 생성된 데이터 가져오기
const placesDataElement = document.getElementById('places-data');
const places = placesDataElement ? JSON.parse(placesDataElement.textContent) : [];

// 지도 생성 기본 설정
const container = document.getElementById('map');
const options = {
    center: new kakao.maps.LatLng(35.900, 128.852), // 초기 지도 중심 좌표
    level: 3 // 초기 지도 확대 레벨
};
const map = new kakao.maps.Map(container, options);

// --- 1. 초기 DB 마커 표시 ---
if (places && places.length > 0) {
    places.forEach(function(place) {
        new kakao.maps.Marker({
            position: new kakao.maps.LatLng(place.latitude, place.longitude),
            title: place.building_name
        }).setMap(map);
    });
}

// --- 2. Geocoder와 Places 객체 생성 ---
const geocoder = new kakao.maps.services.Geocoder(); // 주소 <-> 좌표 변환 객체
const ps = new kakao.maps.services.Places();        // 장소 검색 객체
let selectedMarker = null;                          // 현재 선택된 마커
const placeInfoDiv = document.getElementById('place-info'); // 정보 표시 영역

// --- 3. 지도 클릭 이벤트 처리 (개선된 2단계 검색 로직) ---
kakao.maps.event.addListener(map, 'click', function(mouseEvent) {
    const latlng = mouseEvent.latLng; // 클릭한 위치의 좌표
    console.log("클릭 좌표:", latlng.toString());

    // 이전 마커 제거 및 정보창 초기화
    if (selectedMarker) {
        selectedMarker.setMap(null);
        selectedMarker = null;
    }
    placeInfoDiv.innerHTML = '<p>장소 정보를 검색 중입니다...</p>'; // 정보창 초기화

    // 1단계: 클릭 좌표로 주소 정보 요청 (Geocoder)
    searchAddrFromCoords(latlng, function(result, status) {
        if (status === kakao.maps.services.Status.OK) {
            const roadAddr = result[0].road_address;
            const jibunAddr = result[0].address;

            // 1-1: 도로명 주소에서 건물 이름 찾기 시도
            if (roadAddr && roadAddr.building_name) {
                const buildingName = roadAddr.building_name;
                console.log(`1단계 성공(건물명 O): ${buildingName}. 2단계 검색 실행...`);
                searchPlaceByKeyword(buildingName, latlng); // 이름으로 Places 검색

            } else {
                // 1-2: 건물 이름 없지만 주소는 있음 -> 주소로 2단계 검색 시도
                const searchKeyword = roadAddr ? roadAddr.address_name : (jibunAddr ? jibunAddr.address_name : null);
                if (searchKeyword) {
                    console.log(`1단계 실패(건물명 X), 주소로 2단계 검색 (키워드: ${searchKeyword})...`);
                    searchPlaceByKeyword(searchKeyword, latlng);
                } else {
                    console.log("주소 정보를 찾을 수 없습니다.");
                    placeInfoDiv.innerHTML = '<p>주소 정보를 찾을 수 없습니다.</p>';
                }
            }
        } else {
            // 1-3: Geocoder 실패 -> Places 주변 검색 시도
            console.log("좌표로 주소를 검색할 수 없음. Places 주변 검색 시도...");
            searchPlaceNearBy(latlng);
        }
    });
});

// --- 4. 좌표로 주소를 검색하는 함수 (Geocoder 사용) ---
function searchAddrFromCoords(coords, callback) {
    geocoder.coord2Address(coords.getLng(), coords.getLat(), callback);
}

// --- 5. 키워드로 장소를 검색하는 함수 (Places 사용) ---
function searchPlaceByKeyword(keyword, clickLatLng) {
    console.log(`키워드 '${keyword}'로 장소 검색 중...`);
    ps.keywordSearch(keyword, function(data, status, pagination) {
        if (status === kakao.maps.services.Status.OK) {
            const nearestPlace = data[0]; // TODO: 여러 결과 중 거리 비교 로직 추가 가능
            console.log("키워드 검색 성공:", nearestPlace);
            displayMarkerAndInfo(nearestPlace); // 마커 및 정보창 표시
            savePlaceData(nearestPlace); // 백엔드 저장

        } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
            console.log(`키워드 '${keyword}' 검색 결과가 없습니다. 주변 검색을 시도합니다.`);
            searchPlaceNearBy(clickLatLng); // Fallback
        } else {
            console.error('키워드 검색 중 오류 발생:', status);
            placeInfoDiv.innerHTML = `<p>키워드('${keyword}') 검색 중 오류 발생: ${status}</p>`;
        }
    }, { location: clickLatLng, radius: 20, sort: kakao.maps.services.SortBy.DISTANCE });
}

// --- 5-1. 좌표 주변 장소를 검색하는 함수 (Places 사용 - 키워드 없음) ---
function searchPlaceNearBy(coords) {
    console.log("좌표 주변 장소 검색 중...");
    ps.keywordSearch('', function(data, status, pagination) {
        if (status === kakao.maps.services.Status.OK) {
            const nearestPlace = data[0];
            console.log('주변 검색 성공:', nearestPlace);
            if (nearestPlace.place_name) {
                displayMarkerAndInfo(nearestPlace); // 마커 및 정보창 표시
                savePlaceData(nearestPlace); // 백엔드 저장
            } else {
                console.warn('주변 검색 성공했으나 place_name이 없습니다:', nearestPlace);
                placeInfoDiv.innerHTML = '<p>주변 장소를 찾았지만 이름 정보가 없습니다.</p>';
            }
        } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
            console.log('주변 검색 결과가 없습니다.');
            placeInfoDiv.innerHTML = '<p>클릭한 위치 주변에 등록된 장소가 없습니다.</p>';
        } else {
            console.error('주변 검색 중 오류 발생:', status);
            placeInfoDiv.innerHTML = `<p>주변 검색 중 오류 발생: ${status}</p>`;
        }
    }, { location: coords, radius: 200, sort: kakao.maps.services.SortBy.DISTANCE });
}

// --- 6. 마커 표시 및 정보창 업데이트 함수 ---
function displayMarkerAndInfo(placeInfo) {
    if (!placeInfo || !placeInfo.y || !placeInfo.x || !placeInfo.place_name) { /* ... 유효성 검사 ... */ return; }
    console.log("마커 및 정보 표시:", placeInfo);

    selectedMarker = new kakao.maps.Marker({
        position: new kakao.maps.LatLng(placeInfo.y, placeInfo.x), // ✅ 찾은 장소 좌표 사용
        title: placeInfo.place_name
    });
    selectedMarker.setMap(map);

    // 정보창 내용 업데이트
    placeInfoDiv.innerHTML = `
        <h3>${placeInfo.place_name}</h3>
        <p><strong>주소:</strong> ${placeInfo.address_name || '정보 없음'}</p>
        <p><strong>카테고리:</strong> ${placeInfo.category_name || '정보 없음'}</p>
        <p><strong>좌표:</strong> ${placeInfo.y}, ${placeInfo.x}</p>
        <p><strong>카카오 ID:</strong> ${placeInfo.id || '정보 없음'}</p>
    `;
}

// --- 6-1. 백엔드 데이터 저장 함수 ---
function savePlaceData(placeInfo){
     const newPlaceData = {
        building_name: placeInfo.place_name,
        id: String(placeInfo.id || `${placeInfo.address_name}_${placeInfo.place_name}`), // ID 처리 (문자열로)
        latitude: parseFloat(placeInfo.y),
        longitude: parseFloat(placeInfo.x),
    };
    // 백엔드 API로 데이터 전송
    postNewPlace(newPlaceData);
}

// --- 7. 백엔드 API POST 요청 함수 ---
async function postNewPlace(data) {
    // 임시: ID를 문자열로 보내도록 허용 (백엔드 모델 ID 필드 CharField 추천)
    data.id = String(data.id);

    console.log("백엔드로 전송할 데이터:", data);
    try {
        const response = await fetch('/api/places/', { /* ... */ });
        if (response.ok) {
             const savedData = await response.json();
             console.log('백엔드 저장 성공:', savedData);
             // alert(`"${data.building_name}" 정보가 저장되었습니다!`); // 성공 알림 필요시 활성화
         } else { /* ... 실패 처리 ... */ }
    } catch (error) { /* ... */ }
}

// --- 8. CSRF 토큰 가져오는 함수 ---
function getCSRFToken() { /* ... */ return csrftoken; }