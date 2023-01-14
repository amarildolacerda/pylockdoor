from machine import unique_id
from ubinascii import hexlify

uid = '{}'.format(hexlify(unique_id()).decode('utf-8'))
config = {
    'label':'Luz escritório',
    'ifconfig': None,
    'ssid' : 'VIVOFIBRA-A360',
    'password' : '6C9FCEC12A', 
    'ap_ssid': 'machup',
    'ap_password': '123456780',
    'mqtt_prefix': 'mesh',
    'mqtt_name':'escritorio'    
}