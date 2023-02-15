#include <homeware.h>
#include <functions.h>

#include <ArduinoJson.h>
#include <FS.h>
#include <LittleFS.h>

#ifdef OTA
#include <ElegantOTA.h>
#endif


void linha()
{
    Serial.println("-------------------------------");
}

Homeware *myself;
Homeware::Homeware(ESP8266WebServer *externalServer)
{
    server = externalServer;
    myself = this;
}

void Homeware::setupServer()
{
    server->on("/cmd", []()
               {
        if (myself->server->hasArg("q"))
        {
            String cmd = myself->server->arg("q");
            String rt = myself->doCommand(cmd);
            if (!rt.startsWith("{"))
               rt = "\""+rt+"\"";
            myself->server->send(200, "application/json", "{\"result\":" + rt + "}");
            return;
        } });

}
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

void Homeware::begin()
{
    if (inited)
        return;
#ifdef OTA
    ElegantOTA.begin(server);
#endif
    server->begin();
    inited = true;
}
void Homeware::setup()
{
    if (!LittleFS.begin())
    {
        Serial.println("LittleFS mount failed");
    }

    defaultConfig();
    restoreConfig();
    setupPins();
#ifdef ALEXA
    setupAlexa();
#endif
#ifdef TELNET
    setupTelnet();
    setupServer();
#endif
}
void Homeware::loop()
{
    if (!inited)
        begin();

    loopEvent();
#ifdef ALEXA
    alexa.loop();
#endif
#ifdef TELNET
    telnet.loop();
#endif
}

