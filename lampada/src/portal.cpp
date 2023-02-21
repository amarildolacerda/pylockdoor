#include <Arduino.h>
#include <portal.h>
#include <functions.h>
#include <wm_strings_pt_BR.h>
#include <homeware.h>

#include <ESP8266WiFi.h>
#include <chart.h>

void Portal::setup(ESP8266WebServer *externalServer)
{
    server = externalServer;
}
void Portal::loop()
{
    if ((WiFi.status() != WL_CONNECTED) || (WiFi.localIP().toString() == "0.0.0.0"))
    {
        WiFi.reconnect();
    }
}

void onStationConnected(const WiFiEventSoftAPModeStationConnected &evt)
{
    homeware.connected = true;
    Serial.print("Station connected: ");
    // Serial.println(macToString(evt.mac));
}

void onStationDisconnected(const WiFiEventSoftAPModeStationDisconnected &evt)
{
    homeware.connected = false;
    Serial.print("Station disconnected: ");
    // Serial.println(macToString(evt.mac));
}

void Portal::autoConnect(const String slabel)
{
    unsigned start = millis();
    unsigned timeLimitMsec = 20000;

    label = slabel;
    WiFi.onSoftAPModeStationConnected(&onStationConnected);
    WiFi.onSoftAPModeStationDisconnected(&onStationDisconnected);
    WiFi.setAutoReconnect(true);
    if (homeware.config["password"] && homeware.config["ssid"])
    {
        WiFi.enableSTA(true);
        WiFi.begin(homeware.config["ssid"], String(homeware.config["password"]));
        Serial.println(String(homeware.config["ssid"]));
        while (WiFi.status() != WL_CONNECTED && millis() - start < timeLimitMsec)
        {
            delay(500);

            Serial.print(".");
        }
        Serial.print("\r\nIP: ");
        Serial.print(WiFi.localIP());
        Serial.println("");
    }
    /* NAO FUNCIONOU
       unsigned start = millis();
       unsigned timeLimitMsec = 30000;

       if (!homeware.config["ssid"])
       {
           WiFi.softAPdisconnect();
           WiFi.enableAP(false);
           Serial.println("SmartConfig.");
           WiFi.beginSmartConfig();
           while (!WiFi.smartConfigDone() && millis() - start < timeLimitMsec)
           {
               delay(500);
               Serial.print(".");
           }
           WiFi.stopSmartConfig();
       }
       */
    bool connected = (WiFi.status() == WL_CONNECTED);

    if (!connected)
    {
        WiFi.mode(WIFI_AP_STA);
        hostname = stringf("%s.local", slabel);
        WiFi.softAP(hostname, "123456780");
        WiFi.setHostname(hostname);
        wifiManager.setConfigPortalTimeout(180);
        wifiManager.setConnectTimeout(30);
        wifiManager.setMinimumSignalQuality(30);
        wifiManager.setDebugOutput(true);
        wifiManager.setHostname(hostname);
        wifiManager.setAPCallback([](WiFiManager *mgr)
                                  { Serial.println("looping...");
                                   homeware.loop(); });
        wifiManager.autoConnect(hostname);
        connected = (WiFi.status() == WL_CONNECTED);
    }

    if (!connected)
        ESP.reset();

    homeware.connected = connected;
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
    homeware.config.remove("ssid");
    homeware.config.remove("password");
    homeware.saveConfig();
    ESP.reset();
    delay(1000);
}

String button(const String name, const char *link, const char *style = "")
{
    return stringf("<br/><form action='%s' method='get'><button %s>%s</button></form>", link, (style == "") ? "" : String(stringf("class='%s'", style)), name);
}
String inputH(const String name, const String value)
{
    return String(stringf("<input type=\"hidden\" name=\"%s\" value=\"%s\">", name, value));
}

void setManager(WiFiManager *wf)
{
    String hostname = stringf("%s-local", portal.label);
    wf->setHostname(hostname);
    wf->setTitle("Homeware");
}

const char BUTTON_SCRIPT[] PROGMEM =
    "\r\nfunction buttonClick(buttonId, pinNumber)"
    "{"
    "\r\nconsole.log(buttonId,pinNumber);"
    "\r\nvar xhr = new XMLHttpRequest();"
    "\r\nxhr.onreadystatechange = function()"
    "{"
    "\r\nif (xhr.readyState == 4 &&xhr.status ==200)"
    "{"
    "\r\nvar button = document.getElementById(buttonId);"
    "\r\nbutton.innerText = (xhr.responseText=='1')?'ON':'OFF';"
    "\r\nbutton.value = xhr.responseText;"
    "\r\nconsole.log('response',xhr.responseText);"
    "\r\n}"
    "};"
    "\r\nvar button = document.getElementById(buttonId);"
    "\r\nvar lnk = '/switch?p='+pinNumber; lnk+='&q='; \r\n lnk+=(button.value=='1')?'OFF':'ON';"
    "\r\nconsole.log(lnk);"
    "\r\nxhr.open('GET', lnk , true);"
    "\r\nxhr.send();"
    "\r\n}";

