
import time

def ticks_diff(a,b):
    return a - b
    
def ticks_ms():
    return time.time() * 1000
    
def localtime():
    return time.localtime() 
def sleep(ms):
    time.sleep(ms/1000.0)   
