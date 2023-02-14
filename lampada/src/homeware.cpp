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

void Homeware::setup(){
    defaultConfig();
    restoreConfig();
    setupPins();
}
void Homeware::loop(){

}

void Homeware::defaultConfig()
{
    config["label"] = "LABEL";
    config.createNestedObject("mode");
    config.createNestedObject("trigger");
    config.createNestedObject("stable");
    config["debug"] = inDebug ? "on" : "off";
    config["interval"] = "500";
    config["adc_min"] = "511";
    config["adc_max"] = "512";

    
}

String Homeware::saveConfig()
{
    String rsp = "OK";
    config["debug"] = inDebug ? "on" : "off"; // volta para o default para sempre ligar com debug desabilitado
    serializeJson(config, Serial);
    File file = LittleFS.open("/config.json", "w");
    if (serializeJson(config, file) == 0)
        rsp = "não gravou /config.json";
    file.close();
    return rsp;
}

void Homeware::initPinMode(int pin, const String m)
{
    if (m == "in")
        pinMode(pin, INPUT);
    else if (m == "out")
        pinMode(pin, OUTPUT);
}

void Homeware::setupPins()
{
    JsonObject mode = config["mode"];
    for (JsonPair k : mode)
    {
        int pin = String(k.key().c_str()).toInt();
        initPinMode(pin, k.value().as<String>());
        int trPin = getTrigger()[String(pin)];
        if (trPin)
        {
            initPinMode(trPin, "out");
        }
    }
}

JsonObject Homeware::getTrigger()
{
    return config["trigger"].as<JsonObject>();
}
