

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
#include <portal.h>
#include <homeware.h>

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


void defaultConfig()
{
 // homeware.doCommand("reset factory"); 
 // homeware.doCommand("save");
  //homeware.doCommand("reset");
  // homeware.doCommand(stringf("gpio %d mode in", BUTTON_PIN));
  // homeware.doCommand(stringf("gpio %d mode out", RELAY_PIN));
  // homeware.doCommand("gpio 4 trigger 15 monostable");
  // homeware.doCommand("gpio 15 device onoff");
  // homeware.printConfig();
}

void setupServer()
{
  homeware.server->on("/clear", []()
                      {
        Serial.println("reiniciando");
        homeware.server->send(200, "text/html", "reiniciando...");
        portal.reset(); });
}

// main setup function
void setup()
{

  Serial.begin(BAUD_RATE);
  Serial.printf("\r\n\r\n");
  homeware.setup(&server);
  portal.setup(&server);
  portal.autoConnect(homeware.config["label"]);
  Serial.printf("Ver: %s \r\n", VERSION);

  setupServer();
  defaultConfig();
  homeware.begin();
}

void loop()
{
  portal.loop(); // checa reconecta;
  homeware.loop();
}
