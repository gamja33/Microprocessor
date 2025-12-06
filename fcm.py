import requests              # HTTP 요청을 보내기 위한 라이브러리
import json                  # JSON 변환 용도
from google.oauth2 import service_account  # 서비스 계정 기반 인증
import google.auth.transport.requests       # Google OAuth 요청 처리용


PROJECT_ID = "imuuu-f2c2d"
# FCM v1 API 엔드포인트 (Firebase Cloud Messaging)
FCM_URL = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

# FCM을 사용하기 위한 Google API 권한 범위
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]


# 서비스 계정 키 파일 경로 (라즈베리파이에 저장된 JSON)
KEY_FILE_PATH = "/home/pi/service-account.json"

# 1) 서비스 계정 파일 로드 (인증 정보 불러오기)
try:
    creds = service_account.Credentials.from_service_account_file(
        KEY_FILE_PATH,
        scopes=SCOPES
    )
except FileNotFoundError:
    print(f"Error: {KEY_FILE_PATH} 파일을 찾을 수 없습니다.")
    exit()

# 2) Access Token 갱신 (Google OAuth 인증 절차)
#    → 서버에서 FCM 사용하려면 Access Token이 필요함
request = google.auth.transport.requests.Request()
creds.refresh(request)
access_token = creds.token  # FCM 요청 헤더에 포함할 토큰

# 3) HTTP 요청 헤더 설정
headers = {
    "Authorization": f"Bearer {access_token}",  # OAuth 인증 토큰
    "Content-Type": "application/json"          # JSON 데이터 전송
}


# 푸시 알림 받을 대상의 FCM 디바이스 토큰
target_token = ""  # 앱에서 받아서 넣어야 하는 값


# 4) 실제 FCM 메시지 Payload
message = {
    "message": {
        "token": target_token,   # 대상 디바이스 토큰

        "notification": {
            "title": "긴급 경보 (Emergency)",  # 알림 제목
            "body": "아동이 안전 구역을 이탈했습니다! 위치를 확인하세요."  # 알림 내용
        },

        # 5) 안드로이드 고우선 알림 설정 (Doze 모드에서도 즉시 전송됨)
        "android": {
            "priority": "high"
        }
    }
}

# 6) FCM 전송 요청 실행 및 결과 출력
try:
    print("Sending FCM request...")
    
    # FCM API로 POST 요청 전송
    response = requests.post(FCM_URL, headers=headers, data=json.dumps(message))
    
    # HTTP 상태 코드 (200이면 성공)
    print("Status:", response.status_code)

    # FCM 서버 응답 출력
    print("Response:", response.text)
    
except Exception as e:
    print(f"전송 실패: {e}")
