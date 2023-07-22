import socket
import sys
import random



        

class Router:

    def __init__(self, ip: str, port: str) -> None:
        self.ip = ip
        self.port = int(port)
        self.routerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.routerSocket.setblocking(1)
        self.routerSocket.bind((ip, self.port))
        self.received = dict()
        self.natpublic = dict()
        self.natprivate = dict()



    def listen(self):
        while(True):
            full_msg, (ip, private) = self.routerSocket.recvfrom(4096)
            if (ip, private) not in self.natprivate.keys(): # saves client if it doesnt exist
                public_port = random.randint(8000, 15000)   # generates public port
                publicskt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                while True:
                    try:
                        publicskt.bind(("localhost", public_port))
                        break
                    except OSError:
                        "port used, trying another"
                        public_port = random.randint(8000, 10000) # if port used, generates another
                self.natpublic[public_port] = (ip, private)
                self.natprivate[(ip, private)] = [public_port, publicskt]
            else:
                publicskt = self.natprivate[(ip, private)][1] #looks up client if it exists
            print("sending data")
            publicskt.sendto(full_msg, ("localhost", 8000)) # sends dns message to server
            response, _ = publicskt.recvfrom(4096)
            responselist = response.split(b",", 2)
            destination_port = responselist[1]
            response_msg = responselist[2]
            destination = self.natpublic[int(destination_port.decode())] #looks up the private direction of the destination
            self.routerSocket.sendto(response_msg, destination)

            

                    
                    
            


if __name__ == "__main__":
    router = Router("localhost", 8888)
    router.listen()