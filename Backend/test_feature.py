"""
프론트엔드 기능 테스트 스크립트
각 JS 모듈의 실제 동작 테스트
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class FrontendFunctionTest:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/places/test/"
        self.test_results = []
        
    def setup_driver(self):
        """웹드라이버 설정"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 백그라운드 실행
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            print("✅ Chrome 드라이버 초기화")
            return True
        except:
            print("❌ Chrome 드라이버 설치 필요")
            print("   pip install selenium")
            print("   ChromeDriver 다운로드: https://chromedriver.chromium.org/")
            return False
            
    def test_map_initialization(self):
        """지도 초기화 테스트"""
        print("\n🧪 지도 초기화 테스트")
        
        try:
            self.driver.get(self.base_url)
            time.sleep(3)  # 지도 로딩 대기
            
            # 지도 객체 확인
            result = self.driver.execute_script("return typeof mapMain.map !== 'undefined';")
            
            if result:
                print("✅ 지도 초기화 성공")
                self.test_results.append(("지도 초기화", True))
            else:
                print("❌ 지도 초기화 실패")
                self.test_results.append(("지도 초기화", False))
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            self.test_results.append(("지도 초기화", False))
            
    def test_filter_functionality(self):
        """필터 기능 테스트"""
        print("\n🧪 필터 기능 테스트")
        
        try:
            # 휠체어 필터 체크
            self.driver.execute_script("""
                document.getElementById('wheelchair').checked = true;
                mapFilter.updateFilters();
            """)
            
            # 필터 상태 확인
            filter_state = self.driver.execute_script("return mapMain.currentFilters;")
            
            if filter_state['wheelchair']:
                print("✅ 필터 업데이트 성공")
                print(f"   필터 상태: {filter_state}")
                self.test_results.append(("필터 기능", True))
            else:
                print("❌ 필터 업데이트 실패")
                self.test_results.append(("필터 기능", False))
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            self.test_results.append(("필터 기능", False))
            
    def test_click_functionality(self):
        """클릭 기능 테스트"""
        print("\n🧪 지도 클릭 기능 테스트")
        
        try:
            # 테스트 좌표로 클릭 시뮬레이션
            result = self.driver.execute_script("""
                const testLatlng = new kakao.maps.LatLng(35.8959, 128.8502);
                mapClick.handleMapClick(testLatlng);
                return true;
            """)
            
            time.sleep(2)  # API 응답 대기
            
            if result:
                print("✅ 클릭 이벤트 처리 성공")
                self.test_results.append(("클릭 기능", True))
            else:
                print("❌ 클릭 이벤트 처리 실패")
                self.test_results.append(("클릭 기능", False))
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            self.test_results.append(("클릭 기능", False))
            
    def test_search_functionality(self):
        """검색 기능 테스트"""
        print("\n🧪 검색 기능 테스트")
        
        try:
            # 검색어 입력 및 검색 실행
            self.driver.execute_script("""
                document.getElementById('search-input').value = '공학';
                mapSearch.search();
            """)
            
            time.sleep(2)  # API 응답 대기
            
            # 마커 확인
            marker_count = self.driver.execute_script("return mapMain.markers.length;")
            
            if marker_count > 0:
                print(f"✅ 검색 성공: {marker_count}개 마커")
                self.test_results.append(("검색 기능", True))
            else:
                print("❌ 검색 결과 없음")
                self.test_results.append(("검색 기능", False))
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            self.test_results.append(("검색 기능", False))
            
    def test_db_view(self):
        """DB 보기 기능 테스트"""
        print("\n🧪 DB 보기 기능 테스트")
        
        try:
            self.driver.execute_script("mapUI.showDBInfo();")
            time.sleep(2)
            
            # 결과 영역 확인
            results_html = self.driver.execute_script(
                "return document.getElementById('results').innerHTML;"
            )
            
            if "데이터베이스 현황" in results_html:
                print("✅ DB 정보 표시 성공")
                self.test_results.append(("DB 보기", True))
            else:
                print("❌ DB 정보 표시 실패")
                self.test_results.append(("DB 보기", False))
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            self.test_results.append(("DB 보기", False))
            
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "=" * 50)
        print("🚀 프론트엔드 기능 테스트 시작")
        print("=" * 50)
        
        if not self.setup_driver():
            return
            
        try:
            self.test_map_initialization()
            self.test_filter_functionality()
            self.test_click_functionality()
            self.test_search_functionality()
            self.test_db_view()
            
        finally:
            self.driver.quit()
            
        # 결과 요약
        print("\n" + "=" * 50)
        print("📊 테스트 결과 요약")
        print("=" * 50)
        
        success_count = sum(1 for _, result in self.test_results if result)
        total_count = len(self.test_results)
        
        print(f"\n성공: {success_count}/{total_count}")
        
        for test_name, result in self.test_results:
            status = "✅" if result else "❌"
            print(f"{status} {test_name}")

if __name__ == "__main__":
    print("브라우저 테스트를 위해 Selenium 사용")
    print("Chrome 드라이버가 필요합니다\n")
    
    tester = FrontendFunctionTest()
    tester.run_all_tests()