import os
import requests

class KakaoService:
    """카카오 로컬 API 연동 서비스"""

    def __init__(self):
        self.api_key = os.getenv('KAKAO_RESTAPI_KEY')
        self.headers = {"Authorization": f"KakaoAK {self.api_key}"} if self.api_key else {}

    def get_building_name(self, lat, lng):
        """
        좌표(lat, lng)를 기반으로 건물명 또는 장소명을 찾습니다.
        1. 좌표 -> 주소 변환 (coord2address)
        2. 도로명 주소의 건물명 확인
        3. 없으면 주소 텍스트로 주변(50m) 키워드 검색
        """
        if not self.api_key:
            print("⚠️ KAKAO_RESTAPI_KEY가 설정되지 않았습니다.")
            return None

        try:
            # 1. 좌표 -> 주소 변환
            geo_url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
            params = {"x": lng, "y": lat}
            res = requests.get(geo_url, headers=self.headers, params=params).json()
            
            if not res.get('documents'):
                return None

            document = res['documents'][0]
            road_addr = document.get('road_address')
            address = document.get('address')
            
            # 2. 도로명 주소의 건물명 우선 사용
            if road_addr and road_addr.get('building_name'):
                return road_addr.get('building_name')
            
            # 3. 건물명이 없으면 주소 텍스트로 주변 검색 (radius 50m)
            search_keyword = None
            if road_addr:
                search_keyword = road_addr.get('address_name')
            elif address:
                search_keyword = address.get('address_name')
                
            if search_keyword:
                search_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
                search_params = {"query": search_keyword, "x": lng, "y": lat, "radius": 50}
                search_res = requests.get(search_url, headers=self.headers, params=search_params).json()
                if search_res.get('documents'):
                    return search_res['documents'][0]['place_name']

        except Exception as e:
            print(f"❌ 카카오 API 에러: {e}")
            return None
            
        return None

    def search_keyword(self, query):
        """키워드로 장소 검색 (전국)"""
        if not self.api_key:
            raise Exception("KAKAO_RESTAPI_KEY is not set")
            
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        res = requests.get(url, headers=self.headers, params={"query": query})
        res.raise_for_status() # HTTP 에러 발생 시 예외 처리
        return res.json()