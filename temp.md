
## 🛠️ ESP32 아두이노 IDE 설정 방법
추가 보드 관리자 URL 등록

파일 > 설정 (Preferences)

추가적인 보드 매니저 URLs에 아래 주소 붙여넣기:

https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

ESP32 보드 매니저 설치

툴 > 보드 > 보드 매니저...

"esp32" 검색

esp32 by Espressif Systems 설치

보드 및 포트 선택

툴 > 보드 > ESP32 Arduino > ESP32S3 Dev Module 선택

툴 > 포트 > ESP32S3가 연결된 COM 포트 선택

---
## 🔊 스피커 예제 코드 (Standard tone() API)
C++
```
// --- 오직 오디오 출력 핀 1개만 설정 ---
const int AUDIO_L_PIN = 21; // PAM8403 L INPUT

void setup() {
  Serial.begin(115200);
  Serial.println("Simple Tone Test (Pin 21) - Standard Arduino API");

  // --- 앰프 및 LEDC 설정 코드 (모두 불필요!) ---
  // tone() 함수는 호출될 때 알아서 핀 모드를 설정하고
  // ESP32의 LEDC 채널을 자동으로 할당받아 사용합니다.
  
  Serial.println("Setup Complete. Starting loop...");
}

void loop() {
  Serial.println("Playing Left Channel (1000 Hz)");
  
  // tone(핀번호, 주파수);
  // 21번 핀에서 1000Hz 소리를 *계속* 재생 시작
  tone(AUDIO_L_PIN, 1000);  
  delay(500); // 0.5초 동안 소리가 유지됨

  Serial.println("Stop");
  // noTone(핀번호);
  // 21번 핀의 소리를 *즉시* 멈춤
  noTone(AUDIO_L_PIN);
  delay(500); // 0.5초간 조용히 대기

  Serial.println("Playing Left Channel (1500 Hz)");
  tone(AUDIO_L_PIN, 1500); // 1500Hz 소리 시작
  delay(500); // 0.5초 동안 유지

  Serial.println("Stop");
  noTone(AUDIO_L_PIN); // 소리 멈춤
  delay(500); // 0.5초간 대기
}
```

---
## ⚠️ 중요 유의사항: 전원 문제
PAM8403 (오디오 앰프 모듈)은 5V 전원이 필요합니다. ESP 보드의 5V (VIN) 핀에서 전원을 가져올 경우, 전압은 5V로 맞지만 전류가 부족하여 앰프가 제대로 작동하지 않습니다.

**해결책: 앰프의 5V 전원은 ESP 보드가 아닌, 별도의 USB 단자 (충전기 어댑터 등)에 직접 연결하여 충분한 전류를 공급해야 합니다. (이때, ESP의 GND와 앰프의 GND는 서로 연결해야 합니다.)**

---
## 🎵 오디오 재생 관련 참고 사항
MP3 vs WAV

ESP32에서 MP3 파일을 직접 디코딩하는 것은 매우 복잡합니다.

- 오디오 파일을 사용하려면 WAV 파일 (.wav) 형식으로 미리 변환해서 사용하는 것이 훨씬 간단합니다.

### DAC 부재

1. mp3파일을 하기 위해서는 복잡함 -> mp3파일을 받은경우 WAV파일로 변경해야함

2. DAC가 없기 때문에 맑은 소리가 안나올수 있음 but 알아듣는데는 상관 X  

3. XT_DAC_Audio라이브러리를 통해서 DAC가 없이 가능하다.

**GitHub 링크: https://github.com/WeekendWarrior1/XTronical_XT_DAC_Audio_Mirror**
**파일 다운로드 링크:  https://github.com/WeekendWarrior1/XTronical_XT_DAC_Audio_Mirror/archive/master.zip**

적용법
- 스케치 -> 라이브러리 포함 -> .zip라이브러리


## 🎧 기타 오디오 라이브러리 (컴파일 시 오래 걸림 주의)
- ESP32-audioI2S

- ESP8266Audio


 빨리 끝난다면 라즈베리파일에서 Classic BT로 오디오 파일을 전송할 수 있게 하고, 버튼을 통해서 BLE로 거리를 감지하는 식으로 가면 될듯
