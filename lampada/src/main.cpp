

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
#include "options.h"

// needed for library
#include <homeware.h>
#ifdef PORTAL
#include <portal.h>
#endif

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
  // homeware.doCommand("reset");
  // homeware.doCommand(stringf("gpio %d mode in", BUTTON_PIN));
  // homeware.doCommand(stringf("gpio %d mode out", RELAY_PIN));
  // homeware.doCommand("gpio 4 trigger 15 monostable");
  // homeware.doCommand("gpio 15 device onoff");
  // homeware.printConfig();
}

void setupServer()
{
#ifdef PORTAL
  homeware.server->on("/clear", []()
                      {
        Serial.println("reiniciando");
        homeware.server->send(200, "text/html", "reiniciando...");
        portal.reset(); });
#endif
}

// main setup function
void setup()
{

  Serial.begin(BAUD_RATE);
  Serial.printf("\r\n\r\n");
  homeware.setup(&server);
#ifdef PORTAL
  portal.setup(&server);
  portal.autoConnect(homeware.config["label"]);
#endif
  Serial.printf("Ver: %s \r\n", VERSION);

  setupServer();
  defaultConfig();
}

void loop()
{
#ifdef PORTAL
  portal.loop(); // checa reconecta;
#endif
  homeware.loop();
}
