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

// --- 3. 지도 클릭 이벤트 처리 (개선된 2단계 검색 로직) ---
kakao.maps.event.addListener(map, 'click', function(mouseEvent) {
    const latlng = mouseEvent.latLng; // 클릭한 위치의 좌표
    console.log("클릭 좌표:", latlng.toString());

    // 이전 마커 제거
    if (selectedMarker) {
        selectedMarker.setMap(null);
        selectedMarker = null;
    }

    // 1단계: 클릭 좌표로 주소 정보 요청 (Geocoder)
    searchAddrFromCoords(latlng, function(result, status) {
        if (status === kakao.maps.services.Status.OK) {
            const roadAddr = result[0].road_address;
            const jibunAddr = result[0].address;

            // 1-1: 도로명 주소에서 건물 이름 찾기 시도
            if (roadAddr && roadAddr.building_name) {
                const buildingName = roadAddr.building_name;
                const address = roadAddr.address_name || jibunAddr.address_name;
                console.log(`1단계 성공(건물명 O): ${buildingName}. 정확한 위치 찾기 위해 2단계 검색 실행...`);
                // 건물 이름으로 Places 검색하여 정확한 좌표 얻기
                searchPlaceByKeyword(buildingName, latlng); // 키워드와 함께 좌표 전달

            } else {
                // 1-2: 건물 이름은 없지만 주소 정보는 있음 -> 주소로 2단계 검색 시도
                const searchKeyword = roadAddr ? roadAddr.address_name : (jibunAddr ? jibunAddr.address_name : null);
                if (searchKeyword) {
                    console.log(`1단계 실패(건물명 X), 주소로 2단계 검색 시도 (키워드: ${searchKeyword})...`);
                    searchPlaceByKeyword(searchKeyword, latlng); // 주소를 키워드로 장소 검색
                } else {
                    console.log("주소 정보를 찾을 수 없습니다.");
                }
            }

        } else {
            // 1-3: Geocoder 실패 -> Places 주변 검색 시도 (원래 방식)
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
            // 키워드 검색 결과 중 첫 번째 장소 사용
            // TODO: 결과가 여러 개일 경우 클릭 위치와 가장 가까운 것을 선택하는 로직 추가 가능
            const nearestPlace = data[0];
            console.log("키워드 검색 성공:", nearestPlace);
            displayMarkerAndSendData(nearestPlace); // 찾은 장소 정보로 처리

        } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
            console.log(`키워드 '${keyword}' 검색 결과가 없습니다. 주변 검색을 시도합니다.`);
            // 키워드 검색 실패 시 주변 검색으로 fallback
            searchPlaceNearBy(clickLatLng);
        } else {
            console.error('키워드 검색 중 오류 발생:', status);
        }
    }, {
        location: clickLatLng, // 검색 중심 좌표 제한
        radius: 500, // 검색 반경
        sort: kakao.maps.services.SortBy.DISTANCE // 거리순 정렬
    });
}

// --- 5-1. 좌표 주변 장소를 검색하는 함수 (Places 사용 - 키워드 없음) ---
function searchPlaceNearBy(coords) {
    console.log("좌표 주변 장소 검색 중...");
    ps.keywordSearch('', function(data, status, pagination) {
        if (status === kakao.maps.services.Status.OK) {
            const nearestPlace = data[0]; // 가장 가까운 장소 정보
            console.log('주변 검색 성공:', nearestPlace);
            if (nearestPlace.place_name) {
                displayMarkerAndSendData(nearestPlace); // 찾은 장소 정보로 처리
            } else {
                console.warn('주변 검색 성공했으나 place_name이 없습니다:', nearestPlace);
            }
        } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
            console.log('주변 검색 결과가 없습니다.');
        } else {
            console.error('주변 검색 중 오류 발생:', status);
        }
    }, {
        location: coords,
        radius: 200, // 주변 검색 반경
        sort: kakao.maps.services.SortBy.DISTANCE
    });
}


// --- 6. 마커 표시 및 백엔드 전송 함수 (수정됨) ---
function displayMarkerAndSendData(placeInfo) {
    // placeInfo 객체 자체 또는 내부 속성이 유효한지 확인
    if (!placeInfo || !placeInfo.y || !placeInfo.x || !placeInfo.place_name) {
        console.error("displayMarkerAndSendData: 유효하지 않은 placeInfo", placeInfo);
        return; // 함수 종료
    }
    console.log("마커 표시 및 데이터 전송:", placeInfo);

    // 새 선택 마커 생성 (✅ placeInfo의 y, x 좌표 사용)
    selectedMarker = new kakao.maps.Marker({
        position: new kakao.maps.LatLng(placeInfo.y, placeInfo.x),
        title: placeInfo.place_name
    });
    selectedMarker.setMap(map); // 지도에 표시

    // 백엔드로 전송할 데이터 준비 (✅ placeInfo의 y, x 좌표 사용)
    const newPlaceData = {
        building_name: placeInfo.place_name,
        // 카카오 장소 ID가 숫자가 아닐 수 있으므로 문자열로 처리하고, 없으면 대체 ID 사용
        id: String(placeInfo.id || `${placeInfo.address_name}_${placeInfo.place_name}`),
        latitude: parseFloat(placeInfo.y),   // 숫자로 변환
        longitude: parseFloat(placeInfo.x),  // 숫자로 변환
    };

    // ID 유효성 검사 (BigIntegerField는 숫자여야 함)
    // 카카오 ID가 항상 숫자 형태인지 확인 필요. 아니라면 모델 필드를 CharField로 변경 고려.
    if (isNaN(parseInt(newPlaceData.id))) {
         console.warn("ID가 숫자가 아님:", newPlaceData.id, "임시 ID로 대체하거나 모델 필드 변경 필요.");
         // 임시 처리: ID 전송을 막거나, 다른 고유값 사용 (여기선 일단 로그만 남김)
         // return; // ID 문제 시 전송 중단
    } else {
        newPlaceData.id = parseInt(newPlaceData.id); // 정수로 변환 시도
    }

    postNewPlace(newPlaceData, placeInfo); // 백엔드로 전송
}


// --- 7. 백엔드 API POST 요청 함수 (이전과 동일) ---
async function postNewPlace(data, placeInfo) {
    // ID 유효성 검사 추가 (BigIntegerField 에러 방지)
    if (typeof data.id !== 'number' || isNaN(data.id)) {
        console.error("postNewPlace: 유효하지 않은 ID 값입니다. 전송 중단.", data.id);
        alert("장소 ID가 올바르지 않아 저장할 수 없습니다.");
        return;
    }

    console.log("백엔드로 전송할 데이터:", data);
    try {
        const response = await fetch('/api/places/', { /* ... */ });
        if (response.ok) { /* ... */ alert(`"${data.building_name}" 정보가 저장되었습니다!`); }
        else { /* ... */ }
    } catch (error) { /* ... */ }
}

// --- 8. CSRF 토큰 가져오는 함수 (이전과 동일) ---
function getCSRFToken() { /* ... */ return csrftoken; }