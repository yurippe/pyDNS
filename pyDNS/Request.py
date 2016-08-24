import socket
from util import *
#http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
request_types = {1 : "A", 2: "NS", 5: "CNAME", 6: "SOA", 11: "WKS", 12: "PTR", 15: "MX", 33: "SRV",
                 28: "AAAA", 255: "*"}

#Parsing information:
#http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm


class Packet(object):

    def __init__(self, udp_data):
        self.raw_headers = udp_data[:12]
        self.raw_data = udp_data[12:]

        self.header_bytes = string2bytearray(self.raw_headers)
        self.data_bytes = string2bytearray(self.raw_data)

        self.headers = parseDNSHeader(self.header_bytes)
        self.data = parseDNSData(self.data_bytes, self.headers)

    def answer(self, address, sock):
        """Sets the type to answer, and sends it"""
        self.headers["QR"] = 1
        header = headerdict2bytes(self.headers)
        body = datadict2bytes(self.data)
        sock.sendto(header + body, address)

    def askOther(self, address, port=53):
        self.headers["QR"] = 0
        header = headerdict2bytes(self.headers)
        body = datadict2bytes(self.data)
        middlesock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytessent = middlesock.sendto(header + body, (address, port))
        reply, from_server = middlesock.recvfrom(4096)
        return Packet(reply)