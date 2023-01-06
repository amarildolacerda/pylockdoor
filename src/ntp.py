
import utime
from machine import RTC

try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct
NTP_DELTA = 3155673600
host = "time.google.com"
def gettime():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1b
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    #res = 
    s.sendto(NTP_QUERY, addr)
    msg = s.recv(48)
    s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA
def getRTCNow():
   return RTC().datetime()
def settime():
     t = gettime()
     tm = utime.localtime(t)
     tm = tm[0:3] + (0,) + tm[3:6] + (0,)
     rtc = RTC()
     rtc.datetime(tm)