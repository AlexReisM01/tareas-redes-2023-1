import socket
from dnslib import DNSRecord, DNSHeader, DNSQuestion
from dnslib.dns import RR, A

if __name__ == "__main__":
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("localhost", 8000))
    skt.settimeout(5)
    while True:
        try:
            data, address = skt.recvfrom(1024)
            parsed_data = DNSRecord.parse(data)
            print(parsed_data)
        except socket.timeout:
            print("timed out")