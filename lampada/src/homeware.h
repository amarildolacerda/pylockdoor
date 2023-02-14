

#ifndef homeware_def
#define homeware_def

#include <ESP8266WiFi.h> //https://github.com/esp8266/Arduino
#include <ESP8266WebServer.h>

#include <ArduinoJson.h>

#define LABEL "sala"
#define VERSION "1.0.0"
#define ALEXA
#define TELNET

#ifdef ALEXA
#include <Espalexa.h>
#endif
#ifdef TELNET
#include "ESPTelnet.h"
#endif

char *stringf(const char *format, ...);
void linha();

class Homeware
{
public:
    Homeware(ESP8266WebServer *externalServer = nullptr);
    static constexpr int SIZE_BUFFER = 1024;
    DynamicJsonDocument config = DynamicJsonDocument(SIZE_BUFFER);
    IPAddress localIP = IPAddress(0, 0, 0, 0);
#ifdef ALEXA
    Espalexa espalexa = Espalexa();
#endif
#ifdef TELNET
    ESPTelnet telnet;
#endif
    ESP8266WebServer *server;
    unsigned currentAdcState = 0;
    bool inDebug = false;
    void setup();
    void loop();
    String restoreConfig();
    void defaultConfig();
    String saveConfig();
    void initPinMode(int pin, const String m);
    JsonObject getTrigger();
    JsonObject getStable();
    JsonObject getMode();
    void writePin(int pin, int value);
    void readPin(int pin, String mode);
    void checkTrigger(int pin, int value);
    String help();
    bool readFile(String filename, char *buffer, size_t maxLen);
    String doCommand(String command);
    String print(String msg);
    void printConfig();
    void debug(String txt);
    int getAdcState(int pin);
    uint32_t getChipId();
    void errorMsg(String msg);

private:
    void setupPins();
    void loopEvent();
#ifdef ALEXA
    void setupAlexa();
#endif
#ifdef TELNET
    void setupTelnet();
#endif
};

#endif
