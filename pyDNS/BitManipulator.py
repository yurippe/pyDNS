
#A byte is 8 bits long
#10000000 = 0x80 = 128
#01000000 = 0x40 = 64
#00100000 = 0x20 = 32
#00010000 = 0x10 = 16
#00001000 = 0x8  = 8
#00000100 = 0x4  = 4
#00000010 = 0x2  = 2
#00000001 = 0x1  = 1

def mask_byte(byte, mask="11111111"):
    """
    >>> mask_byte(255, "10000000")
    128
    >>> mask_byte(255)
    255
    >>> mask_byte(96, "10011111")
    0
    >>> mask_byte(96, "11011111")
    64
    >>> mask_byte(96, "11111111")
    96
    """
    i = int(mask, 2)
    return byte & i

def read_bits_from_to(byte, from_bit, to_bit):
    """
    (Pads with 0 in the front if to_bit - from_bit < 8)
    
    >>> read_bits_from_to(255, 0, 8)
    255
    >>> read_bits_from_to(255, 1, 8)
    127
    >>> read_bits_from_to(255, 2, 6)
    15
    >>> read_bits_from_to(24, 2, 6)
    6
    """
    length = to_bit - from_bit
    s = 0
    for i in range(length):
        s = (s << 1) + 1
    return (byte & (s << from_bit)) >> from_bit

#This is wrong because it reads it from the wrong side for our puroses
def _read_bits(byte, from_bit, length):
    """
    (Pads with 0 in the front if to_bit - from_bit < 8)
    
    >>> _read_bits(255, 0, 8)
    255
    >>> _read_bits(255, 1, 7)
    127
    >>> _read_bits(255, 2, 4)
    15
    >>> _read_bits(24, 2, 4)
    6
    """
    s = 0
    for i in range(length):
        s = (s << 1) + 1
    return (byte & (s << from_bit)) >> from_bit


def read_bits(byte, from_bit, length):
    """
    (Pads with 0 in the front if to_bit - from_bit < 8)
    
    >>> read_bits(255, 0, 8)
    255
    >>> read_bits(255, 1, 7)
    127
    >>> read_bits(255, 2, 4)
    15
    >>> read_bits(24, 2, 4)
    6
    >>> read_bits(255, 1, 3)
    7
    """
    s = 255 #1111 1111
    s = s >> from_bit
    rightside = 0
    for i in range(8-(from_bit + length)):
        rightside = (rightside << 1) + 1
    s -= rightside
    return (byte & s) >> (8 - (from_bit + length))


def bytes2int(byte_array):
    """
    >>> bytes2int([0, 255])
    255
    >>> bytes2int([255, 0])
    65280
    >>> bytes2int([255, 255])
    65535
    >>> bytes2int([255, 2])
    65282
    """
    s = 0
    for byte in byte_array:
        s = (s << 8) + byte
    return s

def int2bytes(integer, bytelength=1):
    bytearr = []
    mask = 255
    for i in range(bytelength):
        masked = integer & (mask << (i*8))
        downsized = masked >> (i*8)
        bytearr = [downsized] + bytearr
    return bytearr
    
class Byte(object):
    def __init__(self, bits="00000000"):
        self.bits = [int(b) for b in bits.replace(" ", "")]

    def set_bit(self, index, val):
        if val: self.bits[index] = 1
        else: self.bits[index] = 0

    def toInt(self):
        return int("".join([str(b) for b in self.bits]), 2)

    def toIntArray(self):
        return [self.toInt()]

if __name__ == "__main__":

    import doctest
    doctest.testmod()
