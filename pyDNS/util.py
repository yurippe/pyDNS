def string2bytearray(string):
    """Inverse of bytearray2string"""
    bytes = []
    for byte in bytearray(string):
        string_byte = bin(byte)[2:]
        while len(string_byte) < 8:
            string_byte = "0" + string_byte
        bytes.append([int(bit) for bit in string_byte])
    return bytes

def bytearray2string(bytearray):
    """Inverse of string2bytearray"""
    string = ""
    for byte in bytearray:
        s = byte2int(byte)
        string += chr(s)
    return string

def byte2int(bitarray):
    if type(bitarray) == int: return bitarray
    sum = 0
    c = 0
    for i in xrange(len(bitarray)-1, -1, -1):
        if bitarray[i]:
            sum += 2**c
        c += 1
    return sum

def bytes2int(bytearray):
    sum = 0
    i = len(bytearray)-1
    for byte in bytearray:
        s = byte2int(byte)
        s <<= 8 * i
        sum += s
        i -= 1
    return sum


def int2bytes(val, numofbytes=1):
    if val >= (2**(8*numofbytes)):
        raise ValueError("Value out of bounds for " + str(numofbytes) + " bytes (" + str(val) + ")")
    b = bin(val)[2:]
    while len(b) < numofbytes*8:
        b = "0" + b
    bytes = []
    for i in xrange(numofbytes):
        byte = [int(i) for i in b[:8]]
        bytes.append(byte)
        b = b[8:]
    return bytes

def int2bits(val, numofbits=1):
    if val >= 2**numofbits:
        raise ValueError("Value out of bounds for " + str(numofbits) + " bits (" + str(val) + ")")
    b = bin(val)[2:]
    while len(b) < numofbits:
        b = "0" + b
    return [int(i) for i in b]



def parseDNSHeader(header_bytes):
    """Requires header_bytes to be a 2 dimensional 'array' so we can access individual bits of each byte"""
    return {
        #1st and 2nd Byte
        "ID": bytes2int(header_bytes[:2]),  #ID of the message
        #3rd Byte
        "QR": byte2int(header_bytes[2][0]),           #1st bit: 0 for query, 1 for anser
        "OPCODE": byte2int(header_bytes[2][1:5]),     #2nd, 3rd, 4th and 5th bit: The Opcode, 0 for standard query
        "AA": byte2int(header_bytes[2][5]),           #Auhoritative Answer Flag: 0 for non-autoritative, 1 for authoritative
        "TC": byte2int(header_bytes[2][6]),           #Truncation Flag: 1 for truncated, 0 for not
        "RD": byte2int(header_bytes[2][7]),           #Recursion Desired: Set by client if recursion is desired
        #4th Byte
        "RA": byte2int(header_bytes[3][0]),           #Recursion Available: Set by server if it supports recursion, 1 for yes
        "Z": byte2int(header_bytes[3][1:4]),          #Three reserved zero bits
        "RCODE": byte2int(header_bytes[3][4:8]),      #Response Code: Set by server, 0 indicates no error
        #5th and 6th Byte
        "QDCOUNT": bytes2int(header_bytes[4:6]),      #Question Count: Specifies the number of questions in the Question section
        #7th and 8th Byte
        "ANCOUNT": bytes2int(header_bytes[6:8]),      #Answer Record Count: Specifies the number of RRs in the Answer section
        #9th and 10th Byte
        "NSCOUNT": bytes2int(header_bytes[8:10]),     #Authority Record Count: Specifies the number of RRs in the Authority section
        #11th and 12th Byte
        "ARCOUNT": bytes2int(header_bytes[10:12]),      #Additional Record Count: Specifies the number of RRs in the Additional section
    }


def headerdict2bytes(h_dict, raw=False):
    #1st and 2nd Bytes
    bytes = int2bytes(h_dict["ID"], 2)
    #3rd Byte
    bytes.append(int2bits(h_dict["QR"]) + int2bits(h_dict["OPCODE"], 4) + int2bits(h_dict["AA"]) + int2bits(h_dict["TC"]) \
                  + int2bits(h_dict["RD"]))
    #4th Byte
    bytes.append(int2bits(h_dict["RA"]) + int2bits(h_dict["Z"], 3) + int2bits(h_dict["RCODE"], 4))
    #5th and 6th Byte
    bytes += int2bytes(h_dict["QDCOUNT"], 2)
    #7th and 8th Byte
    bytes += int2bytes(h_dict["ANCOUNT"], 2)
    #9th and 10th Byte
    bytes += int2bytes(h_dict["NSCOUNT"], 2)
    #11th and 12th Byte
    bytes += int2bytes(h_dict["ARCOUNT"], 2)
    if raw:
        return bytes
    return bytearray2string(bytes)

if __name__ == "__main__":
    b255 = [1,1,1,1,1,1,1,1]
    b127 = [0,1,1,1,1,1,1,1]
    assert byte2int(b255) == 255
    assert bytes2int([b127, b255]) == 32767
    assert bytes2int([b255, b255]) == 65535

    assert int2bytes(255,1) == [b255]
    assert int2bytes(32767,2) == [b127, b255]
    assert int2bytes(65535,2) == [b255, b255]


    print("Passed unit tests")
