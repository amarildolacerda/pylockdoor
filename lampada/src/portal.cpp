#include <Arduino.h>
#include <portal.h>
#include <functions.h>
#include <wm_strings_pt_BR.h>

Portal *curPortal;
Portal::Portal(ESP8266WebServer *externalServer)
{
    server = externalServer;
    curPortal = this;
}

void Portal::autoConnect(const String label)
{
    WiFi.mode(WIFI_STA);
    hostname = stringf("%s-local", label);
    wifiManager.setMinimumSignalQuality(30);
    wifiManager.setDebugOutput(true);
    wifiManager.autoConnect(hostname);
    setupServer();
}

void Portal::reset()
{
    WiFiManager wifiManager;
    WiFi.mode(WIFI_STA);
    WiFi.persistent(true);
    WiFi.disconnect(true);
    WiFi.persistent(false);
    wifiManager.resetSettings();
    ESP.reset();
    delay(1000);
}

String button(String name, String link, String style = "")
{
    return stringf("<br/><form action='%s' method='get'><button class='%s'>%s</button></form>", link, style, name);
}
void Portal::setupServer()
{
    server->on("/", []()
               {
        WiFiManager wf ;
        String pg = button("GPIO", "/gpio");
        pg += button("Recarregar","/");
        curPortal->server->send(200, "text/html", wf.pageMake("Homeware",pg)); });
}