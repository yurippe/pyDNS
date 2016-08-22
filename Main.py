from pyDNS.Server import DNSServer
from pyDNS.Request import Request
from struct import unpack_from
server = DNSServer()

def on_recv(data, address):
    print("Received %s bytes from %s"%(len(data), address))
    print("DATA:")
    print(data)
    print("----------")
    mid = unpack_from("bb", data, 0)
    theid = (mid[0] << 8) + mid[1]
    print mid
    print theid
    req = Request(data)
    print "id: " + str(req.id)
    print "Query(0) / Response(1): " + str(req.qr)
    print "Opcode: " + str(req.opcode)
    print "Authorative answer flag: " + str(req.aa)
    print "Recursion desired: " + str(req.rd)
    print "Question Count: " + str(req.qdcount)
    print req.questions
    print req.raw_questions
    print req.raw_body
    print("----------")

server.on_receive = on_recv

server.serve()

#####
# To test, run
# nsloopkup - 127.0.0.1
# on windows, and just type any domain
#
# To continue on this project these links will be of great help:
# http://www.zytrax.com/books/dns/ch15/
# http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm
# http://www.tcpipguide.com/free/t_DNSMessageResourceRecordFieldFormats-2.htm
# http://www.tcpipguide.com/free/t_DNSNameNotationandMessageCompressionTechnique-2.htm
# http://www.tcpipguide.com/free/t_DNSNameNotationandMessageCompressionTechnique.htm
# http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
#####