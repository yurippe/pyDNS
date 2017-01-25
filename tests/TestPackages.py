import sys
sys.path.append('../')
from pyDNS.BitManipulator import int2bytes
from pyDNS.BitManipulator import Byte as B

data = []
#Message ID = 1337
data += int2bytes(1337, 2)
#QR = 0 (Query) ; OPCODE = 0 (standard query) ;  AA = 0
#TC = 0 ; RD = 1
data += B("0 0000 0 0 1").toIntArray()
#RA = 0 ; Z = 000 ; RCODE = 0 ; 
data += B("0 000 0000").toIntArray()
#QDCOUNT = 1
data += int2bytes(1, 2)
#ANCOUNT = 0
data += int2bytes(0, 2)
#NSCOUNT = 0
data += int2bytes(0, 2)
#NSCOUNT = 0
data += int2bytes(0, 2)
#QNAME = "test.com"
data += B("00 000100").toIntArray() #First label length 4
data += [ord(l) for l in "test"]
data += B("00 000011").toIntArray() #Second label length 3
data += [ord(l) for l in "com"]
data += B().toIntArray() #Nullbyte
#QTYPE = 28 (AAAA Record)
data += int2bytes(28, 2)
#QCLASS = 1 (IN or Internet)
data += int2bytes(1, 2)
SimplePackageWithOnly1Question = bytearray(data)
