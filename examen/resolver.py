import socket
from dnslib import DNSRecord

if __name__ == "__main__":
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("localhost", 8000))
    skt.settimeout(5)
    while True:
        try:
            data, address = skt.recvfrom(2048)
            print(data)
        except:
            print("timed out")