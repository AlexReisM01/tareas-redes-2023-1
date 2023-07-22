import socket
import sys
from dnslib import DNSRecord

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(10)
    while True:
        name = input("insert query:")
        record = DNSRecord.question(name)
        query = bytes(record.pack())
        client_socket.sendto(query, ("localhost", 8888)) #sending message to router
        try:
            response = client_socket.recv(4096)
            if response == b"no response":
                print("no response")
            elif len(response)>0:
                print(DNSRecord.parse(response))
        except TimeoutError:
            print("timed out")
