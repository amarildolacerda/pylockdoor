from machine import unique_id
from ubinascii import hexlify

CFG_LABEL:int = 0
CFG_SSID : int = 1
CFG_PASS: int = 2
CFG_APSSID : int = 3
CFG_APPASS : int = 4

CFG_MQTTPREFIX: int = 51
CFG_MQTTNAME:int = 52

uid = '{}'.format(hexlify(unique_id()).decode('utf-8'))
ifconfig = None
config = {
    CFG_LABEL:'Luz escritório',
    CFG_SSID : 'VIVOFIBRA-A360',
    CFG_PASS : '6C9FCEC12A', 
    CFG_APSSID: 'machup',
    CFG_APPASS: '123456780',
    CFG_MQTTPREFIX: 'mesh',
    CFG_MQTTNAME:'escritorio'    
}