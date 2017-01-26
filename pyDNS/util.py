from BitManipulator import read_bits, bytes2int

class Index(object):
    def __init__(self, i=0):
        self.i = i

    def inc(self, incr=1):
        self.i += incr

def _parse_label(data, index):
    length = read_bits(data[index.i], 2, 6)
    name = []
    for l in range(length):
        index.inc()
        name.append(chr(data[index.i]))
    return name

def _parse_pointer(data, index):
    offset = bytes2int(data[index.i: index.i + 2]) & 0x3FFF #16383 (DEC) We & with 00111111 11111111 to get rid of the first 2 bits
    return parse_label_or_pointer(data, Index(offset-12))  #Offset - header length (12)
        
def parse_label_or_pointer(data, index):
    val = []
    length = data[index.i]
    while length > 0:
        read_type = read_bits(length, 0, 2)
        if read_type == 0: #Label
            val.append(_parse_label(data, index))
            index.inc()
        elif read_type == 3: #Pointer
            pval = _parse_pointer(data, index) #Because pointers terminate this should be ok, but have in mind this area
            index.inc() #pointers are 2 bytes long, so why does this work?
            return val + pval
        length = data[index.i]
    return val

def dotted2string(dottedarray):
    """
    >>> _dotted2string(_string2dotted("www.test.com"))
    'www.test.com'
    """
    return ".".join(["".join(subarr) for subarr in dottedarray])

def string2dotted(string):
    return string.split(".")
