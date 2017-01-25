import socket
from BitManipulator import read_bits, bytes2int, int2bytes, Byte
#http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
request_types = {1 : "A", 2: "NS", 5: "CNAME", 6: "SOA", 11: "WKS", 12: "PTR", 15: "MX", 16: "TXT", 33: "SRV",
                 28: "AAAA", 255: "*"}

#Parsing information:
#http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm

class Index(object):

    def __init__(self, i=0):
        self.i = i

    def inc(self, incr=1):
        self.i += incr

def _dotted2string(dottedarray):
    """
    >>> _dotted2string(_string2dotted("www.test.com"))
    'www.test.com'
    """
    return ".".join(["".join(subarr) for subarr in dottedarray])

def _string2dotted(string):
    return string.split(".")

def _parse_label(data, index):
    length = read_bits(data[index.i], 2, 6)
    name = []
    for l in range(length):
        index.inc()
        name.append(chr(data[index.i]))
    return name

def _parse_pointer(data, index):
    offset = bytes2int(data[index.i: index.i + 2]) & 0x3FFF #16383 (DEC) We & with 00111111 11111111 to get rid of the first 2 bits
    return _parse_label_or_pointer(data, Index(offset-12))  #Offset - header length (12)
        
def _parse_label_or_pointer(data, index):
    val = []
    length = data[index.i]
    while length > 0:
        read_type = read_bits(length, 0, 2)
        if read_type == 0: #Label
            val.append(_parse_label(data, index))
            index.inc()
        elif read_type == 3: #Pointer
            val = _parse_pointer(data, index) #Because pointers terminate this should be ok, but have in mind this area
            index.inc(2) #pointers are 2 bytes long
        length = data[index.i]
    return val

class RData(object):

    @staticmethod
    def parse_from_data(data, index):
        return RData()

    def __init__(self):
        pass

class Question(object):

    @staticmethod
    def parse_from_data(data, index):
        QNAME = _parse_label_or_pointer(data, index)
        index.inc()
        QTYPE = bytes2int(data[index.i:index.i+2])
        index.inc(2)
        QCLASS = bytes2int(data[index.i:index.i+2])
        index.inc(2)

        return Question(QNAME, QTYPE, QCLASS)
        

    def __init__(self, qname, qtype, qclass):
        """
        Arguments:
            qname  (str | list) - The name being queried, either in list-dotted-form or (the easiest) a string, and we will convert it
            qtype  (int)        - The query type (1=A, 2=NS, 5=CNAME, 6=SOA, 15=MX, ect)
            qclass (int)        - Class of resource records being requested. Most common value is 1 for IN or Internet
        """
        if type(qname) == str:
            qname = _string2dotted(qname)
        self.qname  = qname
        self.qtype  = qtype
        self.qclass = qclass

    def toBinary(self):
        data = []
        #convert qname
        for part in self.qname:
            data += int2bytes(len(part), 1) #Single octet describing length, ##TODO check no overflow
            #add binary data for each
            data += [ord(l) for l in part]
        ##Add final 0 byte
        data.append(0)
        #convert qtype
        data += int2bytes(self.qtype, 2)
        #convert qclass
        data += int2bytes(self.qclass, 2)
        return str(bytearray(data))

    def __str__(self):
        return "QNAME: %s\nQTYPE: %d\nQCLASS: %d" % (str(self.qname), self.qtype, self.qclass)

class Resource(object):

    @staticmethod
    def parse_from_data(data, index):
        NAME = _parse_label_or_pointer(data, index)
        index.inc() #TODO This doesn't work as intended,
        #seems to be a problem with parsing pointers, since I got a response with a pointer in it
        #comment out the line and it works for pointers, but that is too inconsistent with
        #how Question handles it's parsing
        TYPE = bytes2int(data[index.i:index.i+2])
        index.inc(2)
        CLASS = bytes2int(data[index.i:index.i+2])
        index.inc(2)
        TTL  = bytes2int(data[index.i:index.i+4])
        index.inc(4)
        RDLENGTH = bytes2int(data[index.i:index.i+2])
        index.inc(2)
        RDATA = RData.parse_from_data(data, index)
        index.inc(RDLENGTH)
        return Resource(NAME, TYPE, CLASS, TTL, RDATA)

    def __init__(self, name, tpe, cls, ttl, rdata):
        self.name = name
        self.type = tpe
        self.cls = cls
        self.ttl = ttl
        self.rdata = rdata

    def toBinary(self):
        pass

    def __str__(self):
        return "NAME: %s\nTYPE: %d\nCLASS: %d\nTTL: %d\nRDATA: <>" % (str(self.name), self.type, self.cls, self.ttl)

