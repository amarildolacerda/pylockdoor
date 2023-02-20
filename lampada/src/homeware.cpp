#include <homeware.h>
#include <functions.h>

#include <ArduinoJson.h>
#include <FS.h>
#include <LittleFS.h>

#ifdef OTA
#include <ElegantOTA.h>
#endif

#include <ESP8266WiFi.h>
#include <mqtt.h>

#ifdef ALEXA
void alexaTrigger(int pin, int value);
#endif

void linha()
{
    Serial.println("-------------------------------");
}

void Homeware::setServer(ESP8266WebServer *externalServer)
{
    server = externalServer;
}

void Homeware::setupServer()
{
    server->on("/cmd", []()
               {
        if (homeware.server->hasArg("q"))
        {
            String cmd = homeware.server->arg("q");
            String rt = homeware.doCommand(cmd);
            if (!rt.startsWith("{"))
               rt = "\""+rt+"\"";
            homeware.server->send(200, "application/json", "{\"result\":" + rt + "}");
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

#ifdef ALEXA
    setupAlexa();
#endif
#ifdef TELNET
    setupTelnet();
#endif
    setupServer();

#ifdef OTA
    ElegantOTA.begin(server);
#endif
    server->begin();
    mqtt.setup(config["mqtt_host"], config["mqtt_port"], config["mqtt_prefix"], (config["mqtt_name"] != NULL) ? config["mqtt_name"] : config["label"]);
    mqtt.setUser(config["mqtt_user"], config["mqtt_password"]);
    inited = true;
}
void Homeware::setup(ESP8266WebServer *externalServer)
{
    setServer(externalServer);

    if (!LittleFS.begin())
    {
        Serial.println("LittleFS mount failed");
    }

    defaultConfig();
    restoreConfig();
    setupPins();
}
void Homeware::loop()
{
    if (!inited)
        begin();

    mqtt.loop();
    loopEvent();
#ifdef ALEXA
    alexa.loop();
#endif
#ifdef TELNET
    telnet.loop();
#endif
    mqtt.loop();
}

void Homeware::defaultConfig()
{
    config["label"] = LABEL;
    config["board"] = "esp8266";
    config.createNestedObject("mode");
    config.createNestedObject("trigger");
    config.createNestedObject("stable");
    config.createNestedObject("device");
    config["debug"] = inDebug ? "on" : "off";
    config["interval"] = "500";
    config["adc_min"] = "511";
    config["adc_max"] = "512";

    config["mqtt_host"] = "test.mosquitto.org";
    config["mqtt_port"] = 1883;
    config["mqtt_user"] = "homeware";
    config["mqtt_password"] = "123456780";
    config["mqtt_interval"] = 1;
    config["mqtt_prefix"] = "mesh";
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
JsonObject Homeware::getDevices()
{
    return config["device"].as<JsonObject>();
}

JsonObject Homeware::getMode()
{
    return config["mode"].as<JsonObject>();
}

JsonObject Homeware::getStable()
{
    return config["stable"].as<JsonObject>();
}

StaticJsonDocument<256> docPinValues;

int Homeware::writePin(const int pin, const int value)
{
    String mode = getMode()[String(pin)];
    if (mode != NULL)
        if (mode == "adc")
            return -1;
        else if (mode == "lc")
        {
            byte relON[] = {0xA0, 0x01, 0x01, 0xA2}; // Hex command to send to serial for open relay
            byte relOFF[] = {0xA0, 0x01, 0x00, 0xA1};
            if (value == 0)
            {
                Serial.write(relOFF, sizeof(relOFF));
            }
            else
                Serial.write(relON, sizeof(relON));
            docPinValues[String(pin)] = value;
        }

        else
        {
            digitalWrite(pin, value);
        }
    else
    {
        // initPinMode(pin, "out");
        digitalWrite(pin, value);
    }
    Serial.println(stringf("writePin: %d value: %d", pin, value));
    return value;
}

JsonObject Homeware::getValues()
{
    return docPinValues.as<JsonObject>();
}
int Homeware::readPin(const int pin, const String mode)
{
    int oldValue = docPinValues[String(pin)];
    int newValue = 0;
    if (mode == "adc")
    {
        newValue = analogRead(pin);
    }
    else if (mode == "lc")
    {
        newValue = docPinValues[String(pin)];
    }
    else if (mode == "ldr")
    {
        newValue = getAdcState(pin);
    }
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
#ifdef ALEXA
        alexaTrigger(pin, newValue);
#endif
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
    s += "set board <esp8266>\r\n";
    s += "show config\r\n";
    s += "gpio <pin> mode <in,out,adc,lc,ldr>\r\n";
    s += "gpio <pin> trigger <pin> [monostable,monostableNC,bistable,bistableNC]\r\n";
    s += "gpio <pin> device <onoff> (usado na alexa)\r\n";
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
{
    Serial.print("RSP: ");
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
            IPAddress x = localIP();
            sprintf(ip, "%d.%d.%d.%d", x[0], x[1], x[2], x[3]);
            FSInfo fs_info;
            LittleFS.info(fs_info);

            sprintf(buffer, "{ 'version':'%s', 'name': '%s', 'ip': '%s', 'total': %d, 'free': %s }", VERSION, String(config["label"]), ip, fs_info.totalBytes, String(fs_info.totalBytes - fs_info.usedBytes));
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
            String spin = cmd[1];
            if (cmd[2] == "none")
            {
                config["mode"].remove(cmd[1]);
                return "OK";
            }
            else if (cmd[2] == "get")
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
                initPinMode(pin, cmd[3]);
                return "OK";
            }
            else if (cmd[2] == "device")
            {
                JsonObject devices = getDevices();
                devices[spin] = cmd[3];
                return "OK";
            }
            else if (cmd[2] == "trigger")
            {
                // gpio 4 trigger 15 bistable
                JsonObject trigger = getTrigger();
                trigger[spin] = cmd[3];

                // 0-monostable 1-monostableNC 2-bistable 3-bistableNC
                getStable()[spin] = (cmd[4] == "bistable" ? 2 : 0) + (cmd[4].endsWith("NC") ? 1 : 0);

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
void alexaTrigger(int pin, int value)
{
    for (int i = 0; i < ESPALEXA_MAXDEVICES; i++)
    {
        EspalexaDevice *d = homeware.alexa.getDevice(i);
        if (d != nullptr && d->getValue() != value)
        {
            int id = d->getId();
            int index = 0;
            for (JsonPair k : homeware.getDevices())
            {
                if (index == id)
                {
                    d->setState(value != 0);
                    if (value > 0 && k.value().as<String>() == "onoff")
                    {
                        d->setValue(value);
                        d->setPercent(100);
                    }
                    Serial.printf("Alexa Pin %d setValue(%d)", pin, value);
                }
                index += 1;
            }
        }
    }
}
void onoffChanged(EspalexaDevice *d)
{
    if (d == nullptr)
        return;          // this is good practice, but not required
    int id = d->getId(); // * base 0
    Serial.printf("\r\nId: %d \r\n", id);
    bool value = d->getState();
    // procurar qual o pin associado pelo ID;
    JsonObject devices = homeware.getDevices();
    int index = 0;

    for (JsonPair k : devices)
    {
        // Serial.printf("Alexa: %s %s %d", k.key().c_str(), k.value(), value);
        if (index == (id))
        {
            int pin = String(k.key().c_str()).toInt();
            homeware.writePin(pin, (value) ? HIGH : LOW);
        }
        index += 1;
    }
}

void Homeware::setupAlexa()
{
    JsonObject devices = getDevices();

    Serial.println("\r\nDevices\r\n============================\r\n");
    for (JsonPair k : devices)
    {
        Serial.printf("%s is %s\r\n", k.key().c_str(), k.value().as<String>());
        String sName = config["label"];
        sName += "-";
        sName += k.key().c_str();
        if (k.value().as<String>() == "onoff")
        {
            alexa.addDevice(sName, onoffChanged, EspalexaDeviceType::onoff); // non-dimmable device
            Serial.printf("alexa: onoff em %s \r\n", sName);
        }
    }
    Serial.println("============================");
    alexa.begin(server);
}
#endif

void Homeware::setupTelnet()
{
    telnet.onConnect([](String ip)
                     {
        Serial.print("- Telnet: ");
        Serial.print(ip);
        Serial.println(" conectou");
        homeware.telnet.println("\nOlá " + homeware.telnet.getIP());
        homeware.telnet.println("(Use ^] + q  para desligar.)"); });
    telnet.onInputReceived([](String str)
                           { homeware.print(homeware.doCommand(str)); });

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

IPAddress Homeware::localIP()
{
    return WiFi.localIP();
}

Homeware homeware;
ESP8266WebServer server;
