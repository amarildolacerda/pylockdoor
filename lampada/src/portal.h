
#ifndef portal_def
#define portal_def

#include <WManager.h>

class Portal
{
public:
    char *hostname;
    WiFiManager wifiManager = WiFiManager();
    ESP8266WebServer *server;
    String label;
    void setup(ESP8266WebServer *externalServer = nullptr);
    void autoConnect(const String label);
    void reset();

private:
    void setupServer();
};

extern Portal portal;

#endif