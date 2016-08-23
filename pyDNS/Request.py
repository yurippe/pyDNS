from struct import unpack_from
from util import *
#http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
request_types = {1 : "A", 2: "NS", 5: "CNAME", 6: "SOA", 11: "WKS", 12: "PTR", 15: "MX", 33: "SRV",
                 28: "AAAA", 255: "*"}

#Parsing information:
#http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm

class Request(object):

    def __init__(self, udp_data):
        self.raw_headers = udp_data[:12]
        self.raw_data = udp_data[12:]

        self.header_bytes = string2bytearray(self.raw_headers)
        self.data_bytes = string2bytearray(self.raw_data)

        self.headers = parseDNSHeader(self.header_bytes)
