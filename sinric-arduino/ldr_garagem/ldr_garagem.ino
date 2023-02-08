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
#endif
#ifdef ESP32
#endif

#include <WiFiManager.h>
WiFiManager wifiManager;



#include "SinricPro.h"
#include "SinricProDoorbell.h"
#include "SinricProSwitch.h"

#include "ESPTelnet.h"


// Include libraries
#if defined ESP8266 || defined ESP32
#endif

#if defined ESP8266
#endif




#define APP_KEY "5176f8b7-0e16-429f-8f22-73d4093f7c40"
#define APP_SECRET "66c53efa-f3ce-419d-abe5-ac3fdecf71d9-4a0a01d2-5bd0-4ae1-806e-7c7a02438d73"
#define DOORBELL_ID "63dee83722e49e3cb5f91932"
#define SWITCH_ID "63ded33a22e49e3cb5f90d3d"

#define BAUD_RATE 115200  // Change baudrate to your need

#define BUTTON_PIN 4
#define RELAY_PIN 15
#define inDebug false
unsigned long lastBtnPress;

int ldrState = 0;
bool myPowerState = false;
int tmpAdc = 0;
int adcState = 0;


ESPTelnet telnet;


bool onPowerState(const String &deviceId, bool &state) {
  Serial.printf("Device %s turned %s (via SinricPro) \r\n", deviceId.c_str(), state ? "on" : "off");
  myPowerState = state;
  digitalWrite(RELAY_PIN, myPowerState ? HIGH : LOW);
  return true;  // request handled properly
}

void handleRelayState() {
  if (int(myPowerState) != digitalRead(RELAY_PIN)) {
    myPowerState = digitalRead(RELAY_PIN) == HIGH;
    SinricProSwitch &mySwitch = SinricPro[SWITCH_ID];
    mySwitch.sendPowerStateEvent(myPowerState);  // send the new powerState to SinricPro server
  }
}


int getAdc() {
  tmpAdc = analogRead(0);
  int rt = ldrState;
  if (tmpAdc > 600) rt = HIGH;  // quando acende a luz, sobe o medidor com a propria luz que foi acionada, para não desligar.
  if (tmpAdc < 50) rt = LOW;
  if (rt != ldrState || inDebug) {
    Serial.print("adc: ");
    Serial.print(tmpAdc);
    Serial.print(" ldrState: ");
    Serial.print(ldrState);
    Serial.print(" adcState: ");
    Serial.println(rt);
  }
  return rt;
}
// checkButtonpress
// reads if BUTTON_PIN gets LOW and send Event
void checkButtonPress() {
  unsigned long actualMillis = millis();

  adcState = getAdc();
  if (actualMillis - lastBtnPress > 60000 * 5 && (ldrState != adcState)) {
    Serial.println(tmpAdc);
    if (adcState == HIGH) {
      Serial.printf("Noite");
      // get Doorbell device back
      SinricProDoorbell &myDoorbell = SinricPro[DOORBELL_ID];
      // send doorbell event
      myDoorbell.sendDoorbellEvent();
      Serial.print(" escura");
      Serial.printf("... \r\n");
      ldrState = adcState;
      lastBtnPress = actualMillis;
    }
    // desliga o rele
    if (ldrState != digitalRead(RELAY_PIN)) {
      Serial.println(adcState ? "HIGH" : "LOW");
      digitalWrite(RELAY_PIN, adcState);
      ldrState = adcState;
      handleRelayState();  // if myPowerState indicates device turned on: turn on led (builtin led uses inverted logic: LOW = LED ON / HIGH = LED OFF)
    }

  } else delay(200);
}

// setup function for WiFi connection
void setupWiFi() {
  Serial.printf("\r\n[Wifi]: Connecting");
  wifiManager.autoConnect("AutoConnectAP");
  Serial.println(WiFi.localIP());
}

// setup function for SinricPro
void setupSinricPro() {

  // add doorbell device to SinricPro
  SinricProDoorbell &myDoorbell = SinricPro[DOORBELL_ID];
  SinricProSwitch &mySwitch = SinricPro[SWITCH_ID];
  mySwitch.onPowerState(onPowerState);

  // setup SinricPro
  SinricPro.onConnected([]() {
    Serial.printf("Connected to SinricPro\r\n");
  });
  SinricPro.onDisconnected([]() {
    Serial.printf("Disconnected from SinricPro\r\n");
  });
  //SinricPro.restoreDeviceStates(true);
  SinricPro.begin(APP_KEY, APP_SECRET);
  ldrState = getAdc() ? LOW : HIGH;
  lastBtnPress = millis() - 360000;
}

// main setup function
void setup() {
  pinMode(BUTTON_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);  // define LED GPIO as output


  Serial.begin(BAUD_RATE);
  Serial.printf("\r\n\r\n");
  setupWiFi();
  setupSinricPro();
  setupTelnet();
}

void setupTelnet() {
  telnet.onConnect(onTelnetConnect);
  telnet.onInputReceived([](String str) {
    telnet.println(onCommand(str));
  });
  
  Serial.print("- Telnet: ");
  if (telnet.begin()) {
    Serial.println("running");
  } else {
    Serial.println("error.");
    errorMsg("Will reboot...");
  }

}
void errorMsg(String msg){
  Serial.println(msg);
}

void onTelnetConnect(String ip) {
  Serial.print("- Telnet: ");
  Serial.print(ip);
  Serial.println(" connected");
  telnet.println("\nWelcome " + telnet.getIP());
  telnet.println("(Use ^] + q  to disconnect.)");
}
void onTelnetDisconnect(String ip) {
  Serial.print("- Telnet: ");
  Serial.print(ip);
  Serial.println(" disconnected");
}

void loop() {
  checkButtonPress();
  SinricPro.handle();
  telnet.loop();
}

String onCommand(String cmd){
   if (cmd=="show"){
     return "{show}";
   }
   elif (cmd=="reset"){
    telnet.println("reiniciando...")
    delay(1000);
    ESP.restart();
    return "OK";
   }
   return "inválido";
}