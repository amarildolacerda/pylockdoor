#ifndef homeware_def
#define homeware_def

#include <ArduinoJson.h>

#define LABEL "sala"
#define VERSION "1.0.0"

class Homeware
{
public:
    static constexpr int SIZE_BUFFER = 1024;
    DynamicJsonDocument config = DynamicJsonDocument(SIZE_BUFFER);
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

private:
    void setupPins();
};

#endif