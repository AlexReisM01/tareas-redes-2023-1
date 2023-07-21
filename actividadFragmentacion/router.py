import socket
import sys

def parse_packet(IP_packet: bytes):
    pckt = IP_packet.split(b',', 7)
    parsed_IP_packet = {"ip": pckt[0].decode(), "port": pckt[1].decode(),"TTL": int(pckt[2].decode()),\
                        "ID": pckt[3].decode(), "Offset": int(pckt[4].decode()), "Tamano": int(pckt[5].decode()),\
                            "Flag": int(pckt[6].decode()) ,"msg": pckt[7]}
    return parsed_IP_packet

def create_packet(parsed_IP_packet: dict):
    packet = parsed_IP_packet["ip"].encode() + b',' + parsed_IP_packet["port"].encode() + b',' \
        + str(parsed_IP_packet["TTL"]).encode() + b',' + parsed_IP_packet["ID"].encode() + b','\
              + str(parsed_IP_packet["Offset"]).encode() + b',' + str(parsed_IP_packet["Tamano"]).encode() + b',' \
                + str(parsed_IP_packet["Flag"]).encode() + b',' + parsed_IP_packet["msg"]
    return packet

def get_headers(parsed_IP_packet: dict):
    head = parsed_IP_packet["ip"].encode() + b',' + parsed_IP_packet["port"].encode() + b',' \
        + str(parsed_IP_packet["TTL"]).encode() + b',' + parsed_IP_packet["ID"].encode() + b','\
              + str(parsed_IP_packet["Offset"]).encode() + b',' + str(parsed_IP_packet["Tamano"]).encode() + b',' \
                + str(parsed_IP_packet["Flag"]).encode() + b','
    return head

def fragment_IP_packet(IP_packet, MTU):
    if len(IP_packet)<=MTU:
        return [IP_packet]
    else:
        parsed_packet = parse_packet(IP_packet)
        headers = get_headers(parsed_packet)
        newsize = MTU-(len(headers)+1)
        print(f'\n\n fragmentando paquete de tamano {parsed_packet["Tamano"]} en paquetes de tamano {newsize}\n\n')
        i = 0
        offset = parsed_packet["Offset"]
        fragment_list = []
        while i<parsed_packet["Tamano"]:
            fragment = parsed_packet.copy()
            fragment["Offset"] = offset
            if i+newsize<parsed_packet["Tamano"]:
                fragment["Tamano"] = newsize
                fragment["msg"] = parsed_packet["msg"][i:i+newsize]
                fragment["Flag"] = 1
            else:
                fragment["Tamano"] = parsed_packet["Tamano"]-i
                fragment["msg"] = parsed_packet["msg"][i:]
            fragment_list.append(create_packet(fragment))
            offset+=newsize
            i+=newsize
        return fragment_list
    

def reassemble_IP_packet(fragment_list):
    dict_list = []
    for fragment in fragment_list:
        dict_list.append(parse_packet(fragment))
    dict_list = sorted(dict_list, key=lambda d: d['Offset'])
    message = b""
    if(dict_list[-1]["Flag"] != 0): #si el ultimo valor de flag no es cero, esta incompleto
        return None
    offset = 0
    size = 0
    for fragment in dict_list:
        if fragment["Offset"] != offset: # falta un fragmento entremedio
            return None
        message += fragment["msg"]
        size += fragment["Tamano"]
        offset+=fragment["Tamano"]
    final_dict = dict_list[0].copy()
    final_dict["Tamano"] = size
    final_dict["msg"] = message
    final_dict["Flag"] = 0
    return create_packet(final_dict)        




        

class Router:

    def __init__(self, ip: str, port: str, routes: str) -> None:
        self.ip = ip
        self.port = int(port)
        self.routerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.routerSocket.setblocking(1)
        self.routerSocket.bind((ip, self.port))
        self.routes = routes
        self.round_robin = dict()
        self.received = dict()

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
                MTU = int(line_list[5])
                if ip == line_list[0] and int(line_list[1]) <= int(port) <= int(line_list[2]):
                    if r==0:
                        self.round_robin[(int(line_list[1]), int(line_list[2]))] = line_list[4]
                        return (line_list[3], int(line_list[4]), MTU)
                    else:
                        if (port1, port2) == (int(line_list[1]), int(line_list[2])) and line_list[4] == self.round_robin[port1, port2]:
                            r = 0
            for line in lines:
                line_list = line.split(' ')
                if ip == line_list[0] and int(line_list[1]) <= int(port) <= int(line_list[2]):
                    self.round_robin[(int(line_list[1]), int(line_list[2]))] = line_list[4]
                    return (line_list[3], int(line_list[4]), MTU)
            return (0, 0, 0)
    



    def listen(self):
        while(True):
            full_msg = self.routerSocket.recv(1024)
            parsed_packet = parse_packet(full_msg)
            if(not parsed_packet["TTL"]>0):
                print(f"Se recibió paquete {full_msg} con TTL 0")
                continue
            if parsed_packet["ip"] == self.ip and int(parsed_packet["port"]) == self.port:
                if self.received.get(parsed_packet["ID"]) is not None:
                    self.received[parsed_packet["ID"]].append(full_msg)
                else:
                    self.received[parsed_packet["ID"]] = [full_msg]
                complete = reassemble_IP_packet(self.received[parsed_packet["ID"]])
                if complete is not None:
                    print(parse_packet(complete)["msg"].decode())
                    self.received.pop(parsed_packet["ID"])
            else:
                (next_hop_IP, next_hop_port, MTU) = self.check_routes(parsed_packet["ip"], parsed_packet["port"])
                if next_hop_IP==0 and next_hop_port==0:
                    print(f"No hay rutas hacia {parsed_packet['ip']}:{parsed_packet['port']} para paquete {full_msg}")
                else:
                    parsed_packet["TTL"]+=-1
                    fragment_list = fragment_IP_packet(create_packet(parsed_packet), MTU)
                    print(f"\nredirigiendo paquete {full_msg} con destino final {parsed_packet['ip']}:{parsed_packet['port']} desde {self.ip}:{self.port} hacia {next_hop_IP}:{next_hop_port}\n")
                    for fragment in fragment_list:
                        self.routerSocket.sendto(fragment, (next_hop_IP, next_hop_port))
                    
                    
            


if __name__ == "__main__":
    router = Router(sys.argv[1], sys.argv[2], sys.argv[3])
    router.listen()