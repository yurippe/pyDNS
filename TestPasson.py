from pyDNS.Server import DNSServer
from pyDNS.Request import Packet
from pyDNS.util import *
import socket

server = DNSServer()

##DOES WORK
# def onRecv(data, address, s):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#     server_addr = ("8.8.8.8", 53)
#     sent = sock.sendto(data, server_addr)
#     print sent
#     reply, f = sock.recvfrom(4096)
#
#     p = Packet(reply)
#
#     print p.raw_headers
#     print p.raw_data
#
#     s.sendto(reply, address)


#DOES NOT WORK, because we aren't parsing beyond questions atm
def onRecv(data, address, sock):
    packet = Packet(data)
    print "------------------"
    print packet.headers
    print packet.data
    reply_from_google = packet.askOther("8.8.8.8")
    print "------"
    print reply_from_google.headers
    print reply_from_google.data
    print "------------------"
    reply_from_google.headers["AA"] = 1
    reply_from_google.answer(address, sock)


server.on_receive = onRecv

server.serve()