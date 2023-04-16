#include <ESP8266WiFi.h> // precisa ser a primeira linha para fixar: ISR not in IRAM!

#include <Arduino.h>
#include <ArduinoJson.h>
#include "homeware_setup.h"

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
}

// main setup function
void setup()
{

  Serial.begin(BAUD_RATE);

  homeware_setup();

  setupServer();
  defaultConfig();

#ifndef BASIC
  Serial.println(timer.getNow());
#endif
}

void loop()
{

  homeware_loop();
}
