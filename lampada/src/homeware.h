#ifndef homeware_h
#define homeware_h
#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h> //https://github.com/esp8266/Arduino
#include <FS.h>
#include <LittleFS.h>

#include <config.h>


#define getChipId() (ESP.getChipId())

DynamicJsonDocument config(1024);
IPAddress localIP;

String print(String msg)
{
    Serial.println(msg);
    //telnet.println(msg);
    return msg;
}

void printConfig()
{
    serializeJson(config, Serial);
}
void linha()
{
    Serial.println("-------------------------------");
}
String *split(String s, const char delimiter)
{
    unsigned int count = 0;
    for (unsigned int i = 0; i < s.length(); i++)
    {
        if (s[i] == delimiter)
        {
            count++;
        }
    }

    String *words = new String[count + 1];
    unsigned int wordCount = 0;

    for (unsigned int i = 0; i < s.length(); i++)
    {
        if (s[i] == delimiter)
        {
            wordCount++;
            continue;
        }
        words[wordCount] += s[i];
    }
    // words[count+1] = 0;

    return words;
}

bool readFile(String filename, char *buffer, size_t maxLen)
{
    File file = LittleFS.open(filename, "r");
    if (!file)
    {
        return false;
    }
    size_t len = file.size();
    if (len > maxLen)
    {
        len = maxLen;
    }
    file.readBytes(buffer, len); //(buffer, len);
    buffer[len] = 0;
    file.close();
    return true;
}

String help()
{
    String s = "";
    s += "show config\r\n";
    s += "gpio <pin> mode <in,out,adc>\r\n";
    s += "gpio <pin> trigger <pin> [monostable,monostableNC,bistable,bistableNC]\r\n";
    s += "gpio <pin> get\r\n";
    s += "gpio <pin> set <n>\r\n";
    s += "set interval 50\r\n";
    s += "set adc_min 511 \r\n";
    s += "set adc_max 512 \r\n";
    return s;
}

//============================================================================
class Homeware
{
public:
    Homeware();
    String doCommand(String command);

    void loop();
    void setup();
    void defaultConfig();
    String restoreConfig();
    String saveConfig();
    JsonObject getMode();
    JsonObject getTrigger();
    JsonObject getStable();
    void readPin(int pin, String mode);
    void writePin(int pin, int value);
    void debug(String txt);
    void checkTrigger(int pin, int value);

private:
    void setupPins();
    void initPinMode(int pin, const String m);
    void loopEvent();
};

#endif