import os
import requests

def get_kakao_building_name(lat, lng):
    """
    좌표(lat, lng)를 이용하여 카카오 API를 통해 건물 이름을 찾습니다.
    """
    kakao_api_key = os.getenv('KAKAO_RESTAPI_KEY')
    if not kakao_api_key:
        return None

    try:
        headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
        
        # 1단계: 좌표 -> 주소 변환
        geo_url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
        geo_params = {"x": lng, "y": lat}
        res = requests.get(geo_url, headers=headers, params=geo_params).json()
        
        found_name = None
        
        if res.get('documents'):
            road_addr = res['documents'][0].get('road_address')
            if road_addr and road_addr.get('building_name'):
                found_name = road_addr.get('building_name')
            
            if not found_name:
                # 2단계: 주소 키워드 검색
                search_keyword = road_addr.get('address_name') if road_addr else res['documents'][0]['address']['address_name']
                if search_keyword:
                    search_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
                    search_params = {"query": search_keyword, "x": lng, "y": lat, "radius": 50}
                    search_res = requests.get(search_url, headers=headers, params=search_params).json()
                    if search_res.get('documents'):
                        found_name = search_res['documents'][0]['place_name']
        
        return found_name
    except Exception as e:
        print(f"❌ 카카오 API 에러: {e}")
        return None