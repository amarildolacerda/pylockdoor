
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
#define VERSION "1.0.0"

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

// #include <Espalexa.h>
// Espalexa espalexa;

#include <WiFiManager.h>
WiFiManager wifiManager;

#include "SinricPro.h"
#include "SinricProDoorbell.h"
#include "SinricProSwitch.h"

#include "ESPTelnet.h"

#define SIZE_BUFFER 1024
DynamicJsonDocument config(SIZE_BUFFER);
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
String localIP;
bool isConnected = false;

ESPTelnet telnet;

// declaracoes
void setupTelnet();
void debug(String txt);
void errorMsg(String msg);
void firstDeviceChanged(uint8_t brightness);
void writePin(int pin, int value);
void readPin(int pin, String mode);
void initPinMode(int pin, const String m);
void setupTelnet();
String doCommand(String command);

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
  if (tmpAdc > v_max)
    rt = HIGH;  // quando acende a luz, sobe o medidor com a propria luz que foi acionada, para não desligar.
  if (tmpAdc < v_min)
    rt = LOW;
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
  if (!isConnected) {
    if (adcState != digitalRead(RELAY_PIN))
      digitalWrite(RELAY_PIN, adcState);
  } else if (actualMillis - lastBtnPress > 60000 * 5 && (ldrState != adcState)) {
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
    if (adcState != digitalRead(RELAY_PIN)) {
      Serial.println(adcState ? "HIGH" : "LOW");
      digitalWrite(RELAY_PIN, adcState);
      handleRelayState();  // if myPowerState indicates device turned on: turn on led (builtin led uses inverted logic: LOW = LED ON / HIGH = LED OFF)
    }
  } 
}

// setup function for WiFi connection
void setupWiFi() {
  Serial.printf("\r\n[Wifi]: Connecting");
  wifiManager.autoConnect("AutoConnectAP");
  Serial.println(WiFi.localIP());
  localIP = WiFi.localIP().toString().c_str();
  Serial.printf("V: %s \r\n",VERSION);
}

// setup function for SinricPro
void setupSinricPro() {

  // add doorbell device to SinricPro
  // SinricProDoorbell &myDoorbell = SinricPro[DOORBELL_ID];
  SinricProSwitch &mySwitch = SinricPro[SWITCH_ID];
  mySwitch.onPowerState(onPowerState);

  // setup SinricPro
  SinricPro.onConnected([]() {
    isConnected = true;
    Serial.printf("Connected to SinricPro\r\n");
  });
  SinricPro.onDisconnected([]() {
    isConnected = false;
    Serial.printf("Disconnected from SinricPro\r\n");
  });
  // SinricPro.restoreDeviceStates(true);
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

  defaultConfig();
  restoreConfig();
  setupPins();
  // setupAlexa();
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
  // espalexa.loop();
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
  //words[count+1] = 0;

  return words;
}

String saveConfig() {
  String rsp = "OK";
  serializeJson(config, Serial);
  File file = LittleFS.open("/config.json", "w");
  if (serializeJson(config, file) == 0) rsp = "não gravou /config.json";
  file.close();
  return rsp;
}



String restoreConfig() {
  String rt = "nao restaurou config";
  Serial.println("");
  linha();
  try {
    String old = config.as<String>();
    File file = LittleFS.open("/config.json", "r");
    if (!file) return "erro ao abrir /config.json";
    String novo = file.readString();
    config.clear();
    auto error = deserializeJson(config, novo);
    if (error) {
      Serial.printf("lido: %s \r\n corrente: %s \r\n", novo, old);
      config.clear();
      deserializeJson(config, old);
      return "Error: " + String(novo);
    }
    serializeJson(config, Serial);
    Serial.println("");
    rt = "OK";
    linha();
  } catch (const char *e) {
    return String(e);
  }
  Serial.println("");
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
  config["ldr_max"] = "800";
  config["debug"] = inDebug ? "on" : "off";
  config["interval"] = "100";

  doCommand("gpio 0 mode adc");
  doCommand("gpio 0 trigger 15 monostable");
  //doCommand("set ldr_min 1");
}

