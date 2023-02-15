#include <Arduino.h>
#include <portal.h>
#include <functions.h>

Portal::Portal(ESP8266WebServer *externalServer ){
    server = externalServer;
}

void Portal::autoConnect(const String label){
    hostname = stringf("%s-%d", label, getChipId());
    wifiManager.setMinimumSignalQuality(30);
    wifiManager.setDebugOutput(true);
    wifiManager.autoConnect(hostname);
}

void Portal::reset(){
    WiFiManager wifiManager;
    WiFi.mode(WIFI_STA);
    WiFi.persistent(true);
    WiFi.disconnect(true);
    WiFi.persistent(false);
    wifiManager.resetSettings();
    ESP.reset();
    delay(1000);
}