class Packet(object):

    @staticmethod
    def from_binary(bin_data):
        raw_headers = bin_data[:12]
        raw_body = bin_data[12:]

        header = bytearray(raw_headers)
        body = bytearray(raw_body)

        #1st and 2nd Byte
        ID      = bytes2int(header[0:2])
        #3rd Byte
        QR      = read_bits(header[2], 0, 1)
        OPCODE  = read_bits(header[2], 1, 4)
        AA      = read_bits(header[2], 5, 1)
        TC      = read_bits(header[2], 6, 1)
        RD      = read_bits(header[2], 7, 1)
        #4th Byte
        RA      = read_bits(header[3], 0, 1)
        Z       = read_bits(header[3], 1, 3)
        RCODE   = read_bits(header[3], 4, 4)
        #5th and 6th Bytes
        QDCOUNT = bytes2int(header[4:6])
        #7th and 8th Bytes
        ANCOUNT = bytes2int(header[6:8])
        #9th and 10th Bytes
        NSCOUNT = bytes2int(header[8:10])
        #11th and 12th Bytes
        ARCOUNT = bytes2int(header[10:12])

        i = Index(0) #global index for body data
        questions   = []
        answers     = []
        nameservers = []
        additionals = []

        for q in range(QDCOUNT):
            questions.append(Question.parse_from_data(body, i))
        for r in range(ANCOUNT):
            answers.append(Resource.parse_from_data(body, i))
        for n in range(NSCOUNT):
            nameservers.append(Resource.parse_from_data(body, i))
        for a in range(ARCOUNT):
            additionals.append(Resource.parse_from_data(body, i))
            
        return Packet(ID, QR, OPCODE, AA, TC, RD, RA, Z, RCODE,
                      questions, answers, nameservers, additionals)
 
        

    def __init__(self, uid, qr, opcode, aa, tc, rd, ra, z=0, rcode=0, questions=[], answers=[], nameservers=[], additionals=[]):
        """
        Arguments:
            uid    (int)  - 16 bit message ID supploed by the questioner and reflected back unchanged by the responder. Identifies the transaction
            qr     (bool) - Query-Response bit, set to 0 (False) by the questioner and to 1 (True) in the response
            opcode (int)  - Identifies the request/operation type. Currently assigned values are:
                                0: QUERY. standard query
                                1: IQUERY. Inverse query, Optional support by DNS
                                2: STATUS. DNS status request
            aa     (bool) - Authoritative Answer. Valid in responses only. Because of aliases multiple owners may exists so the AA bit corresponds to the name which matches the query name, OR the first owner name in the answer section.
            tc     (bool) - TrunCation. specifies that this message was truncated due to length greater than that permitted on the transmission channel. Set on all truncated messages except the last one.
            rd     (bool) - Recursion Desired. this bit may be set in a query and is copied into the response if recursion supported by this Name Server. If Recursion is rejected by this Name Server, for example it has been configured as Authoritative Only, the response (answer) does not have this bit set. Recursive query support is optional.
            ra     (bool) - Recursion Available. this bit is valid in a response (answer) and denotes whether recursive query support is available (1) or not (0) in the name server.
            z      (int)  - 3 bits not used for anything at all (Reserved bits) Should always be 0
            rcode  (int)  - Identifies the response type to the query. Ignored on a request(question). Currently assigned values:
                                0: No error condition
                                1: Format error - The nameserver was unable to interpret the query
                                2: Server failure - The nameserver was unable to process this query due to a problem with the name server.
                                3: Name Error - Meaningful only for responses from an authoritative name server, this code signifies that the domain name referenced in the query does not exist.
                                4: Not Implemented - The name server does not support the requested kind of query.
                                5: Refused - The name server refuses to perform the specified operation for policy reasons. For example, a name server may not wish to provide the information to the particular requester, or a name server may not wish to perform a particular operation (e.g., zone transfer) for particular data.
            questions    (list) - A list of Question
            answers      (list) - A list of Answer
            nameservers  (list) - A list of Nameserver
            additionals  (list) - A list of Additional
        """

        self.uid = uid
        self.qr = qr
        self.opcode = opcode
        self.aa = aa
        self.tc = tc
        self.rd = rd
        self.ra = ra
        self.z = z
        self.rcode = rcode
        self.questions = questions
        self.answers = answers
        self.nameservers = nameservers
        self.additionals = additionals
        


    def answer(self, address, sock):
        """Sets the type to answer, and sends it"""
        self.headers["QR"] = 1
        header = headerdict2bytes(self.headers)
        body = datadict2bytes(self.data)
        sock.sendto(header + body, address)

    def ask(self, address, port=53):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sent = s.sendto(self.toBinary(), (address, port))
        reply, from_server = s.recvfrom(4096)
        return Packet.from_binary(reply)
        return [hex(ord(l)) for l in reply]

    def toBinary(self):
        data = []
        #Message ID (2 bytes)
        data += int2bytes(self.uid, 2)

        #TODO kinda hacky ?
        data += [((self.qr & 1) << 7) | ((self.opcode & 15) << 3) |  ((self.aa & 1) << 2) | ((self.tc & 1) << 1) | (self.rd & 1)]
        data += [((self.ra & 1) << 7) | ((self.z & 7) << 4) | (self.rcode & 15)]
        data += int2bytes(len(self.questions), 2)
        data += int2bytes(len(self.answers), 2)
        data += int2bytes(len(self.nameservers), 2)
        data += int2bytes(len(self.additionals), 2)

        headers = str(bytearray(data))
        body = []
        for q in self.questions:
            body.append(q.toBinary())
        for a in self.answers:
            body.append(a.toBinary())
        for n in self.nameservers:
            body.append(n.toBinary())
        for a in self.additionals:
            body.append(a.toBinary())
        return headers + "".join(body)
        

    def __str__(self):
        qr = "Response" if self.qr else "Query"
        aa = "True" if self.aa else "False"
        tc = "True" if self.tc else "False"
        rd = "True" if self.rd else "False"
        ra = "True" if self.ra else "False"
        z  = "000" if self.z == 0 else str(self.z)
        return "Message ID: %d\nQR: %s\nOPCODE: %d\nAA: %s\nTC: %s\nRD: %s\nRA: %s\nZ: %s\nRCODE: %d\nQuestions: %d\nAnswers: %d\nNameservers: %d\nAdditionals: %d" % (
                self.uid, qr, self.opcode, aa, tc, rd, ra, z, self.rcode, len(self.questions), len(self.answers), len(self.nameservers), len(self.additionals))

if __name__ == "__main__":

    import doctest
    doctest.testmod()
