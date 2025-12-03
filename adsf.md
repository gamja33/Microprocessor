# 라즈베리 파이 자동 실행 시스템 구축 가이드

이 문서는 라즈베리 파이 5(또는 4) 부팅 시 **핫스팟(Wi-Fi)**과 **블루투스**를 자동으로 활성화하고, **Python 제어 코드(ESP32 통신 + 웹앱)**를 실행하는 전체 과정을 정리한 것입니다.

---

## 1. 핫스팟(Wi-Fi AP) 설정 (최초 1회)

파이썬 코드가 아닌 **OS의 네트워크 관리자(NetworkManager)**에게 설정을 맡깁니다. 한 번만 설정하면 부팅 시 자동으로 핫스팟을 켭니다.

**터미널 명령어:**

**Bash**

```
# 핫스팟 이름(SSID): MyPiProject
# 비밀번호: 12345678
# 인터페이스: wlan0 (일반적인 무선랜 이름)

sudo nmcli device wifi hotspot ssid "MyPiProject" password "12345678" ifname wlan0
```

---

## 2. Python 코드 작성 (`main.py`)

파이썬 코드 내에서 **블루투스 강제 활성화(안전장치)**와 **멀티스레딩(웹+블루투스 동시 실행)**을 구현합니다.

**파일 경로 예시:** `/home/pi/my_project/main.py`

**Python**

```
import os
import time
import threading
from flask import Flask

# --- [1] 안전장치: 부팅 직후 블루투스 강제 활성화 ---
def init_bluetooth_system():
    print("[System] 블루투스 장치 점검 중...")
    os.system("sudo rfkill unblock bluetooth")  # 차단 해제
    os.system("sudo systemctl start bluetooth") # 서비스 시작
    time.sleep(2)
    os.system("sudo hciconfig hci0 up")         # 장치 UP
    print("[System] 블루투스 활성화 완료")

# --- [2] 기능 정의 ---
app = Flask(__name__)

@app.route('/')
def index():
    return "IoT Controller Online"

def run_web_server():
    # 핫스팟 IP 대역에서 접속 가능하도록 host='0.0.0.0' 필수
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def run_esp32_communication():
    print("[Thread] ESP32 블루투스 연결 대기 중...")
    # 여기에 ESP32 연결 및 데이터 송수신 코드 작성
    # while True:
    #     ...

# --- [3] 메인 실행 ---
if __name__ == '__main__':
    # 1. 블루투스 하드웨어 켜기
    init_bluetooth_system()

    # 2. 웹 서버를 별도 스레드로 실행 (백그라운드)
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # 3. 메인 스레드에서 ESP32 통신 로직 실행
    try:
        run_esp32_communication()
    except KeyboardInterrupt:
        print("시스템 종료")
```

---

## 3. 자동 실행 등록 (Systemd 서비스)

부팅이 완료되고 **네트워크와 블루투스가 준비된 시점**에 위 코드를 실행하도록 관리자(Systemd)에게 등록합니다.

### 3-1. 서비스 파일 생성

터미널에서 편집기를 엽니다.

**Bash**

```
sudo nano /etc/systemd/system/my_iot.service
```

### 3-2. 내용 작성 (복사/붙여넣기)

> **주의:** `ExecStart`와 `WorkingDirectory`의 경로는 본인의 실제 경로로 수정하세요.

**Ini, TOML**

```
[Unit]
Description=Raspberry Pi IoT Controller Service
# 핵심: 네트워크(핫스팟)와 블루투스가 준비된 후 실행
After=network-online.target bluetooth.target
Wants=network-online.target bluetooth.target

[Service]
# 실행할 명령어 (파이썬 절대 경로 필수)
ExecStart=/usr/bin/python3 /home/pi/my_project/main.py
WorkingDirectory=/home/pi/my_project

# 로그 출력을 위해 버퍼링 비활성화
Environment=PYTHONUNBUFFERED=1

# 프로그램 종료 시 5초 후 자동 재시작 (무한 루프 유지)
Restart=always
RestartSec=5

# 실행 권한 유저
User=pi

[Install]
WantedBy=multi-user.target
```

### 3-3. 서비스 등록 및 활성화

작성한 파일을 저장(`Ctrl+O` -> `Enter` -> `Ctrl+X`)하고 아래 명령어를 순서대로 입력합니다.

**Bash**

```
# 1. 시스템 설정 새로고침
sudo systemctl daemon-reload

# 2. 부팅 시 자동 실행 등록 (Enable)
sudo systemctl enable my_iot.service

# 3. 지금 즉시 실행하여 테스트 (Start)
sudo systemctl start my_iot.service
```

---

## 4. 상태 확인 및 디버깅

제대로 작동하는지 확인하려면 다음 명령어를 사용하세요.

**Bash**

```
# 서비스 상태 및 로그 확인 (Active: active (running) 떠야 함)
sudo systemctl status my_iot.service

# 실시간 로그 모니터링 (print 문 확인)
sudo journalctl -u my_iot.service -f
```

```
🚦 부팅 프로세스 최종 요약
⚡ 전원 ON

라즈베리파이가 켜집니다.

⚙️ OS(운영체제) 작업 시작

OS: "주인님이 설정해둔 핫스팟(MyPiProject) 켜자!" (와이파이 송출 시작)

OS: "블루투스 장치도 켜자!" (하드웨어 전원 공급)

🛑 검문소 (Systemd)

우리가 만든 서비스 파일(After=network-online.target)이 지키고 서 있습니다.

"잠깐! 아직 인터넷(핫스팟) 안 켜졌지? 파이썬 코드는 대기해!"

✅ 통과 및 실행

핫스팟이 정상적으로 켜진 신호가 들어옵니다.

Systemd: "오케이, 핫스팟 켜졌다. 이제 파이썬 코드(main.py) 실행해!"

🐍 파이썬 코드 작동

블루투스 확인: "혹시 모르니까 블루투스 다시 한번 확실히 켜!" (안전장치 가동)

ESP32 연결 & 웹서버 시작: 본격적인 작동 시작.

```
