#ifndef homeware_def
#define homeware_def

#include <ESP8266WiFi.h> //https://github.com/esp8266/Arduino
#include <ArduinoJson.h>

#define LABEL "sala"
#define VERSION "1.0.0"

class Homeware
{
public:
    static constexpr int SIZE_BUFFER = 1024;
    DynamicJsonDocument config = DynamicJsonDocument(SIZE_BUFFER);
    IPAddress localIP = IPAddress(0, 0, 0, 0);
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

private:
    void setupPins();
    void loopEvent();
};

#endif