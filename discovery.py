import socket
import time
import urllib.request



def download(url):
   try: 
        response = urllib.request.urlopen(url)
        data = response.read()
        return data.decode()
   except:
        pass




msg = \
    'M-SEARCH * HTTP/1.1\r\n' \
    'HOST:239.255.255.250:1900\r\n' \
    'ST: upnp:rootdevice\r\n'\
    'MX:2\r\n' \
    'MAN:"ssdp:discover"\r\n' \
    '\r\n'

    #'ST:urn:Belkin:device:**\r\n' \


# Set up UDP socket
print('iniciando socket')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

s.settimeout(5)
#s.sendto(b'M-SEARCH * HTTP/1.1', ('0.0.0.0', 1900) )
s.sendto(msg.encode('utf-8'), (b'239.255.255.250', 1900) )
#s.sendto(b'M-SEARCH * HTTP/1.1', (b'192.168.15.255', 1900) )
#s.sendto(b'M-SEARCH * HTTP/1.1', (b'192.168.15.2', 1900) )
#s.sendto(b'M-SEARCH * HTTP/1.1', (b'255.255.255.255', 1900) )
#s.sendto(b'M-SEARCH * HTTP/1.1', (b'192.168.15.0', 1900) )

print('enviou M-SEARCH, aguardando resposta')
try:
    while True:
        data, addr = s.recvfrom(65507)
        
        
        location = None
        na8080 = None
        tipo = None
        headers = data.split(b'\n')
        for header in headers:
         if header.startswith(b'LOCATION:'):
            location = header.split(b':', 1)[1].strip()
            tipo = "hue"
         if header.find(b":8080")!=-1:
            na8080 = location
            tipo = "mesh"
        index = data.find(b'hue')
        if index!=-1 or na8080:
            print(tipo, location)
            response = download(str(location))
            print(response)
        if (na8080)   : 
            print(location, data )
        
except socket.timeout:
    pass

