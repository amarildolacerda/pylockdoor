
#ifndef portal_def
#define portal_def

#include <WManager.h>

class Portal
{
public:
    Portal(ESP8266WebServer *externalServer = nullptr);
    char *hostname;
    WiFiManager wifiManager = WiFiManager();
    ESP8266WebServer *server;
    void autoConnect(const String label);
    void reset();

private:
    void setupServer();
};

#endif