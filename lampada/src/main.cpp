

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

#include <ESP8266WiFi.h> //https://github.com/esp8266/Arduino

// needed for library
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <ArduinoOTA.h>

DNSServer dnsServer;

#include <WiFiManager.h>
ESP8266WebServer server;
WiFiManager wifiManager;

#include "ESPTelnet.h"

#include <Espalexa.h>
Espalexa espalexa;
#include <homeware.h>
Homeware homeware = Homeware();

// Include libraries
#if defined ESP8266 || defined ESP32
#endif

#if defined ESP8266
#endif

#define BAUD_RATE 115200 // Change baudrate to your need

#define BUTTON_PIN 4
#define RELAY_PIN 15
#define inDebug false
unsigned long lastBtnPress;
IPAddress localIP;
int ldrState = 0;
bool myPowerState = false;
int tmpAdc = 0;
int adcState = 0;
bool isConnected = false;

ESPTelnet telnet;

//=========================================================================================
// declaracoes
//=========================================================================================
void debug(String txt);
void errorMsg(String msg);
void firstDeviceChanged(uint8_t brightness);
void setupTelnet();
String doCommand(String command);
void linha();

//=========================================================================================
#define getChipId() (ESP.getChipId())

char *stringf(const char *format, ...)
{
  static char buffer[512];

  va_list args;
  va_start(args, format);
  vsnprintf(buffer, sizeof(buffer), format, args);
  va_end(args);

  return buffer;
}

void setupAlexa()
{
  espalexa.begin(&server);
  espalexa.addDevice(homeware.config["label"], firstDeviceChanged);
}

String print(String msg)
{
  Serial.println(msg);
  telnet.println(msg);
  return msg;
}

int getAdc()
{
  tmpAdc = analogRead(0);
  int rt = ldrState;
  const int v_min = homeware.config["adc_min"].as<int>();
  const int v_max = homeware.config["adc_max"].as<int>();
  if (tmpAdc >= v_max)
    rt = HIGH; // quando acende a luz, sobe o medidor com a propria luz que foi acionada, para não desligar.
  if (tmpAdc < v_min)
    rt = LOW;
  if (rt != ldrState)
  {
    char buffer[64];
    sprintf(buffer, "adc %d,ldrState %d, adcState %d  (%i,%i) ", tmpAdc, ldrState, rt, v_max, v_min);
    debug(buffer);
  }
  return rt;
}

// setup function for WiFi connection
void setupWiFi()
{
  Serial.printf("\r\n[Wifi]: Connecting");
  wifiManager.autoConnect("AutoConnectAP");
  localIP = WiFi.localIP();
  Serial.printf("V: %s \r\n", VERSION);
}

// setup function for SinricPro

void defaultConfig()
{
  doCommand("gpio 4 trigger 15 monostable");
}


void setupOTA()
{
  ArduinoOTA.onStart([]()
                     { Serial.println("Start"); });
  ArduinoOTA.onEnd([]()
                   { Serial.println("\nEnd"); });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total)
                        { Serial.printf("Progress: %u%%\r", (progress / (total / 100))); });
  ArduinoOTA.onError([](ota_error_t error)
                     {
      Serial.printf("Error[%u]: ", error);
      if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
      else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
      else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
      else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
      else if (error == OTA_END_ERROR) Serial.println("End Failed"); });
  ArduinoOTA.begin();
}

void setupServer()
{
  server.on("/show", {[]()
                      {
                        // wifiManager.resetSettings();
                        String rt = doCommand("show");
                        server.send(200, "application/json", "{\"result\":" + rt + "}");
                        // ESP.restart();
                      }});
}

// main setup function
void setup()
{
  pinMode(BUTTON_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT); // define LED GPIO as output

  Serial.begin(BAUD_RATE);
  Serial.printf("\r\n\r\n");
  setupWiFi();

  if (!LittleFS.begin())
  {
    Serial.println("LittleFS mount failed");
  }
  setupOTA();

  setupServer();

  setupTelnet();
  homeware.setup();

  setupAlexa();
}

void onTelnetConnect(String ip)
{
  Serial.print("- Telnet: ");
  Serial.print(ip);
  Serial.println(" connected");
  telnet.println("\nWelcome " + telnet.getIP());
  telnet.println("(Use ^] + q  to disconnect.)");
}
void onTelnetDisconnect(String ip)
{
  Serial.print("- Telnet: ");
  Serial.print(ip);
  Serial.println(" disconnected");
}

void setupTelnet()
{
  telnet.onConnect(onTelnetConnect);
  telnet.onInputReceived([](String str)
                         { print(doCommand(str)); });

  Serial.print("- Telnet: ");
  if (telnet.begin())
  {
    Serial.println("running");
  }
  else
  {
    Serial.println("error.");
    errorMsg("Will reboot...");
  }
}
void errorMsg(String msg)
{
  Serial.println(msg);
  telnet.println(msg);
}