void Homeware::defaultConfig()
{
    config["label"] = LABEL;
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
    JsonObject mode = getMode();
    if (!mode[String(pin)])
        mode[String(pin)] = m;    
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

int Homeware::writePin(const int pin, const int value)
{
    String mode = getMode()[String(pin)];
    if (mode != NULL)
        if (mode == "adc")
            return -1;
        else
        {
            digitalWrite(pin, value);
        }
    else
    {
        initPinMode(pin, "out");
        digitalWrite(pin, value);
    }
    return value;
}

StaticJsonDocument<256> docPinValues;
int Homeware::readPin(const int pin, const String mode)
{
    int oldValue = docPinValues[String(pin)];
    int newValue = 0;
    if (mode == "adc")
        newValue = analogRead(pin);
    else
        newValue = digitalRead(pin);

    debug(stringf("readPin %d from %d to %d \r\n", pin, oldValue, newValue));

    if (oldValue != newValue)
    {
        char buffer[32];
        sprintf(buffer, "pin %d : %d ", pin, newValue);
        debug(buffer);
        docPinValues[String(pin)] = newValue;
        checkTrigger(pin, newValue);
    }
    return newValue;
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
        debug(stringf("pin %s trigger %s to %d \r\n", p, pinTo, v));
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

bool Homeware::readFile(String filename, char *buffer, size_t maxLen)
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

unsigned long loopEventMillis = millis();
void Homeware::loopEvent()
{
    try
    {
        unsigned long interval;
        try
        {
            interval = String(config["interval"]).toInt();
        }
        catch (char e)
        {
            interval = 500;
        }
        if (millis() - loopEventMillis > interval)
        {
            JsonObject mode = config["mode"];
            for (JsonPair k : mode)
            {
                readPin(String(k.key().c_str()).toInt(), k.value().as<String>());
            }
            loopEventMillis = millis();
        }
    }
    catch (const char *e)
    {
        print(String(e));
    }
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

String Homeware::print(String msg)
{   Serial.print("RSP: ");
    Serial.println(msg);
    telnet.println(msg);
    return msg;
}

String Homeware::doCommand(String command)
{
    try
    {
        String *cmd = split(command, ' ');
        Serial.print("CMD: ");
        Serial.println(command);
        if (cmd[0] == "format")
        {
            LittleFS.format();
            return "formated";
        }
        else if (cmd[0] == "open")
        {
            char json[1024];
            readFile(cmd[1], json, 1024);
            return String(json);
        }
        else if (cmd[0] == "help")
            return help();
        else if (cmd[0] == "show")
        {
            if (cmd[1] == "config")
                return config.as<String>();
            char buffer[32];
            char ip[20];
            sprintf(ip, "%d.%d.%d.%d", localIP[0], localIP[1], localIP[2], localIP[3]);
            FSInfo fs_info;
            LittleFS.info(fs_info);

            sprintf(buffer, "{ 'name': '%s', 'ip': '%s', 'total': %d, 'free': %s }", String(config["label"]), ip, fs_info.totalBytes, String(fs_info.totalBytes - fs_info.usedBytes));
            return buffer;
        }
        else if (cmd[0] == "reset")
        {
            if (cmd[1] == "factory")
            {
                defaultConfig();
                return "OK";
            }
            print("reiniciando...");
            delay(1000);
            // telnet.stop();
            ESP.restart();
            return "OK";
        }
        else if (cmd[0] == "save")
        {
            return saveConfig();
        }
        else if (cmd[0] == "restore")
        {
            return restoreConfig();
        }
        else if (cmd[0] == "set")
        {
            if (cmd[2] == "none")
            {
                config.remove(cmd[1]);
            }
            else
            {
                config[cmd[1]] = cmd[2];
                printConfig();
            }
            return "OK";
        }
        else if (cmd[0] == "get")
        {
            return config[cmd[1]];
        }
        else if (cmd[0] == "gpio")
        {
            int pin = cmd[1].toInt();
            if (cmd[2] == "get")
            {
                int v = digitalRead(pin);
                return String(v);
            }
            else if (cmd[2] == "set")
            {
                int v = cmd[3].toInt();
                writePin(pin, v);
                return String(v);
            }
            else if (cmd[2] == "mode")
            {
                JsonObject mode = config["mode"];
                initPinMode(cmd[1].toInt(), cmd[3]);
                return "OK";
            }
            else if (cmd[2] == "trigger")
            {
                // gpio 4 trigger 15 bistable
                JsonObject trigger = getTrigger();
                trigger[String(pin)] = cmd[3];

                // 0-monostable 1-monostableNC 2-bistable 3-bistableNC
                getStable()[String(pin)] = (cmd[4] == "bistable" ? 2 : 0) + (cmd[4].endsWith("NC") ? 1 : 0);

                return "OK";
            }
        }
        return "invalido";
    }
    catch (const char *e)
    {
        return String(e);
    }
}
void Homeware::printConfig()
{

    serializeJson(config, Serial);
}

void Homeware::debug(String txt)
{
    if (config["debug"] == "on")
    {
        print(txt);
    }
}

int Homeware::getAdcState(int pin)
{

    unsigned int tmpAdc = analogRead(pin);
    int rt = currentAdcState;
    const int v_min = config["adc_min"].as<int>();
    const int v_max = config["adc_max"].as<int>();
    if (tmpAdc >= v_max)
        rt = HIGH;
    if (tmpAdc < v_min)
        rt = LOW;
    if (rt != currentAdcState)
    {
        char buffer[64];
        sprintf(buffer, "adc %d,currentAdcState %d, adcState %d  (%i,%i) ", tmpAdc, currentAdcState, rt, v_max, v_min);
        debug(buffer);
    }
    return rt;
}
uint32_t Homeware::getChipId() { return ESP.getChipId(); }

#ifdef ALEXA
void Homeware::setupAlexa()
{
    alexa.begin(server);
}
#endif

void Homeware::setupTelnet()
{
    telnet.onConnect([](String ip)
                     {
        Serial.print("- Telnet: ");
        Serial.print(ip);
        Serial.println(" connected");
        myself->telnet.println("\nWelcome " + myself->telnet.getIP());
        myself->telnet.println("(Use ^] + q  to disconnect.)"); });
    telnet.onInputReceived([](String str)
                           { myself->print(myself->doCommand(str)); });

    Serial.print("- Telnet: ");
    if (telnet.begin())
    {
        Serial.println("running");
    }
    else
    {
        Serial.println("error.");
        errorMsg("Will reboot...");
    }
}
void Homeware::errorMsg(String msg)
{
    Serial.println(msg);
    telnet.println(msg);
}
