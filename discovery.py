import socket
import time

msg = \
    'M-SEARCH * HTTP/1.1\r\n' \
    'HOST:239.255.255.250:1900\r\n' \
    'ST:urn:Belkin:device:**\r\n' \
    'MX:2\r\n' \
    'MAN:"ssdp:discover"\r\n' \
    '\r\n'

# Set up UDP socket
print('iniciando socket')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

s.settimeout(5)
#s.sendto(b'M-SEARCH * HTTP/1.1', ('0.0.0.0', 1900) )
s.sendto(b'M-SEARCH * HTTP/1.1', (b'239.255.255.250', 1900) )
#s.sendto(b'M-SEARCH * HTTP/1.1', (b'192.168.15.255', 1900) )
#s.sendto(b'M-SEARCH * HTTP/1.1', (b'192.168.15.2', 1900) )
#s.sendto(b'M-SEARCH * HTTP/1.1', (b'255.255.255.255', 1900) )
#s.sendto(b'M-SEARCH * HTTP/1.1', (b'192.168.15.0', 1900) )

print('enviou M-SEARCH, aguardando resposta')
try:
    while True:
        data, addr = s.recvfrom(65507)
        print(addr, data)
        
except socket.timeout:
    pass