void loop()
{
  ArduinoOTA.handle();
  telnet.loop();
  homeware.loop();
  espalexa.loop();
}

void printCmds(String *cmd)
{
  Serial.println("command:");
  for (unsigned int i = 0; i < sizeof(cmd); i++)
  {
    if (cmd[i] != NULL)
    {
      Serial.print(cmd[i]);
      Serial.print(" ");
    }
  }
  Serial.println("");
}
String *split(String s, const char delimiter)
{
  unsigned int count = 0;
  for (unsigned int i = 0; i < s.length(); i++)
  {
    if (s[i] == delimiter)
    {
      count++;
    }
  }

  String *words = new String[count + 1];
  unsigned int wordCount = 0;

  for (unsigned int i = 0; i < s.length(); i++)
  {
    if (s[i] == delimiter)
    {
      wordCount++;
      continue;
    }
    words[wordCount] += s[i];
  }
  // words[count+1] = 0;

  return words;
}


void linha()
{
  Serial.println("-------------------------------");
}
void printConfig()
{

  serializeJson(homeware.config, Serial);
}


String doCommand(String command)
{
  try
  {
    String *cmd = split(command, ' ');
    Serial.println(command);
    if (cmd[0] == "format")
    {
      LittleFS.format();
      return "formated";
    }
    else if (cmd[0] == "open")
    {
      char json[1024];
      homeware.readFile(cmd[1], json, 1024);
      return String(json);
    }
    else if (cmd[0] == "help")
      return homeware.help();
    else if (cmd[0] == "show")
    {
      if (cmd[1] == "config")
        return homeware.config.as<String>();
      char buffer[32];
      char ip[20];
      sprintf(ip, "%d.%d.%d.%d", localIP[0], localIP[1], localIP[2], localIP[3]);
      FSInfo fs_info;
      LittleFS.info(fs_info);

      sprintf(buffer, "{ 'name': '%s', 'ip': '%s', 'total': %d, 'free': %s }", String(homeware.config["label"]), ip, fs_info.totalBytes, String(fs_info.totalBytes - fs_info.usedBytes));
      return buffer;
    }
    else if (cmd[0] == "reset")
    {
      if (cmd[1] == "factory")
      {
        defaultConfig();
        return "OK";
      }
      print("reiniciando...");
      delay(1000);
      telnet.stop();
      ESP.restart();
      return "OK";
    }
    else if (cmd[0] == "save")
    {
      return homeware.saveConfig();
    }
    else if (cmd[0] == "restore")
    {
      return homeware.restoreConfig();
    }
    else if (cmd[0] == "set")
    {
      if (cmd[2] == "none")
      {
        homeware.config.remove(cmd[1]);
      }
      else
      {
        homeware.config[cmd[1]] = cmd[2];
        printConfig();
      }
      return "OK";
    }
    else if (cmd[0] == "get")
    {
      return homeware.config[cmd[1]];
    }
    else if (cmd[0] == "gpio")
    {
      int pin = cmd[1].toInt();
      if (cmd[2] == "get")
      {
        int v = digitalRead(pin);
        return String(v);
      }
      else if (cmd[2] == "set")
      {
        int v = cmd[3].toInt();
        Serial.printf("set pin %d to %d \r\n", pin, v);
        digitalWrite(pin, (v == 0) ? LOW : HIGH);
        return "OK";
      }
      else if (cmd[2] == "mode")
      {
        JsonObject mode = homeware.config["mode"];
        mode[cmd[1]] = cmd[3];
        homeware.initPinMode(cmd[1].toInt(), cmd[3]);
        printConfig();
        return "OK";
      }
      else if (cmd[2] == "trigger")
      {
        // gpio 4 trigger 15 bistable
        JsonObject trigger = homeware.getTrigger();
        trigger[String(pin)] = cmd[3];

        // 0-monostable 1-monostableNC 2-bistable 3-bistableNC
        homeware.getStable()[String(pin)] = (cmd[4] == "bistable" ? 2 : 0) + (cmd[4].endsWith("NC") ? 1 : 0);

        return "OK";
      }
    }
    return "invalido";
  }
  catch (const char *e)
  {
    return String(e);
  }
}

void debug(String txt)
{
  if (homeware.config["debug"] == "on")
  {
    print(txt);
  }
}



void firstDeviceChanged(uint8_t brightness)
{
  if (brightness)
  {
    digitalWrite(RELAY_PIN, HIGH);
    Serial.print("ON, brightness ");
    Serial.println(brightness);
    print("RELAY ON");
  }
  else
  {
    digitalWrite(RELAY_PIN, LOW);
    print("RELAY OFF");
  }
}
