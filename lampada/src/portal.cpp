#include <Arduino.h>
#include <portal.h>
#include <functions.h>
#include <wm_strings_pt_BR.h>

void Portal::setup(ESP8266WebServer *externalServer)
{
    server = externalServer;
}

void Portal::autoConnect(const String slabel)
{
    WiFi.mode(WIFI_STA);
    label = slabel;
    hostname = stringf("%s.local", slabel);
    wifiManager.setMinimumSignalQuality(30);
    wifiManager.setDebugOutput(true);
    wifiManager.setHostname(hostname);
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
    return stringf("<br/><form action='%s' method='get'><button %s>%s</button></form>", link, style==""?"":stringf("class='%s'",style), name);
}

void setManager(WiFiManager *wf){
    String hostname = stringf("%s-local", portal.label);
    wf->setHostname(hostname);
    wf->setTitle("Homeware");
}
void Portal::setupServer()
{
    server->on("/", []()
               {
        WiFiManager wf  ;
        setManager(&wf);
    
        String pg = button("GPIO", "/gs");
        pg += button("Recarregar","/");
        portal.server->send(200, "text/html", wf.pageMake("Homeware", pg)); });

    server->on("/gs", []()
               {
        WiFiManager wf ;
        setManager(&wf);

        String pg = "GPIO Status<hr><br/>";
        pg+="<table>";
        pg+="<tr><td>pin</td><td>value</td></tr>";
        pg+="</table>";
        pg += button("Menu","/");
        portal.server->send(200, "text/html", wf.pageMake("Homeware",pg)); });
}

Portal portal;