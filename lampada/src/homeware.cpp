#include <homeware.h>

#include <ArduinoJson.h>
#include <FS.h>
#include <LittleFS.h>

String Homeware::restoreConfig()
{
    String rt = "nao restaurou config";
    Serial.println("");
    //linha();
    try
    {
        String old = config.as<String>();
        File file = LittleFS.open("/config.json", "r");
        if (!file)
            return "erro ao abrir /config.json";
        String novo = file.readString();
        config.clear();
        auto error = deserializeJson(config, novo);
        if (error)
        {
            //debug(stringf("lido: %s \r\n corrente: %s \r\n", novo, old));
            config.clear();
            deserializeJson(config, old);
            return "Error: " + String(novo);
        }
        serializeJson(config, Serial);
        Serial.println("");
        rt = "OK";
        //linha();
    }
    catch (const char *e)
    {
        return String(e);
    }
    Serial.println("");
    return rt;
}
