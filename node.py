import packet_transmission
import packet_retieval

import thread
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
        self.checksum = 0
        self.header = header
        self.payload = payload

class FilePacket(Packet):

    def __init__(self, header, payload):
        super(header, payload)

if __name__ == "__main__":
    pass
