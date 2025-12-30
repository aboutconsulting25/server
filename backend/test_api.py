import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# 1. 로그인 테스트
print("=" * 50)
print("1. 로그인 테스트")
print("=" * 50)

login_data = {
    "code": "3a64ed7d-af99-4f7a-9a7a-985dac51277f",
    "password": "test1234"
}

response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if response.status_code == 200:
    access_token = response.json()['access']
    refresh_token = response.json()['refresh']
    
    # 2. 사용자 정보 조회 테스트
    print("\n" + "=" * 50)
    print("2. 사용자 정보 조회 테스트 (/me)")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    me_response = requests.get(f"{BASE_URL}/auth/me/", headers=headers)
    print(f"Status Code: {me_response.status_code}")
    print(f"Response: {json.dumps(me_response.json(), indent=2, ensure_ascii=False)}")
    
    # 3. 토큰 갱신 테스트
    print("\n" + "=" * 50)
    print("3. 토큰 갱신 테스트")
    print("=" * 50)
    
    refresh_data = {
        "refresh": refresh_token
    }
    
    refresh_response = requests.post(f"{BASE_URL}/auth/refresh/", json=refresh_data)
    print(f"Status Code: {refresh_response.status_code}")
    print(f"Response: {json.dumps(refresh_response.json(), indent=2, ensure_ascii=False)}")
    
    # 4. 인증 없이 접근 테스트 (실패해야 함)
    print("\n" + "=" * 50)
    print("4. 인증 없이 /me 접근 테스트 (401 에러 예상)")
    print("=" * 50)
    
    no_auth_response = requests.get(f"{BASE_URL}/auth/me/")
    print(f"Status Code: {no_auth_response.status_code}")
    print(f"Response: {json.dumps(no_auth_response.json(), indent=2, ensure_ascii=False)}")
    
    # 5. 잘못된 비밀번호 테스트
    print("\n" + "=" * 50)
    print("5. 잘못된 비밀번호로 로그인 테스트 (401 에러 예상)")
    print("=" * 50)
    
    wrong_login = {
        "code": "3a64ed7d-af99-4f7a-9a7a-985dac51277f",
        "password": "wrongpassword"
    }
    
    wrong_response = requests.post(f"{BASE_URL}/auth/login/", json=wrong_login)
    print(f"Status Code: {wrong_response.status_code}")
    print(f"Response: {json.dumps(wrong_response.json(), indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료!")
    print("=" * 50)

