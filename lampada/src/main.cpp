#define BAUD_RATE 115200 // Change baudrate to your need

#ifdef AVR
#include <Arduino.h>
#include "protocol_base.h"
void setup()
{
  Serial.begin(BAUD_RATE);
  hwavr.setup();
}

void loop()
{
  {
    hwavr.loop();
  }

#elif UPLOAD_ONLY

#include <Arduino.h>
#ifdef ESP32
#include <WiFi.h>
#else
#include <ESP8266WiFi.h> // precisa ser a primeira linha para fixar: ISR not in IRAM!
#endif
#include <ArduinoJson.h>

void setup()
{
  Serial.begin(BAUD_RATE);
}

unsigned int timer = millis();
unsigned int value = 0;

void loop()
{
  if (millis() - timer > 1000)
  {
    Serial.println(value);
    value = 1 - value;
    timer = millis();
  }
}

#else

#include <Arduino.h>

#ifndef NO_WIFI
#ifdef ESP32
#include <WiFi.h>
#else
#include <ESP8266WiFi.h> // precisa ser a primeira linha para fixar: ISR not in IRAM!
#endif
#endif

#include <ArduinoJson.h>
#include "homeware_setup.h"

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
  homeware.config["board"] = "LCTECHRELAY";
#endif

#ifdef SONOFF_BASIC
  homeware.doCommand("gpio 12 mode out");
  homeware.doCommand("gpio 0 mode in");
  homeware.doCommand("gpio 0 trigger 12 bistable");
  homeware.doCommand("gpio 12 device onoff");
  homeware.doCommand("gpio 13 mode led");
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
#ifdef RESET
  homeware.doCommand("reset wifi");
  homeware.doCommand("save");
#endif
}

// main setup function
void setup()
{

  Serial.begin(BAUD_RATE);

  homeware_setup();

  setupServer();
  defaultConfig();

#ifndef NO_TIMER
  Serial.println(timer.getNow());
#endif
}

void loop()
{

  homeware_loop();
}
#endif