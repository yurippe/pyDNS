import sys
sys.path.append('../')
import pyDNS
import pyDNS.BitManipulator as BM

from pyDNS.Request import Packet, Question, Resource, Index
import TestPackages

packet = Packet.from_binary(str(TestPackages.SimplePackageWithOnly1Question))

assert packet.uid == 1337
assert packet.qr == 0
assert packet.opcode == 0
assert packet.aa == 0
assert packet.tc == 0
assert packet.rd == 1
assert packet.ra == 0
assert packet.z == 0
assert packet.rcode == 0
assert len(packet.questions) == 1
assert packet.questions[0].qtype == 28
assert packet.questions[0].qclass == 1

assert packet.toBinary() == str(TestPackages.SimplePackageWithOnly1Question)

pack2 = Packet(1337, 0, 0, 0, 0, 1, 0, questions=[Question("test.com", 28, 1)])
assert pack2.toBinary() == packet.toBinary()

print("All tests passed")

pack2.questions[0].qtype = 1
print BM.int2bytes(pack2.ask("8.8.8.8").answers[0].rdata.strategy.ip_address,4)
