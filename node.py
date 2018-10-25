import packet_transmission
import packet_retrieval
import sys
import socket
import hashlib

# import thread
from collections import deque

class StarNode(object):

    def __init__(self, name, l_addr, l_port, max_nodes, poc_addr=None, poc_port=None):
        # constructor variables
        self.name = name
        self.l_addr = l_addr
        self.l_port = l_port
        self.n = max_nodes
        self.poc_addr = poc_addr
        self.poc_port = poc_port
        self.identity = name + ":" +  l_addr + ":" + l_port
        print(self.identity)

        # Data Structures and Booleans
        self.rrt_vector = []
        self.sum_vector = []
        self.hub = False
        self.star_map = {}
        self.receive_q = deque()
        self.send_q = deque()
        self.print_q = deque()

class Packet(object):

    def __init__(self, header, payload):
        self.header = header
        self.payload = payload
        self.checksum = hashlib.md5(payload.encode('utf-8')).hexdigest()

class FilePacket(Packet):

    def __init__(self, header, payload):
        super(header, payload)

if __name__ == "__main__":
    name = sys.argv[1]
    l_addr = socket.gethostbyname(socket.gethostname())
    l_port = sys.argv[2]
    max_nodes = sys.argv[5]
    poc_addr = sys.argv[3]
    poc_port = sys.argv[4]
    node = StarNode(name, l_addr, l_port, max_nodes, poc_addr, poc_port)
    pass
