from machine import Pin
from machine import ADC
import dht
import mqtt
try:
    import esp
    defineEsp32 = true
except:
    defineEsp32 = false


#def readDht22(pin:int) -> str:
#    dht22 = DHT22(Pin(pin))
#    dht22.measure()
#    return '{ "temp": {}, "hum": {} }'.format(dht22.temperature(), dht22.humidity())

#def readLdr(pin:int) -> str:
#    lumPerct = (ADCRead(pin)-40)*(10/86) 
#    return '{ "lum": {} }'.format( round(lumPerct) )

#def ADCRead(pin:int):
#    if defineEsp32:
#       return ADC(Pin(pin)).read() #Esp32
#    else:
#       return ADC(pin).read()   #8266

                  #      if (md == 3):
                  #          o(i, ADCRead(i),md)
                  #          continue
                  #      if md==g.sMde(i,'ldr'):
                  #          utls.p(i,utls.readLdr(i))
                  #          continue
                  #      if md==g.sMde(i,'dht22'):
                  #          utls.p(i,utls.readDht22(i))
                  #          continue
