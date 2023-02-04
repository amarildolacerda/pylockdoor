STA_IF = "Station"
AP_IF = "Local Area"

import socket
import time
class WLAN:

    def __init__(self, interface_id):
        self.active_for_testing = None
        self.interface_id_for_testing = interface_id
        self.is_connected_for_testing = False
         
    def active(self, is_active):
        self.active_for_testing = is_active

    # noinspection PyUnusedLocal
    def connect(self, ssid=None, password=None, *, bssid=None):
        self.is_connected_for_testing = True

    def isconnected(self):
        return self.is_connected_for_testing

    def scan(self):
        return [['VIVO','x',-80,0,1,2]]    
    def ifconfig(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        sock = s.getsockname()
        s.close()
        return [sock[0],sock[1],0,0]   
    def config(self,essid,password,authmode):
        pass     