void printConfig() {

  serializeJson(config, Serial);
}

void setupPins() {
  JsonObject mode = config["mode"];
  for (JsonPair k : mode) {
    int pin = String(k.key().c_str()).toInt();
    initPinMode(pin, k.value().as<String>());
    int trPin = getTrigger()[String(pin)];
    if (trPin)
    {
      initPinMode(trPin,"out");
    }
  }
}

void initPinMode(int pin, const String m) {
  if (m == "in")
    pinMode(pin, INPUT);
  else if (m == "out")
    pinMode(pin, OUTPUT);
}

String doCommand(String command) {
  try {
    String *cmd = split(command, ' ');
    Serial.println(command);
    Serial.println(cmd[0]);
    if (cmd[0] == "format") {
      LittleFS.format();
      return "formated";
    } else if (cmd[0] == "open") {
      char json[1024];
      readFile(cmd[1], json, 1024);
      return String(json);
    } else if (cmd[0] == "help")
      return help();
    else if (cmd[0] == "show") {
      if (cmd[1] == "config")
        return config.as<String>();
      char buffer[32];
      FSInfo fs_info;
      LittleFS.info(fs_info);

      sprintf(buffer, "{ \"ip\": %s, \"total\": %d, \"free\": %d }", localIP, fs_info.totalBytes, fs_info.totalBytes - fs_info.usedBytes);
      return buffer;
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

        //0-monostable 1-monostableNC 2-bistable 3-bistableNC
        getStable()[String(pin)] = (cmd[4] == "bistable" ? 2 : 0) + (cmd[4].endsWith("NC") ? 1 : 0);

        return "OK";
      }
    }
    return "invalido";
  } catch (const char *e) {
    return String(e);
  }
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
  try {
    int interval;
    try {
      interval = String(config["interval"]).toInt();
    } catch (char e) {
      interval = 500;
    }
    if (millis() - loopEventMillis > interval) {
      JsonObject mode = config["mode"];
      for (JsonPair k : mode) {
        readPin(String(k.key().c_str()).toInt(), k.value().as<String>());
      }
      loopEventMillis = millis();
    }
  } catch (const char *e) {
    print(String(e));
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
  } 
}
void checkTrigger(int pin, int value) {
  String p = String(pin);
  JsonObject trig = getTrigger();
  if (trig.containsKey(p)) {
    int bistable = getStable()[String(pin)] || 0;
    int v = value;
    if (bistable == 1|| bistable == 3) {
      v = 1 - v;
    }                                                       // troca o sinal quando é NC
    if ((bistable == 2 || bistable == 3) && v == 0) return;  // so aciona quando v for 1
    //checa se troca o sinal NC
    String pinTo = trig[p];
    if (pinTo.toInt() != pin)
      writePin(pinTo.toInt(), v);
  }
}

void writePin(int pin, int value) {
  String mode = getMode()[String(pin)];
  if (mode != NULL)
    if (mode == "adc")
      return;
    else {
      digitalWrite(pin, value);
    }
  else {
    initPinMode(pin,"out");
    digitalWrite(pin, value);
  }
}

String help() {
  String s = "set ldr_max x \r\n";
  s += "set ldr_min x \r\n";
  return s;
}

bool readFile(String filename, char *buffer, size_t maxLen) {
  File file = LittleFS.open(filename, "r");
  if (!file) {
    return false;
  }
  size_t len = file.size();
  if (len > maxLen) {
    len = maxLen;
  }
  file.readBytes(buffer, len);  //(buffer, len);
  buffer[len] = 0;
  file.close();
  return true;
}

// void setupAlexa() {
//   espalexa.begin();
//   espalexa.addDevice(config["label"], firstDeviceChanged);
// }

void firstDeviceChanged(uint8_t brightness) {
  if (brightness) {
    digitalWrite(RELAY_PIN, HIGH);
    Serial.print("ON, brightness ");
    Serial.println(brightness);
    print("RELAY ON");
  } else {
    digitalWrite(RELAY_PIN, LOW);
    print("RELAY OFF");
  }
}
