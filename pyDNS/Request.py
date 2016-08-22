from struct import unpack_from

#http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
request_types = {1 : "A", 2: "NS", 5: "CNAME", 6: "SOA", 11: "WKS", 12: "PTR", 15: "MX", 33: "SRV",
                 28: "AAAA", 255: "*"}

#Parsing information:
#http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm

class Request(object):

    def __init__(self, udp_data):
        self.raw_data = udp_data

        self.raw_header = udp_data[:12] #First 12 bytes are header bytes
        self.raw_body = udp_data[12:]   #Skip first 12 bytes, as they are the header we just unpacked

        #unpack data
        unpacked_data = unpack_from("bbbbbbbbbbbb", self.raw_header, 0)

        #Parse id, 2 bytes
        self.id = (unpacked_data[0] << 8) + unpacked_data[1]

        #Parse next byte:
        b = unpacked_data[2]
        self.qr = b >> 7                        #first bit, 0 for query; 1 for response
        #0111 1000 binary = 120 decimal
        self.opcode = (b & 120) >> 3            #2-5th bits, opcode; 0 for standard query
        #0000 0100 binary = 4 decimal
        self.aa = (b & 4) >> 2                  #6th bit, Authorative answer flag, 1 if authorative; 0 if not
        #0000 0010 binary = 2 decimal
        self.tc = (b & 2) >> 1                  #7th bit, Truncation flag
        #0000 0010 binary = 1 decimal
        self.rd = b & 1                         #8th bit, Recursion Desired

        #Next byte
        b = unpacked_data[3]
        self.ra = b >> 7                        #first bit, Recursion Available, 1 for available
        #0111 0000 binary = 112 decimal
        self.z = (b & 112) >> 4                 #next 3 bits, should all be zero TODO: check this
        #0000 1111 binary = 15 decimal
        self.rcode = (b & 15)                   #last 4 bits, response code, should be zero in queries and 0 in a successful response

        self.qdcount = (unpacked_data[4] << 8) + unpacked_data[5]
        self.ancount = (unpacked_data[6] << 8) + unpacked_data[7]
        self.nscount = (unpacked_data[8] << 8) + unpacked_data[9]
        self.arcount = (unpacked_data[10] << 8) + unpacked_data[11]

        #Parse Question section
        #We assume that self.qdcount holds the correct number of questions
        self.questions = []

        bp = 0 #Body pointer
        for question in xrange(self.qdcount):
            qname = []

            subdomain_length = unpack_from("b", self.raw_body, bp)[0]
            while subdomain_length != 0:
                sub_qname = []
                for sub in xrange(subdomain_length):
                    bp += 1
                    sub_qname.append(chr(unpack_from("b", self.raw_body, bp)[0]))
                qname.append(sub_qname)
                bp += 1
                subdomain_length = unpack_from("b", self.raw_body, bp)[0]

            bp += 1
            tail = unpack_from("bbbb", self.raw_body, bp)
            qtype = (tail[0] << 8) + tail[1]
            qclass = (tail[2] << 8) + tail[3]
            bp += 4
            dottedqname = ".".join(["".join(sname) for sname in qname])
            self.questions.append({"QName": qname, "QType": qtype, "QClass": qclass, "DottedQName": dottedqname})

        self.raw_questions = self.raw_body[:bp]