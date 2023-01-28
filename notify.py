notify ="""NOTIFY / HTTP/1.1\r
HOST: http://{host}:8080\r
CONTENT-TYPE: text/xml; charset="utf-8"\r
CONTENT-LENGTH: {lenght}\r
NT: upnp:event\r
NTS: upnp:propchange\r
SID:{uuid}\r
SEQ: 0\r\n\r\n"""

soap ="""<e:propertyset xmlns:e="urn:schemas-upnp-org:event-1-0">
  <e:property>
    <BinaryState>{state}</BinaryState>
  </e:property>
</e:propertyset>\r\n"""

search = """HTTP/1.1 200 OK\r
LOCATION: http://{host}:8080/setup.xml\r
CACHE-CONTROL: max-age=120"""


ip = '192.168.15.2'

print('iniciando socket')
import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.settimeout(30)

uuid = '79076600'

msg = soap.format(state=1)
x = len(msg)
cmd = (notify.format(host=ip,lenght=x,uuid=uuid)+msg).encode('utf-8')
print(cmd)
s.sendto(cmd, (b'239.255.255.250', 1900) )




# esperar respostas

# Set up the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 1900))

# Join the UPnP multicast group
group = socket.inet_aton("239.255.255.250")
mreq = struct.pack("4sL", group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

while True:
    data, address = sock.recvfrom(1024)
    print(data)