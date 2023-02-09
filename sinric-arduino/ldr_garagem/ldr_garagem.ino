#include <ESP8266SSDP.h>

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


#define LABEL "bancada"

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

#include <ArduinoJson.h>
#include <FS.h>
#include <LittleFS.h>

#include <Espalexa.h>
Espalexa espalexa;


#include <WiFiManager.h>
WiFiManager wifiManager;



#include "SinricPro.h"
#include "SinricProDoorbell.h"
#include "SinricProSwitch.h"

#include "ESPTelnet.h"

DynamicJsonDocument config(1024);
#define kmode "mode"

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
  const int v_min = config["ldr_min"].as<int>();
  const int v_max = config["ldr_max"].as<int>();
  if (tmpAdc > v_max) rt = HIGH;  // quando acende a luz, sobe o medidor com a propria luz que foi acionada, para não desligar.
  if (tmpAdc < v_min) rt = LOW;
  if (rt != ldrState) {
    char buffer[64];
    sprintf(buffer, "adc %d,ldrState %d, adcState %d  (%i,%i) ", tmpAdc, ldrState, rt, v_max, v_min);
    debug(buffer);
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

  if (!LittleFS.begin()) {
    Serial.println("LittleFS mount failed");
  }

  setupTelnet();

  restoreConfig();
  setupPins();
  setupAlexa();
}

void setupTelnet() {
  telnet.onConnect(onTelnetConnect);
  telnet.onInputReceived([](String str) {
    print(doCommand(str));
  });

  Serial.print("- Telnet: ");
  if (telnet.begin()) {
    Serial.println("running");
  } else {
    Serial.println("error.");
    errorMsg("Will reboot...");
  }
}
void errorMsg(String msg) {
  Serial.println(msg);
  telnet.println(msg);
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
  loopEvent();
  espalexa.loop();
}

String print(String msg) {
  Serial.println(msg);
  telnet.println(msg);
  return msg;
}
void printCmds(String *cmd) {
  Serial.println("command:");
  for (int i = 0; i < sizeof(cmd); i++) {
    if (cmd[i] != NULL) {
      Serial.print(cmd[i]);
      Serial.print(" ");
    }
  }
  Serial.println("");
}
String *split(String s, const char delimiter) {
  int count = 0;
  int j = 0;
  for (int i = 0; i < s.length(); i++) {
    if (s[i] == delimiter) {
      count++;
    }
  }

  String *words = new String[count + 1];
  int wordCount = 0;
  j = 0;

  for (int i = 0; i < s.length(); i++) {
    if (s[i] == delimiter) {
      wordCount++;
      continue;
    }
    words[wordCount] += s[i];
  }

  return words;
}


String saveConfig() {
  String rsp = "saved";
  String json;
  serializeJson(config,json);
  writeFile("/config.json",json);
  return rsp;
}
String restoreConfig() {
  //defaultConfig();
  String rt = "nao restaurou config";
  Serial.println("restoreConfig");
  String json = readFile("/config.json");
  if (json){
    deserializeJson(config,json);
    rt = "restored";
  }
  Serial.println(json);
  linha();
  return rt;
}
void linha() {
  Serial.println("-------------------------------");
}
void defaultConfig() {
  config["label"] = LABEL;
  config.createNestedObject("mode");
  config.createNestedObject("trigger");
  config.createNestedObject("stable");
  config["ldr_min"] = "5";
  config["ldr_max"] = "600";
  config["debug"] = inDebug ? "on" : "off";
  config["interval"] = "500";

  doCommand("gpio 0 mode adc");
  doCommand("set ldr_min 1");
}

void printConfig() {

  serializeJson(config, Serial);
}

void setupPins() {
  JsonObject mode = config["mode"];
  for (JsonPair k : mode) {
    initPinMode(String(k.key().c_str()).toInt(), k.value().as<String>());
  }
}

void initPinMode(int pin, const String m) {
  if (m == "in")
    pinMode(pin, INPUT);
  else if (m == "out")
    pinMode(pin, OUTPUT);
}

