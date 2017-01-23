from pyDNS.Server import DNSServer
from pyDNS.Request import Packet
from pyDNS.util import string2bytearray

server = DNSServer()

def on_recv(data, address, sock):
    print("Received %s bytes from %s"%(len(data), address))
    print("DATA:")
    print(data)
    print("----------")
    print string2bytearray(data[:12])
    print("----------------")
    req = Packet.from_binary(data)
    print(req)
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
