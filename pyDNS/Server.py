import socket

class DNSServer(object):

    BUFFER_SIZE = 4096

    def __init__(self, host='', port=53):
        self.host = host
        self.port = port

    @staticmethod
    def on_receive(data, address):
        print("Received %s bytes from %s"%(len(data), address))
        print("DATA:")
        print(data)



    def serve(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        localaddr = (self.host, self.port)
        sock.bind(localaddr)
        while True:
            data, address = sock.recvfrom(self.BUFFER_SIZE)
            self.on_receive(data, address)
