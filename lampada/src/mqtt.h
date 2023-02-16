

#ifndef mqtt_h
#define mqtt_h

#include <functions.h>
#include <PubSubClient.h>
#include <ESP8266WiFi.h>

WiFiClient mqttWifiClient;
PubSubClient mqttClient(mqttWifiClient);

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];

void callback(char *topic, byte *payload, unsigned int length)
{
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    for (int i = 0; i < length; i++)
    {
        Serial.print((char)payload[i]);
    }
    Serial.println();
}

class MQTT
{
public:
    String prefix;
    String name;
    String user;
    String password;
    String host;
    int port;
    unsigned long interval = 1;
    String getTopic()
    {
        return prefix + "/" + name;
    }
    String getTopicIN()
    {
        return getTopic() + "/in";
    }
    void setup(const char *ahost, const int aport, const char *aprefix, const char *aname)
    {
        if (aname)
            name = aname;
        else
            name = String(getChipId(), HEX);
        Serial.println(String(getChipId(), HEX));
        prefix = aprefix;
        host = ahost;
        port = aport;
        mqttClient.setCallback(callback);
    }
    void setUser(const String user, const String pass)
    {
        this->user = user;
        this->password = pass;
    }
    void loop()
    {
        if (reconnect())
            mqttClient.loop();
    }
    bool isConnected()
    {
        return mqttClient.connected();
    }
    bool send(const char *subtopic, const char *payload)
    {
        if (isConnected())
        {
            char topic[64];
            sprintf(topic, "%s/%s%s", prefix, name, subtopic);

            sprintf(msg, payload);
            Serial.println(topic);
            Serial.println(msg);
            return mqttClient.publish(topic, msg);
        }
        return false;
    }

private:
    unsigned long lastReconnect = 0;
    bool reconnect()
    {
        // Loop until we're reconnected
        if (millis() - lastReconnect > 500)
            while (!mqttClient.connected())
            {
                lastReconnect = millis();
                Serial.print("MQTT connection...");
                String clientId = String(getChipId(), HEX);
                Serial.println(clientId);

                Serial.println(name.c_str());
                Serial.println(host.c_str());
                mqttClient.setServer(host.c_str(), port);

                if (mqttClient.connect(clientId.c_str()))
                {
                    Serial.println("connected");
                    send("/response", "online");
                    char subscribe[64];
                    sprintf(subscribe, "%s", getTopicIN());
                    Serial.println(subscribe);
                    mqttClient.subscribe(subscribe);
                    return true;
                }
                else
                {
                    //  Serial.print("failed, rc=");
                    //  Serial.print(mqttClient.state());
                    Serial.println(" try again in 5 seconds");
                    return false;
                }
            }
        return true;
    }
};

MQTT mqtt;
extern MQTT mqtt;

#endif
