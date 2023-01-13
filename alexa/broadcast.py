
import config as g


class Alexa:
    def __init__(self,ip):
        self.ip = ip
    def readFile(self,nome:str):  
        with open(nome, 'r') as f:return f.read()
    def sendto(self, destination, message):
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.sendto(message, destination)
        idle()
        time.sleep(0.1)
    def send_msearch(self,  addr):
        self.sendto(addr, self.readFile("msearch.html").format(self.ip))



def discovery(sender,addr, message):
        if message.startswith(b'M-SEARCH'):
           alexa = Alexa(g.ifconfig[0])
           alexa.send_msearch(addr)
        else:   
           print('broadcast',ip, addr,message)
        pass
    
