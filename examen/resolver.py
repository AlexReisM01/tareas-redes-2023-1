import socket
from dnslib import DNSRecord, DNSHeader, DNSQuestion
from dnslib.dns import RR, A, CLASS, QTYPE

ROOT_ADDRESS = ("192.33.4.12", 53)

class Record:
    def __init__(self, Qname, ANCOUNT, NSCOUNT, ARCOUNT):
        self.qname = Qname
        self.anc = ANCOUNT
        self.nsc = NSCOUNT
        self.arc = ARCOUNT
        self.ans = []
        self.auth = []
        self.add = []

    def set_ans(self, ans):
        self.ans = ans

    def set_auth(self, auth):
        self.auth = auth

    def set_add(self, add):
        self.add = add

    def find_ans(self):
        for ans in self.ans:
            rtype = QTYPE.get(ans.rtype)
            if(rtype == "A"):
                return ans.rdata, rtype
        return 0, ""
    
    def find_add(self):
        for add in self.add:
            rtype = QTYPE.get(add.rtype)
            if(rtype == "A"):
                return add.rdata, rtype
        return 0, ""
    
    def find_auth(self):
        for auth in self.add:
            rtype = QTYPE.get(auth.rtype)
            if(rtype == "NS"):
                return auth.rdata, rtype
        return 0, ""

             
    

    

def resolver(query, address = ROOT_ADDRESS):
    sendskt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"sending query to {address}")
    sendskt.sendto(query, address)
    data, _ = sendskt.recvfrom(4096)
    parsed_data = DNSRecord.parse(data)
    ans_num, auth_num, ar_num = parsed_data.header.a, parsed_data.header.auth, parsed_data.header.ar
    record = Record(parsed_data.get_q().get_qname(), ans_num, auth_num, ar_num)
    if(ans_num>0):
        record.set_ans(parsed_data.rr)
    if(auth_num>0):
        record.set_auth(parsed_data.auth)
    if(ar_num>0):
        record.set_add(parsed_data.ar)
    answer, rtype = record.find_ans()
    if rtype == "A":
        return data
    authanswer, authtype = record.find_auth()
    if authtype == "NS":
        addanswer, addtype = record.find_add()
        if addtype == "A":
            sendskt.sendto(query, (addanswer))
            adddata, _ = sendskt.recvfrom(4096)
            return adddata
        return resolver(query, (authanswer, 53))
    print "NO ANSWER"
    return None #ignore other type of answers
    

if __name__ == "__main__":
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("localhost", 8000))
    skt.settimeout(20)
    while True:
        try:
            query, address = skt.recvfrom(4096)
            print(f"RECEIVING QUERY FROM {address}")
            ans = resolver(query)
            if ans != None:
                skt.sendto(ans, address)
            else
        except socket.timeout:
            print("timed out")