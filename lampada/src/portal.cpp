#include <Arduino.h>
#include <portal.h>
#include <functions.h>
#include <wm_strings_pt_BR.h>
#include <homeware.h>

#include <ESP8266WiFi.h>

void Portal::setup(ESP8266WebServer *externalServer)
{
    server = externalServer;
}

void Portal::autoConnect(const String slabel)
{
    WiFi.mode(WIFI_STA);
    label = slabel;
    hostname = stringf("%s.local", slabel);
    WiFi.setHostname(hostname);
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

String button(const String name, const char *link, const char *style = "", const String hidden = "")
{
    return stringf("<br/><form action='%s' method='get'> %s <button %s>%s</button></form>", link, hidden, (style == "") ? "" : String(stringf("class='%s'", style)), name);
}
String input(const String name, const String value)
{
    return String(stringf("<input type=\"text\" name=\"%s\" value=\"%s\">", name, value));
}

void setManager(WiFiManager *wf)
{
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
        String pg = "";
        JsonObject mode = homeware.getMode();
        for (JsonPair k : mode)
        {   
          if (k.value().as<String>()=="in"){
              String p1 = k.key().c_str();
              String v1 = k.value().as<String>();
              int v = homeware.readPin(p1.toInt(), v1);
              String s = (v == 1) ? "ON" : (v > 0) ? String(v)
                                                   : "OFF";
              String hd =input("p", p1);
              hd += input("q", ((s == "ON") ? "OFF" : "ON"));
              Serial.println(hd);

              pg += button(s, "/pin", "D",hd );
          }
        }

        pg += button("GPIO", "/gs");
        portal.server->send(200, "text/html", wf.pageMake("Homeware", pg)); });

    server->on("/pin", []()
               {
                //if (portal.server->hasArg("p") && portal.server->hasArg("q")){
                String p = portal.server->arg("p");
                String q = portal.server->arg("q");
                Serial.println(p);
                Serial.println(q);
                //if (p && t){
                    homeware.writePin(p.toInt(),(q=="ON")?1:0);
                //}
                //}
                portal.server->sendHeader("Location", String("/"), true);
                portal.server->send(302, "text/plain", ""); });
    server->on("/gs", []()
               {
        WiFiManager wf ;
        setManager(&wf);

        String pg = "GPIO Status<hr>";
        pg+="<table style=\"width:80%\">";
        pg+="<thead><tr><th>Pin</th><th>Mode</th><th>Value</th></tr></thead><tbody>";
        JsonObject mode = homeware.getMode();
        for (JsonPair k : mode)
        {
            String p1 = k.key().c_str();
            String v1 = k.value().as<String>();
            int v = homeware.readPin(p1.toInt(), v1);
            String s = (v==1)?"ON": (v>0)?  String(v):"OFF";
            pg += stringf("<tr><td>%s</td><td>%s</td><td>%s</td></tr>", p1, v1,s);
        }

        pg+="</tbody></table>";
        pg += button("Menu","/");
        portal.server->send(200, "text/html", wf.pageMake("Homeware",pg)); });
}

Portal portal;