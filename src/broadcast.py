from gc import collect

from config import IFCONFIG, dados, gKey, gpin, gtrigg, strigg, uid
import utime
import ure
from setup import setupXML, eventServiceXML, soapState, deviceType, urnDeviceType
from wifimgr import ifconfig


def now():
    from utime import localtime

    t = localtime()
    return "{}-{}-{}T{}:{}:{}".format(t[0], t[1], t[2], t[3], t[4], t[5])

localIP= ''
class Alexa:
    def __init__(self, ip):
        self.ip = ip
        global localIP 
        localIP = ip
    def sendto(self, dest, msg):
        try:
            from socket import AF_INET, SOCK_DGRAM, socket

            tmp = socket(AF_INET, SOCK_DGRAM)
            tmp.sendto(msg, dest)
            utime.sleep(0.1)
            tmp.close()
        except Exception as e:
            print(str(e))

    def send_msearch(self, addr):
        from setup import setupXML

        print("M-SEARCH->", addr)
        self.sendto(addr, rf("msearch.html").format(ip=self.ip))

    def send_notify(self, sock):
        print("NOTIFY")
        sock.send(rf("msearch_notify.html").format(ip=self.ip))
        utime.sleep(0.1)


def rf(n):
    with open(n, "r") as f:
        return f.read()


def discovery(sdr, addr, dt):
    if dt.startswith(b"M-SEARCH"):
        alexa = Alexa(ifconfig()[0])
        alexa.send_msearch(addr)
    else:
        print(dt)
    return True


def getState(pin=None):
    return gtrigg(pin or gKey("auto-pin"))
def getLdrState(pin=None):
    return gpin(pin or gKey("auto-pin"))

def action_state(v: int, pin=None):
    return strigg(pin or gKey("auto-pin"), v)


def mkhdr(client, status_code, contentType, length):
    w = client.write
    w("HTTP/1.1 {} OK\r\n".format(status_code))
    w("CONTENT-LENGTH: {}\r\n".format(length))
    w("CONTENT-TYPE: {}\r\n".format(contentType))  # charset="utf-8"
    w("CONNECTION: close\r\n")
    w("CACHE-CONTROL: no-cache\r\n\r\n")


def mkrsp(cli, payload, status_code=200, contentType="text/html"):
    print(status_code,payload)
    z = len(payload)
    try:
        mkhdr(cli, status_code, contentType, z)
        cli.write(payload)
        return True
    except Exception as e:
        print(str(e))
        return False
    return True


def notfnd(cli, url):
    mkrsp(cli, "{}".format(url), 404)
    return True


def label():
    return gKey("label") or gKey("mqtt_name")


def handle_req(cli,url, dt):
    print(dt)
    if dt.find(b"/cmd?q=") > 0:
        q = dt.decode("utf-8").split("=")[1].split(" HTTP")[0]
        while "%20" in q:
            q = q.replace("%20", " ")
        if q:
            from command8266 import cmmd

            mkrsp(cli, "{}".format(cmmd(q)))
            return True
        return False
    if dt.find(b"/upnp/control/basicevent1") > 0 and dt.find(b"#GetBinaryState") != -1:
        return mkrsp(cli, rf(soapState.format(deviceType)).format(state=getState()))
    elif dt.find(b"/upnp/control/basicevent1") > 0 and dt.find(b"GetLightLevel") != -1:
        return mkrsp(cli, rf(soapState.format(deviceType)).format(state=getLdrState()))

    elif dt.find(b"/eventservice") > 0:
        return mkrsp(
            cli, rf(eventServiceXML.format(deviceType)), 200, "application/xml"
        )
    elif dt.find(b"/description.xml") > 0:
        global localIP
        return mkrsp(
            cli,
            rf("setup_base.xml").format(ip=localIP, urn=urnDeviceType, name=label(), uuid=uid),
            200,
            "application/xml",
        )
    elif dt.find(b"#SetBinaryState") != -1:
        succ = False
        if dt.find(b"<BinaryState>1</BinaryState>") != -1:
            succ = action_state(1)
        elif dt.find(b"<BinaryState>0</BinaryState>") != -1:
            succ = action_state(0)
        else:
            print("Unknown")
        if succ:
            mkrsp(cli, rf(soapState.format(deviceType)).format(state=getState()))
        return succ
    else:
        print("a impl", dt)
        return False


def http(cli, addr, req):
    try:
        url = ""
        try:
            cli.setblocking(False)
            url = (
                ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", req)
                .group(1)
                .decode("utf-8")
                .rstrip("/")
            )
            print("url:", url)

            if not handle_req(cli,url, req):
                ext = url.split(".")
                if len(ext) > 1:
                    mkrsp(
                        cli,
                        (rf(url) or "").format(
                            name=label() or "indef", uuid=uid, url=url
                        ),
                        200,
                        "text/{}".format(ext[1]),
                    )
                else:
                    notfnd(cli, url)

        except Exception as e:
            print(str(e), " in ", req)
            mkrsp(cli, rf("erro.html").format(msg=str(e), url=url), 500)
        return True
    except Exception as e:
        print(str(e))
        return True
