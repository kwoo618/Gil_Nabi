// public/map.js (최종 완성 버전)

// 1. 기본 지도 생성
const mapContainer = document.getElementById('map');
const mapOption = {
    center: new kakao.maps.LatLng(35.902153, 128.849080), // 중심좌표 (대구대학교)
    level: 4 // 확대 레벨
};
const map = new kakao.maps.Map(mapContainer, mapOption);

// 2. 서버에서 엑셀 데이터 가져오기
async function getPlacesAndShowMarkers() {
    try {
        const response = await fetch('/api/places'); // 우리 서버에 데이터 요청
        const places = await response.json(); // 응답을 JSON 형태로 변환

        // 3. 가져온 데이터로 마커 생성 및 정보창 추가
        places.forEach(place => {
            // 마커를 생성합니다. (엑셀의 'lat', 'lng' 열 사용)
            const markerPosition = new kakao.maps.LatLng(place.lat, place.lng);
            const marker = new kakao.maps.Marker({
                position: markerPosition
            });

            marker.setMap(map);

            // ✍️ 정보창(인포윈도우)에 표시될 내용 구성
            // 엑셀의 헤더 이름(name, wheelchair 등)을 그대로 사용합니다.
            const content = `
                <div style="padding:10px; font-size:12px; border-radius: 5px; min-width:200px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
                    <div style="font-weight:bold; margin-bottom:5px; font-size: 14px;">${place.name}</div>
                    <hr style="margin: 8px 0; border: 0.5px solid #ddd;">
                    <div>휠체어 접근: ${place.wheelchair ? '✔️ 가능' : '❌ 불가'}</div>
                    <div>경사로: ${place.ramp ? '✔️ 있음' : '❌ 없음'}</div>
                    <div>장애인 화장실: ${place.accessible_toilet ? '✔️ 있음' : '❌ 없음'}</div>
                    <div>엘리베이터: ${place.elevator ? '✔️ 있음' : '❌ 없음'}</div>
                </div>
            `;

            const infowindow = new kakao.maps.InfoWindow({
                content: content,
                removable: true // 닫기 버튼 추가
            });

            // 🖱️ 마커를 클릭하면 정보창이 열리도록 이벤트를 등록합니다.
            kakao.maps.event.addListener(marker, 'click', function() {
                infowindow.open(map, marker);
            });
        });

    } catch (error) {
        console.error('데이터를 가져오는 중 오류가 발생했습니다:', error);
    }
}

// 4. 함수 실행
getPlacesAndShowMarkers();