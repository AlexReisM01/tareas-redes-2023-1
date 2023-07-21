import socket
import sys

def parse_packet(IP_packet: bytes):
    pckt = IP_packet.split(b',', 2)
    parsed_IP_packet = {"ip": pckt[0].decode(), "port": pckt[1].decode(), "msg": pckt[2]}
    return parsed_IP_packet

def create_packet(parsed_IP_packet: dict):
    packet = parsed_IP_packet["ip"].encode() + b',' + parsed_IP_packet["port"].encode() + b',' + parsed_IP_packet["msg"]
    return packet

class Router:

    def __init__(self, ip: str, port: str, routes: str) -> None:
        self.ip = ip
        self.port = int(port)
        self.routerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.routerSocket.setblocking(1)
        self.routerSocket.bind((ip, self.port))
        self.routes = routes
        self.round_robin = dict()

    def check_routes(self, ip: str, port: str):
        r = 0
        (port1, port2) = (0,0)
        for (p1, p2) in self.round_robin.keys():
            if p1 <= int(port) <= p2:
                r = 1
                (port1, port2) = (p1,p2)
        with open(self.routes) as f:
            lines = f.readlines()
            for line in lines:
                line_list = line.split(' ')
                if ip == line_list[0] and int(line_list[1]) <= int(port) <= int(line_list[2]):
                    if r==0:
                        self.round_robin[(int(line_list[1]), int(line_list[2]))] = line_list[4]
                        return (line_list[3], int(line_list[4]))
                    else:
                        if (port1, port2) == (int(line_list[1]), int(line_list[2])) and line_list[4] == self.round_robin[port1, port2]:
                            r = 0
            for line in lines:
                line_list = line.split(' ')
                if ip == line_list[0] and int(line_list[1]) <= int(port) <= int(line_list[2]):
                    self.round_robin[(int(line_list[1]), int(line_list[2]))] = line_list[4]
                    return (line_list[3], int(line_list[4]))
            return (0, 0)
    


    def listen(self):
        while(True):
            full_msg = self.routerSocket.recv(1024)
            parsed_packet = parse_packet(full_msg)
            print(parsed_packet)
            if parsed_packet["ip"] == self.ip and int(parsed_packet["port"]) == self.port:
                print(parsed_packet["msg"].decode())
            else:
                (next_hop_IP, next_hop_port) = self.check_routes(parsed_packet["ip"], parsed_packet["port"])
                if next_hop_IP==0 and next_hop_port==0:
                    print(f"No hay rutas hacia {parsed_packet['ip']}:{parsed_packet['port']} para paquete {full_msg}")
                else:
                    print(f"redirigiendo paquete {full_msg} con destino final {parsed_packet['ip']}:{parsed_packet['port']} desde {self.ip}:{self.port} hacia {next_hop_IP}:{next_hop_port}")
                    self.routerSocket.sendto(full_msg, (next_hop_IP, next_hop_port))
                    
                    
            


if __name__ == "__main__":
    router = Router(sys.argv[1], sys.argv[2], sys.argv[3])
    router.listen()