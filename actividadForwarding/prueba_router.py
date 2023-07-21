import sys
import socket

if __name__ == "__main__":
    sckt = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sckt.bind(("127.0.0.1", 8890))
    with open("message.txt") as f:
        lines = f.readlines()
        for line in lines:
            msg = sys.argv[1] + ',' + line
            sckt.sendto(msg.encode(), (sys.argv[2], int(sys.argv[3])))
