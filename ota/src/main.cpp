/*
  ElegantOTA Demo Example - This example will work for both ESP8266 & ESP32 microcontrollers.
  -----
  Author: Ayush Sharma ( https://github.com/ayushsharma82 )

  Important Notice: Star the repository on Github if you like the library! :)
  Repository Link: https://github.com/ayushsharma82/ElegantOTA
*/

#if defined(ESP8266)
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#elif defined(ESP32)
#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#endif


#define WM


#ifdef WM
#include <WiFiManager.h>
#endif
#include <ElegantOTA.h>

const char *ssid = "kcasa";
const char *password = "3938373635";

#if defined(ESP8266)
ESP8266WebServer server(80);
#elif defined(ESP32)
WebServer server(80);
#endif



void setup(void)
{
#ifdef WM
  WiFiManager wifiManager;
#endif
  Serial.begin(115200);
#ifdef WM
  wifiManager.autoConnect("AutoConnectAP");
#else
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
#endif  
  Serial.println("");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/", []()
            { server.send(200, "text/plain", "Hi! I am ESP8266. <a href='/update'>update</a> "); });

  ElegantOTA.begin(&server); // Start ElegantOTA
  server.begin();
  Serial.println("HTTP server started");
}

void loop(void)
{
  server.handleClient();
}