from pyDNS.Server import DNSServer
from pyDNS.Request import Request
from struct import unpack_from
from pyDNS.util import *
server = DNSServer()

def on_recv(data, address):
    print("Received %s bytes from %s"%(len(data), address))
    print("DATA:")
    print(data)
    print("----------")
    req = Request(data)
    print "-- HEAD"
    print req.headers
    print "Original"
    print req.raw_headers
    print "Generated"
    gen = headerdict2bytes(req.headers)
    print gen
    print "Equality:"
    print gen == req.raw_headers
    print "-- DATA"
    print req.data
    print "Original"
    print req.raw_data
    print "Generated"
    gen = datadict2bytes(req.data)
    print gen
    print "Equality:"
    print gen == req.raw_data
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