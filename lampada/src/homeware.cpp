#include <homeware.h>

#include <ArduinoJson.h>
#include <FS.h>
#include <LittleFS.h>

String Homeware::restoreConfig()
{
    String rt = "nao restaurou config";
    Serial.println("");
    // linha();
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
            // debug(stringf("lido: %s \r\n corrente: %s \r\n", novo, old));
            config.clear();
            deserializeJson(config, old);
            return "Error: " + String(novo);
        }
        serializeJson(config, Serial);
        Serial.println("");
        rt = "OK";
        // linha();
    }
    catch (const char *e)
    {
        return String(e);
    }
    Serial.println("");
    return rt;
}

void Homeware::setup()
{
    defaultConfig();
    restoreConfig();
    setupPins();
}
void Homeware::loop()
{
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

JsonObject Homeware::getMode()
{
    return config["mode"].as<JsonObject>();
}

JsonObject Homeware::getStable()
{
    return config["stable"].as<JsonObject>();
}

void Homeware::writePin(int pin, int value)
{
    String mode = getMode()[String(pin)];
    if (mode != NULL)
        if (mode == "adc")
            return;
        else
        {
            digitalWrite(pin, value);
        }
    else
    {
        initPinMode(pin, "out");
        digitalWrite(pin, value);
    }
    //debug(stringf("writePin %d to %d\r\n", pin, value));
}

StaticJsonDocument<256> docPinValues;
void Homeware::readPin(int pin, String mode)
{
    int oldValue = docPinValues[String(pin)];
    int newValue = 0;
    if (mode == "adc")
        newValue = analogRead(pin);
    else
        newValue = digitalRead(pin);

    //debug(stringf("readPin %d from %d to %d \r\n", pin, oldValue, newValue));

    if (oldValue != newValue)
    {
        char buffer[32];
        sprintf(buffer, "pin %d : %d ", pin, newValue);
        //debug(buffer);
        docPinValues[String(pin)] = newValue;
        checkTrigger(pin, newValue);
    }
}

void Homeware::checkTrigger(int pin, int value)
{
    String p = String(pin);
    JsonObject trig = getTrigger();
    if (trig.containsKey(p))
    {
        int bistable = getStable()[String(pin)] || 0;
        int v = value;
        if (bistable == 1 || bistable == 3)
        {
            v = 1 - v;
        } // troca o sinal quando é NC
        if ((bistable == 2 || bistable == 3) && v == 0)
            return; // so aciona quando v for 1
        // checa se troca o sinal NC
        String pinTo = trig[p];
        //debug(stringf("pin %s trigger %s to %d \r\n", p, pinTo, v));
        if (pinTo.toInt() != pin)
            writePin(pinTo.toInt(), v);
    }
}

String Homeware::help()
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
