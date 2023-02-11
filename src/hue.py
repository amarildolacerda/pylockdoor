resp = """HTTP/1.1 200 OK\r\n
HOST: 239.255.255.250:1900\r\n
CACHE-CONTROL: max-age=100\r\nEXT:\r\n
LOCATION: http://{ip}:8080/description.xml\r\n
SERVER: Linux/3.14.0 UPnP/1.0 IpBridge/1.24.0\r\n
hue-bridgeid: {uuid}\r\n
ST: upnp:rootdevice\r\n
USN: uuid:f6543a06-da50-11ba-8d8f-{uuid}::upnp:rootdevice\r\n\r\n"""

setup= """<root xmlns="urn:schemas-upnp-org:device-1-0">
<specVersion>
<major>1</major>
<minor>0</minor>
</specVersion>
<URLBase>http://{ip}:8080/</URLBase>
<device>
<deviceType>urn:schemas-upnp-org:device:Basic:1</deviceType>
<friendlyName>Amazon-Echo-HA-Bridge ({ip})</friendlyName>
<manufacturer>Royal Philips Electronics</manufacturer>
<manufacturerURL>http://www.philips.com</manufacturerURL>
<modelDescription>Philips hue Personal Wireless Lighting</modelDescription>
<modelName>Philips hue bridge 2012</modelName>
<modelNumber>929000226503</modelNumber>
<serialNumber>{uuid}</serialNumber>
<UDN>uuid:f6543a06-da50-11ba-8d8f-{uuid}</UDN>
</device>
</root>"""