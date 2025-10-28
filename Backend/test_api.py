# test_api.py
import requests

BASE_URL = "http://localhost:8000/users"

def test_kakao_login():
    """카카오 로그인 테스트"""
    url = f"{BASE_URL}/auth/social-login/"
    data = {
        "provider": "kakao",
        "access_token": "VLRYChewsnF7BWT1hDV46UCDMSIkzze4AAAAAQoXC2sAAAGaK7RFEYh6dPOEuoNF"  # 카카오에서 받은 실제 토큰
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

def test_complete_profile(access_token):
    """프로필 완성 테스트"""
    url = f"{BASE_URL}/auth/complete-profile/"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "nickname": "길동이",
        "disability_type": "physical",
        "has_wheelchair": True
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

# 실행
result = test_kakao_login()
if 'tokens' in result:
    test_complete_profile(result['tokens']['access'])