/*
const char HTTP_TIMER_RELOAD[] PROGMEM = "<script>setInterval(function(){"
                                         "{code}"
                                         "}, {t});"
                                         "</ script> ";
String timereload(String url = "/", int timeout = 1000)
{
    String s = FPSTR(HTTP_TIMER_RELOAD);
    s.replace("{t}", String(timeout));
    s.replace("{code}", stringf("window.location.href = '%s';", url));
    return s;
}
*/
void Portal::setupServer()
{
    server->on("/", []()
               {
        WiFiManager wf;
        setManager(&wf);
        String head = "";
        head += FPSTR(HTTP_CHART_HEADER);

        String pg = "";
        JsonObject mode = homeware.getMode();
        String charts = "";
        String scp = "";
        for (JsonPair k : mode)
        {
            String md = k.value().as<String>();
            String p1 = k.key().c_str();
            String v1 = k.value().as<String>();
            if (md == "out" || md == "lc")
            {
                int v = homeware.readPin(p1.toInt(), v1);
                String s = (v == 1) ? "ON" : (v > 0) ? String(v)
                                                     : "OFF";
                String j = "<br/><button id='b{id}' class='D' value='{v}'>" + s + "</button></form>"; 
                j.replace("{id}", p1);
                j.replace("{v}",String(v));
                pg += j;
                j = "\r\nvar b{id} = document.getElementById('b{id}');\r\n";
                j.replace("{id}", p1);
                scp += j;
                j = "\r\n b{id}.addEventListener('click', function() { buttonClick('b{id}', '{id}');});\r\n";
                j.replace("{id}", p1);
                scp += j;
        }

        // chart
        if (md == "adc" || md == "ldr" || md == "pwm" || md == "dht")
        {
            Chart chart = Chart();
            charts += chart.render("p" + p1, "Pin " + p1 + " - " + v1, "valor", "/get?p=" + p1);
        }
        }
        pg += charts;

        pg += button("GPIO", "/gs");
        pg += button("Reiniciar","/reset");
        pg += "<div style='height:100'></div><a href=\"/update\" class='D'>firmware</a>";

        if (scp.length() > 0)
        {
        pg += "<script>\r\n";
        pg += FPSTR(BUTTON_SCRIPT);
            pg += scp;

            pg += "\r\n</script>\r\n";
        }
        wf.setCustomHeadElement(head.c_str());

        portal.server->send(200, "text/html", wf.pageMake("Homeware", pg)); });

    server->on("/switch", []()
               {
                String p = portal.server->arg("p");
                int rsp = homeware.switchPin(p.toInt());
                portal.server->send(200, "text/plain", String(rsp)); });

    server->on("/set", []()
               {
                //if (portal.server->hasArg("p") && portal.server->hasArg("q")){
                String p = portal.server->arg("p");
                String q = portal.server->arg("q");
                int rsp = homeware.writePin(p.toInt(), (q == "ON") ? 1 : 0);
                portal.server->send(200, "text/plain", String(rsp)); });
    server->on("/get", []()
               { 
               String p = portal.server->arg("p");
               int v = homeware.readPin(p.toInt(), String(homeware.getMode()[p]));
               Serial.print(p+": ");
               Serial.println(v);
               portal.server->send(200, "text/plain", String(v)); });
    homeware.server->on("/reset", []()
                        {
                            //String pg = "reiniciando...{c}";
                            //pg.replace("{c}", timereload("/", 1000));
                            WiFiManager wf;
        portal.server->send(200, "text/html", wf.pageMake("Homeware", "<a href='/'>reiniciando...</>"));
    homeware.doCommand("reset"); });

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
            String s = (v==1)?"ON": (v>1)?  String(v):"OFF";

            pg += stringf("<tr><td>%s</td><td>%s</td><td>%s</td></tr>", p1, v1,s);
        }

        pg+="</tbody></table>";
        pg += button("Menu","/");
        portal.server->send(200, "text/html", wf.pageMake("Homeware",pg)); });

#ifdef ALEXA
    server->onNotFound([]()
                       {
	if (!homeware.alexa.handleAlexaApiCall(homeware.server->uri(),homeware.server->arg(0)))
	{
        homeware.server->send(404, "text/plain", "Not found");
    } });
#endif
}

Portal portal;
