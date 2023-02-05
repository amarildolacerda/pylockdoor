/*
 * Example for how to use SinricPro Doorbell device:
 * - setup a doorbell device
 * - send event to sinricPro server if button is pressed
 *
 * If you encounter any issues:
 * - check the readme.md at https://github.com/sinricpro/esp8266-esp32-sdk/blob/master/README.md
 * - ensure all dependent libraries are installed
 *   - see https://github.com/sinricpro/esp8266-esp32-sdk/blob/master/README.md#arduinoide
 *   - see https://github.com/sinricpro/esp8266-esp32-sdk/blob/master/README.md#dependencies
 * - open serial monitor and check whats happening
 * - check full user documentation at https://sinricpro.github.io/esp8266-esp32-sdk
 * - visit https://github.com/sinricpro/esp8266-esp32-sdk/issues and check for existing issues or open a new one
 */

#ifdef ENABLE_DEBUG
#define DEBUG_ESP_PORT Serial
#define NODEBUG_WEBSOCKETS
#define NDEBUG
#endif

#include <Arduino.h>
#ifdef ESP8266
//#include <ESP8266WiFi.h>
#endif
#ifdef ESP32
//#include <WiFi.h>
#endif

#include <WiFiManager.h>
WiFiManager wifiManager;



#include "SinricPro.h"
#include "SinricProDoorbell.h"
#include "SinricProSwitch.h"


#define WIFI_SSID "VIVOFIBRA-A360"
#define WIFI_PASS "6C9FCEC12A"
#define APP_KEY "5176f8b7-0e16-429f-8f22-73d4093f7c40"
#define APP_SECRET "66c53efa-f3ce-419d-abe5-ac3fdecf71d9-4a0a01d2-5bd0-4ae1-806e-7c7a02438d73"
#define DOORBELL_ID "63dee83722e49e3cb5f91932"
#define SWITCH_ID "63ded33a22e49e3cb5f90d3d"

#define BAUD_RATE 115200  // Change baudrate to your need

#define BUTTON_PIN 4
#define RELAY_PIN 15
int ldrState = 0;
bool myPowerState = false;



bool onPowerState(const String &deviceId, bool &state) {
  Serial.printf("Device %s turned %s (via SinricPro) \r\n", deviceId.c_str(), state?"on":"off");
  myPowerState = state;
  digitalWrite(RELAY_PIN, myPowerState?HIGH:LOW);
  return true; // request handled properly
}

void handleRelayState(){
  if ( int(myPowerState) != digitalRead(RELAY_PIN)){
    myPowerState = digitalRead(RELAY_PIN)==HIGH;
    SinricProSwitch& mySwitch = SinricPro[SWITCH_ID];
    mySwitch.sendPowerStateEvent(myPowerState); // send the new powerState to SinricPro server
  }
}


// checkButtonpress
// reads if BUTTON_PIN gets LOW and send Event
void checkButtonPress() {
  static unsigned long lastBtnPress;
  unsigned long actualMillis = millis();

  if (actualMillis - lastBtnPress > 5000 && ldrState != digitalRead(BUTTON_PIN)) {
    Serial.printf("Rele: ");
    Serial.printf(digitalRead(RELAY_PIN)==HIGH?"HIGH":"LOW" );
    Serial.printf("\r\n");
    ldrState = digitalRead(BUTTON_PIN);
    if (ldrState==HIGH  ) {
      Serial.printf("Ding");
      // get Doorbell device back
      SinricProDoorbell &myDoorbell = SinricPro[DOORBELL_ID];
      // send doorbell event
      myDoorbell.sendDoorbellEvent();
      if ( digitalRead(RELAY_PIN) == LOW ) {
        Serial.printf(" dong");

        digitalWrite(RELAY_PIN, HIGH);
        handleRelayState();
      }  
      Serial.printf("... \r\n");
    }

    // desliga o rele
    if (ldrState == LOW &&  digitalRead(RELAY_PIN) == HIGH )  {
        Serial.printf("Desligando...\r\n");

        digitalWrite(RELAY_PIN, LOW); 
        handleRelayState(); // if myPowerState indicates device turned on: turn on led (builtin led uses inverted logic: LOW = LED ON / HIGH = LED OFF)
      }
    lastBtnPress = actualMillis;
  }
}

// setup function for WiFi connection
void setupWiFi() {
  Serial.printf("\r\n[Wifi]: Connecting");
  /*WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.printf(".");
    delay(250);
  }
  IPAddress localIP = WiFi.localIP();
  Serial.printf("connected!\r\n[WiFi]: IP-Address is %d.%d.%d.%d\r\n", localIP[0], localIP[1], localIP[2], localIP[3]);
  */
   wifiManager.autoConnect("AutoConnectAP");
  // Imprime o endereço IP obtido após a conexão bem-sucedida
  Serial.println(WiFi.localIP());
}

// setup function for SinricPro
void setupSinricPro() {
  // add doorbell device to SinricPro
  SinricProDoorbell &myDoorbell = SinricPro[DOORBELL_ID];
  SinricProSwitch& mySwitch = SinricPro[SWITCH_ID];
  mySwitch.onPowerState(onPowerState);
  
  // setup SinricPro
  SinricPro.onConnected([]() {
    Serial.printf("Connected to SinricPro\r\n");
  });
  SinricPro.onDisconnected([]() {
    Serial.printf("Disconnected from SinricPro\r\n");
  });
  SinricPro.restoreDeviceStates(true);   
  SinricPro.begin(APP_KEY, APP_SECRET);
}

// main setup function
void setup() {
  pinMode(BUTTON_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);  // define LED GPIO as output


  Serial.begin(BAUD_RATE);
  Serial.printf("\r\n\r\n");
  setupWiFi();
  setupSinricPro();
  ldrState = digitalRead(BUTTON_PIN);
}

void loop() {
  checkButtonPress();
  SinricPro.handle();
}
