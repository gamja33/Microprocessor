import asyncio
from bleak import BleakScanner
import subprocess
import RPi.GPIO as GPIO
import time

# -----------------------------
# 기본 설정 값
# -----------------------------
TARGET_NAME = "CHILD_TAG"      # BLE 태그의 디바이스 이름
BUZZER_PIN = 18                # 부저가 연결된 GPIO 핀 번호
ALERT_DURATION = 3.0           # 부저 경보 지속 시간(초)
DANGER_THRESHOLD = 5           # RSSI 약화가 연속 N번 감지되면 위험으로 판단

# -----------------------------
# GPIO 초기 설정
# -----------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)         # GPIO 핀 번호 모드를 BCM(핀 번호 기준)으로 설정
GPIO.setup(BUZZER_PIN, GPIO.OUT)  # 부저 핀을 출력 모드로 설정

# PWM 설정: 2000Hz 로 동작하는 PWM 객체 생성
pwm = GPIO.PWM(BUZZER_PIN, 2000)
pwm.start(0)  # 처음에는 Duty Cycle 0 → 소리 없음


# -----------------------------
# 상태 변수들
# -----------------------------
danger_count = 0               # RSSI 약화 연속 감지 횟수
last_seen_time = time.time()   # 마지막 태그 감지 시간
has_detected_tag_once = False  # 태그가 한 번이라도 감지되었는지 여부
is_alert_in_progress = False   # 현재 부저 경보가 진행 중인지
alert_end_time = 0.0           # 경보 종료 시간(부저 자동 끄기)

# -----------------------------
# 부저 제어 함수
# -----------------------------
def beep_on():
    """부저를 켬 (Duty Cycle 50%로 설정)"""
    pwm.ChangeDutyCycle(50)

def beep_off():
    """부저를 끔"""
    pwm.ChangeDutyCycle(0)

# -----------------------------
# BLE 감지 콜백 함수
# (태그를 발견할 때마다 자동 호출)
# -----------------------------
def detection_callback(device, advertisement_data):
    global danger_count, last_seen_time, has_detected_tag_once, is_alert_in_progress
    
    # 우리가 찾는 디바이스인지 확인
    if device.name == TARGET_NAME:
        has_detected_tag_once = True  # 태그를 처음이라도 발견하면 True로 변경
        last_seen_time = time.time()  # 마지막 발견 시간 갱신
        
        rssi = advertisement_data.rssi  # 신호 세기
        print(f"RSSI: {rssi} dBm")

        # RSSI가 -75보다 강하면 → 정상 범위로 판단
        if rssi > -75:
            danger_count = 0              # 위험 카운트 초기화
            is_alert_in_progress = False  # 경보 상태 초기화
            beep_off()                     # 부저 끄기
        
        # RSSI 약화 시
        else:
            print("거리 위험!")
            danger_count += 1  # 위험 카운트 증가
            
            # 임계치를 넘고 현재 경보 중이 아니라면 경보 트리거
            if danger_count >= DANGER_THRESHOLD and not is_alert_in_progress:
                trigger_alert("거리 이탈 감지(RSSI 약화)")

# -----------------------------
# 경보 실행 함수
# -----------------------------
def trigger_alert(reason):
    global is_alert_in_progress, alert_end_time
    VENV_PYTHON = "/home/pi/myenv/bin/python3" # 가상환경 파이썬 경로
    # 이미 경보 중이면 다시 실행하지 않음
    if not is_alert_in_progress:
        print(f" {reason} → 부저 {ALERT_DURATION}초 & 푸시")

        is_alert_in_progress = True
        alert_end_time = time.time() + ALERT_DURATION  # 경보 종료 시간 설정

        beep_on()  # 부저 울림
        subprocess.Popen([VENV_PYTHON, "fcm.py"])  # FCM 푸시 알림 실행

# -----------------------------
# 메인 비동기 루프
# -----------------------------
async def main():
    global last_seen_time
    
    print("시스템 시작. 태그를 감지할 때까지 경보는 울리지 않습니다.")
    
    # BLE 스캐너 생성 (콜백 포함)
    scanner = BleakScanner(detection_callback)
    await scanner.start()  # 스캔 시작
    
    # 메인 루프
    while True:
        current_time = time.time()
        time_diff = current_time - last_seen_time

        # 태그가 한 번이라도 발견된 이후,
        # 10초 동안 신호가 전혀 안들어오면 → 신호 소실 경보
        if has_detected_tag_once and time_diff > 10.0:
            print(f"신호 끊김! ({int(time_diff)}초 경과)")

            if not is_alert_in_progress:
                trigger_alert("신호 소실(10초 타임아웃)")

        # 경보 중이고 종료 시간이 지나면 → 자동으로 부저 OFF
        if is_alert_in_progress and current_time > alert_end_time:
            print(f"경보 {ALERT_DURATION}초 완료. 자동 정지.")
            beep_off()

        await asyncio.sleep(1.0)  # 1초마다 루프 돌기

# -----------------------------
# 프로그램 실행 / 종료 처리
# -----------------------------
try:
    asyncio.run(main())
except KeyboardInterrupt:
    # Ctrl+C 종료
    print("프로그램 종료")
    pwm.stop()
    GPIO.cleanup()
