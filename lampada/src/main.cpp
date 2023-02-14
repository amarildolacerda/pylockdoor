

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

DNSServer dnsServer;

#include <WiFiManager.h>
ESP8266WebServer server;
WiFiManager wifiManager;


#include <homeware.h>
Homeware homeware = Homeware(&server);

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
int ldrState = 0;
bool myPowerState = false;
int tmpAdc = 0;
int adcState = 0;
bool isConnected = false;


//=========================================================================================
// declaracoes
//=========================================================================================
void firstDeviceChanged(uint8_t brightness);

//=========================================================================================


// setup function for WiFi connection
void setupWiFi()
{
  Serial.printf("\r\n[Wifi]: Connecting");
  wifiManager.autoConnect("AutoConnectAP");
  homeware.localIP = WiFi.localIP();
  Serial.printf("V: %s \r\n", VERSION);
}

// setup function for SinricPro

void defaultConfig()
{
  homeware.doCommand("gpio 4 trigger 15 monostable");
}


void setupServer()
{
  server.on("/show", {[]()
                      {
                        // wifiManager.resetSettings();
                        String rt = homeware.doCommand("show");
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



  homeware.setup();
  setupServer();
  defaultConfig();
  homeware.alexa.addDevice(homeware.config["label"], firstDeviceChanged);
}


void loop()
{
  homeware.loop();
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


void firstDeviceChanged(uint8_t brightness)
{
  if (brightness)
  {
    digitalWrite(RELAY_PIN, HIGH);
    Serial.print("ON, brightness ");
    Serial.println(brightness);
    homeware.print("RELAY ON");
  }
  else
  {
    digitalWrite(RELAY_PIN, LOW);
    homeware.print("RELAY OFF");
  }
}
