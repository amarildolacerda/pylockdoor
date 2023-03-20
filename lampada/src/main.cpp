

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

#ifdef ALEXA
#include <Espalexa.h>
#include "api/alexa.h"
Espalexa alexa = Espalexa();
#endif

#ifdef SINRICPRO
#include "SinricPro.h"
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
  // homeware.doCommand("reset factory");
  homeware.doCommand("set label gaz");
  homeware.doCommand("gpio A0 mode adc");
  homeware.doCommand("gpio 2 mode srn");
  homeware.doCommand("gpio 4 mode ok");
  homeware.setKey("adc_min", "0");
  homeware.setKeyIfNull("adc_max", "126");
  homeware.doCommand("gpio A0 trigger 2 monostable");
  homeware.doCommand("gpio 2 device motion");
  homeware.doCommand("gpio 2 sensor xxxx");
  homeware.doCommand("set app_key xxx");
  homeware.doCommand("set app_secret xxx");
  // homeware.doCommand("debug off");
  // homeware.doCommand("save");
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
  homeware.setup(&server);
#endif

#ifdef PORTAL
  portal.setup(&server);
  portal.autoConnect(homeware.config["label"]);
  Serial.printf("Ver: %s \r\n", VERSION);
#endif

  setupServer();
  defaultConfig();
#ifdef ALEXA

  Alexa::begin(alexa);
  alexa.begin(&server);
#endif
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
#ifdef ALEXA
  alexa.loop();
#endif

#ifdef SINRICPRO
  SinricPro.handle();
#endif

#endif
}
