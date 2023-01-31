#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char *mqttServer = "";
const int mqttPort = 1883;
const char *mqttUser = "";
const char *mqttPassword = "";

WiFiClient espClient;
PubSubClient client(espClient);

// Read the config from file
DynamicJsonDocument config(1024);

void configDefault()
{
    config["mqtt_name"] = "interruptor";
    config["mqtt_host"] = "broker.emqx.io";
    config["mqtt_port"] = 1883 config["mqtt_user"] = "" config["mqtt_password"] = ""
}
// Function to parse a JSON configuration file
void readConfig()
{
    File configFile = SPIFFS.open(config_file, "r");
    if (!configFile)
    {
        Serial.println("Failed to open config file");
        return;
    }
    DeserializationError error = deserializeJson(config, configFile);
    if (error)
    {
        Serial.println("Failed to parse config file");
        return;
    }
}

void writeConfig()
{
    File configFile = SPIFFS.open(config_file, "w");
    if (!configFile)
    {
        Serial.println("Failed to open config file");
        return;
    }
    serializeJson(config, configFile);
    configFile.close();
}

void setup()
{
    configDefault();
    // Read the config from file
    readConfig();

    // Connect to Wifi
    WiFiManager wifiManager;
    wifiManager.autoConnect();

    // Connect to MQTT server
    client.setServer(config["mqtt_host"], "mqtt_port");
    client.connect("MashEspClient");

    // Subscribe to MQTT topic
    client.subscribe(inTopic().c_str());
    client.setCallback(mqttCallback);
}
String inTopic()
{
    return String("mesh/") + config["mqtt_name"] + "/in";
}

void mqttCallback(char *topic, byte *payload, unsigned int length)
{
    String message;
    for (int i = 0; i < length; i++)
    {
        message += (char)payload[i];
    }
    handleMessage(message);
}

void loop()
{
    if (!client.connected())
    {
        reconnect();
    }
    client.loop();
}

void setPinMode(pin, tp)
{
    // Check if the third word is "in" or "out"
    if (tp == "in")
    {
        pinMode(pin, INPUT);
    }
    else if (tp == "out")
    {
        pinMode(pin, OUTPUT);
    }
}
void degitalW(pin, value)
{
    // Check if the third word is "1" or "high"
    if (value == "1" || value == "high")
    {
        digitalWrite(pin, HIGH);
    }
    else if (value == "0" || value == "low")
    {
        digitalWrite(pin, LOW);
    }
}
int digitalR(pin)
{
    return digitalRead(pin);
}

void handleMessage(String message)
{
    // Parse the message into words
    words = message.split(" ");
    String response = "";
    // Check if the first word is "gpio"
    if (words[0] == "save")
    {
        writeConfig();
    }
    else if (words[0])
        == 'set'
        {
            config[words[1]] = words[2];
        }
    else if (words[0])
        == "get"
        {
            response = config[words[1]];
        }
    else if (words[0] == "gpio")
    {
        // Parse the pin number
        int pin = words[1].toInt();

        // Check if the second word is "mode"
        if (words[2] == "mode")
        {
            setPinMode(pin, words[3]);
        }
        else if (words[2] == "set")
        {
            digitalW(pin, words[3]);
            response = digitalR(pin);
        }
        else if (words[2] == "get")
        {
            response = digitalR(pin)
        }

        client.publish("mesh/" + device_id + "/response", response.c_str());
    }
}
