

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

//--------------------------------- modelos de config
// #define GAZ
// #define RELAY
// #define PIR
// #define INUNDACAO
//---------------------------------------------------

void defaultConfig()
{
#ifdef LCTECHRELAY
  homeware.doCommand("gpio 17 mode lc");
  homeware.doCommand("gpio 17 device onoff");
#endif

#ifdef SONOFF_BASIC
  homeware.doCommand("gpio 12 mode out");
  homeware.doCommand("gpio 14 mode in");
  homeware.doCommand("gpio 14 trigger 12 bistable");
  homeware.doCommand("gpio 12 device onoff");
  homeware.config["board"] = "SONOFF";
#endif

#ifdef RELAY
  homeware.doCommand(stringf("gpio %d mode in", 4));
  homeware.doCommand(stringf("gpio %d mode out", 15));
  homeware.doCommand("gpio 4 trigger 15 bistable");
  homeware.doCommand("gpio 15 device onoff");
#endif
#ifdef INUNDACAO
  homeware.doCommand(stringf("gpio %s mode adc", A0));
  homeware.doCommand(stringf("gpio %d mode srn", 2));
  homeware.doCommand("gpio 0 trigger 2 monostable");
  homeware.doCommand("gpio 2 device onoff");
  homeware.setKey("adc_min", "0");
  homeware.setKeyIfNull("adc_max", "125");
#endif
#ifdef PIR
  homeware.doCommand(stringf("gpio %d mode in", 4));
  homeware.doCommand(stringf("gpio %d mode srn", 2));
  homeware.doCommand("gpio 4 trigger 2 monostable");
  homeware.doCommand("gpio 2 device onoff");
#endif

#ifdef GAZ
  homeware.doCommand("gpio A0 mode adc");
  homeware.setKey("adc_min", "0");
  homeware.setKeyIfNull("adc_max", "240");
  homeware.doCommand("gpio 15 mode out");
  homeware.doCommand("gpio A0 trigger 15 monostable");
  homeware.doCommand("gpio 15 device onoff");
#endif
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
  homeware.prepare();
  defaultConfig();
  homeware.setup(&server);
#endif

#ifdef PORTAL
  portal.setup(&server);
  portal.autoConnect(homeware.config["label"]);
  Serial.printf("Ver: %s \r\n", VERSION);
#endif

  setupServer();
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
