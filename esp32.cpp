#include <BLEDevice.h>        // BLE 디바이스 초기화 및 관리 관련 라이브러리
#include <BLEServer.h>        // BLE 서버 기능 제공 라이브러리
#include <BLEUtils.h>         // BLE 유틸리티 함수들
#include <BLEAdvertising.h>   // BLE 광고(Advertising) 관련 라이브러리

void setup() {
  Serial.begin(115200);        // 시리얼 모니터 시작 (디버깅용)

  BLEDevice::init("CHILD_TAG");  
  // ESP32 BLE 장치 초기화 및 BLE 디바이스 이름 설정

  BLEServer *pServer = BLEDevice::createServer();
  // BLE 서버 객체 생성 (연결을 관리할 수 있는 서버 역할)

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  // Advertising 객체 가져오기 (BLE 광고 패킷 설정/시작 담당)

  pAdvertising->start();
  // BLE 광고 시작 → 주변 기기에서 "CHILD_TAG"로 검색 가능

  Serial.println("ESP32 BLE Advertising Started!");
  // 광고 시작 확인 메시지 출력
}

void loop() {}
// loop는 비워둠 → BLE 광고는 백그라운드에서 자동으로 동작
