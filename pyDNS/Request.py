import socket
from BitManipulator import read_bits, bytes2int
#http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
request_types = {1 : "A", 2: "NS", 5: "CNAME", 6: "SOA", 11: "WKS", 12: "PTR", 15: "MX", 33: "SRV",
                 28: "AAAA", 255: "*"}

#Parsing information:
#http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm


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
        print(ID)
        print(QR)
        print(QDCOUNT)

        return Packet(ID, QR, OPCODE, AA, TC, RD, RA, Z, RCODE)
 
        

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

    def askOther(self, address, port=53):
        self.headers["QR"] = 0
        header = headerdict2bytes(self.headers)
        body = datadict2bytes(self.data)
        middlesock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytessent = middlesock.sendto(header + body, (address, port))
        reply, from_server = middlesock.recvfrom(4096)
        return Packet(reply)

    def __str__(self):
        qr = "Response" if self.qr else "Query"
        aa = "True" if self.aa else "False"
        tc = "True" if self.tc else "False"
        rd = "True" if self.rd else "False"
        ra = "True" if self.ra else "False"
        z  = "000" if self.z == 0 else str(self.z)
        return "Message ID: %d\nQR: %s\nOPCODE: %d\nAA: %s\nTC: %s\nRD: %s\nRA: %s\nZ: %s\nRCODE: %d" % (
                self.uid, qr, self.opcode, aa, tc, rd, ra, z, self.rcode)
