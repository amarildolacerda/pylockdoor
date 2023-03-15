

#include <Arduino.h>

#include <ArduinoJson.h>
#include "options.h"

// needed for library
#ifdef ARDUINO_AVR
#include "protocol.h"
Protocol prot;
#else
#include "homeware.h"
#endif

#ifdef PORTAL
#include <portal.h>
#endif

#define BAUD_RATE 115200 // Change baudrate to your need

void defaultConfig()
{
#ifdef SONOFF_BASIC
  homeware.doCommand("gpio 12 mode out");
  homeware.doCommand("gpio 14 mode in");
  homeware.doCommand("gpio 14 trigger 12 bistable");
#endif
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
#ifdef ARDUINO_AVR
  prot.setup();
#else
  Serial.printf("\r\n\r\n");
  homeware.setup(&server);
#endif

#ifdef PORTAL
  portal.setup(&server);
  portal.autoConnect(homeware.config["label"]);
  Serial.printf("Ver: %s \r\n", VERSION);
#endif

  setupServer();
  defaultConfig();
}

void loop()
{
#ifdef PORTAL
  portal.loop(); // checa reconecta;
#endif
#ifdef ARDUINO_AVR
  prot.loop();
#else
  homeware.loop();
#endif
}
