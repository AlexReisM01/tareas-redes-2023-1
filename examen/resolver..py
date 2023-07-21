import socket
from dnslib import DNSRecord

if __name__ == "__main__":
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("localhost", 8000))
    while True:
        data, address = skt.recvfrom(2048)
        