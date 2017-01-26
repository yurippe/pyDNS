from util import parse_label_or_pointer, bytes2int

def get_strategy(for_class, rdlength, data, index):
    print rdlength
    if for_class == 1:
        return ARDataStrategy(for_class, rdlength, data, index)
    else:
        return RawRDataStrategy(for_class, rdlength, data, index)

class RDataStrategy(object):

    FIELDS = []
    def __init__(self, rdtype, rdlength, data, index):
        pass

class RawRDataStrategy(RDataStrategy):

    FIELDS = ["binary_data"]
    def __init__(self, rdtype, rdlength, data, index):
        self.binary_data = data[index.i:index.i + rdlength]
        index.i += rdlength

class SOARDataStrategy(RDataStrategy):

    FIELDS = [
        "primary_ns",
        "admin_mb",
        "serial_number",
        "refresh_interval",
        "retry_interval",
        "expiration_limit",
        "minimum_ttl"]

    def __init__(self, rdtype, rdlength, data, index):
        self.primary_ns = parse_label_or_pointer(data, index)
        index.inc()
        self.admin_mb = parse_label_or_pointer(data, index)
        index.inc()
        self.serial_number = bytes2int(data[index.i:index.i+4])
        index.inc(4)
        self.refresh_interval = bytes2int(data[index.i:index.i+4])
        index.inc(4)
        self.retry_interval = bytes2int(data[index.i:index.i+4])
        index.inc(4)
        self.expiration_limit = bytes2int(data[index.i:index.i+4])
        index.inc(4)
        self.minimum_ttl = bytes2int(data[index.i:index.i+4])
        index.inc(4)

class ARDataStrategy(RDataStrategy):

    FIELDS = ["ip_address"]

    def __init__(self, rdtype, rdlength, data, index):
        self.ip_address = bytes2int(data[index.i:index.i+4])
        index.inc(4)
