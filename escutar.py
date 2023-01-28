from src import server


class Client(server.Broadcast):
    def send(msg):
        self.sock.sendto(msg,("239.255.255.250",1900))        

def recebe(server,add,msg):
    print(msg)
    return false

cli = Client("")
cli.listen(recebe)           