String doCommand(String command) {
  String *cmd = split(command, ' ');
  printCmds(cmd);
  Serial.println(cmd[0]);
  if (cmd[0] == "open")
    return readFile(cmd[1]);
  else if (cmd[0] == "help")
    return help();
  else if (cmd[0] == "show") {
    return config.as<String>();
  } else if (cmd[0] == "reset") {
    if (cmd[1] == "factory") {
      defaultConfig();
      return "OK";
    }
    print("reiniciando...");
    delay(1000);
    telnet.stop();
    ESP.restart();
    return "OK";
  } else if (cmd[0] == "save") {
    return saveConfig();
  } else if (cmd[0] == "restore") {
    return restoreConfig();
  } else if (cmd[0] == "set") {
    if (cmd[2] == "none") {
      config.remove(cmd[1]);
    } else {
      config[cmd[1]] = cmd[2];
      printConfig();
    }
    return "OK";
  } else if (cmd[0] == "get") {
    return config[cmd[1]];
  } else if (cmd[0] == "gpio") {
    int pin = cmd[1].toInt();
    if (cmd[2] == "get") {
      int v = digitalRead(pin);
      return String(v);
    } else if (cmd[2] == "set") {
      int v = cmd[3].toInt();
      Serial.printf("set pin %d to %d \r\n", pin, v);
      digitalWrite(pin, (v == 0) ? LOW : HIGH);
      return "OK";
    } else if (cmd[2] == "mode") {
      JsonObject mode = config["mode"];
      mode[cmd[1]] = cmd[3];
      initPinMode(cmd[1].toInt(), cmd[3]);
      printConfig();
      return "OK";
    } else if (cmd[2] == "trigger") {
      // gpio 4 trigger 15 bistable
      JsonObject trigger = getTrigger();
      trigger[String(pin)] = cmd[3];
      getStable()[String(pin)] = cmd[4] == "bistable" ? 1 : 0;
      return "OK";
    }
  }
  return "invalido";
}


JsonObject getMode() {
  return config["mode"].as<JsonObject>();
}
JsonObject getTrigger() {
  return config["trigger"].as<JsonObject>();
}
JsonObject getStable() {
  return config["stable"].as<JsonObject>();
}

unsigned long loopEventMillis = millis();
void loopEvent() {
  int interval = String(config["interval"]).toInt();
  if (millis() - loopEventMillis > interval) {
    JsonObject mode = config["mode"];
    for (JsonPair k : mode) {
      readPin(String(k.key().c_str()).toInt(), k.value().as<String>());
    }
    loopEventMillis = millis();
  }
}
StaticJsonDocument<256> docPinValues;
void readPin(int pin, String mode) {
  int oldValue = docPinValues[String(pin)];
  int newValue = 0;
  if (mode == "adc")
    newValue = analogRead(pin);
  else
    newValue = digitalRead(pin);
  if (oldValue != newValue) {
    char buffer[32];
    sprintf(buffer, "pin %d : %d ", pin, newValue);
    debug(buffer);
    docPinValues[String(pin)] = newValue;
    checkTrigger(pin, newValue);
  }
}

void debug(String txt) {
  if (config["debug"] == "on") {
    print(txt);
  } else {
    Serial.println(txt);
  }
}
void checkTrigger(int pin, int value) {
  String p = String(pin);
  JsonObject trig = getTrigger();
  if (trig.containsKey(p)) {
    String pinTo = trig[p];
    if (pinTo.toInt() != pin)
      writePin(pinTo.toInt(), value);
  }
}

void writePin(int pin, int value) {
  String mode = getMode()[String(pin)];
  if (mode != NULL)
    if (mode == "adc") return;
    else
      digitalWrite(pin, value);
  else
    digitalWrite(pin, value);
}

String help() {
  String s = "set ldr_max x \r\n";
  s += "set ldr_min x \r\n";
  return s;
}

void writeFile(String f, String payload){
  File file = LittleFS.open(f,"w");
  file.println(payload);
  file.close();
}

String readFile(String f) {
  File file = LittleFS.open(f, "r");
  if (!file) {
    return "Falhou a abertura do arquivo para leitura";
  }
  String s = file.readString();
  file.close();
  linha();
  Serial.println(s);
  linha();
  return s;
}

void setupAlexa(){
  espalexa.begin();
  espalexa.addDevice(config["label"], firstDeviceChanged);
}

void firstDeviceChanged(uint8_t brightness) {
    if (brightness) {
      digitalWrite(RELAY_PIN,HIGH);
      Serial.print("ON, brightness ");
      Serial.println(brightness);
      print("RELAY ON");

    }
    else  {
      digitalWrite(RELAY_PIN,LOW);
      print("RELAY OFF");
    }
}

