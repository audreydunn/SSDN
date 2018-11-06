import packet_transmission
import packet_retrieval
import sys
import socket
import hashlib
import re

import threading
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

        # Data Structures and Booleans

        # (RTT, Sum)
        self.hub = None
        # this holds RTTs and the Sums known for each node (RTT, Sum)
        self.rtt_vector = {}
        self.star_map = {}
        self.trans_q = deque()
        self.send_q = deque()
        self.print_q = deque()

        # useful for passing signals :)
        # Format: (code #, data requested)
        # code 0 = I need some data
        # code 1 = Here's the data
        self.thread_pipe = None

    # TODO: write helper methods for vectors

    '''
    Helper method for calculating RTT sum of this node
    '''
    def update_rtt_sum(self):
        sum = 0
        for key in rtt_vector:
            if key != (self.l_addr, self.l_port):
                sum += rtt_vector[key][0]
        self.rtt_sum = sum

    '''
    Helper method for calculating which node is the current Hub
    '''
    def update_hub(self):
        max = -1
        hub = None
        for key in rtt_vector:
            if rtt_vector[key][1] > max:
                max = rtt_vector[key][1]
                hub = key
        self.hub = hub

    '''
    Helper method checking whether this node is the Hub
    '''
    def is_hub(self):
        if self.hub == (self.l_addr, self.l_port):
            return True
        return False

    '''
    Return thread pipe data
    '''
    def get_pipe(self):
        return self.thread_pipe

    '''
    Place data into pipe
    '''
    def load_pipe(self, code, payload):
        self.thread_pipe = (code, payload)

    '''
    Return POC Port
    '''
    def get_poc_port(self):
        return self.poc_port

    '''
    Return POC Address
    '''
    def get_poc_addr(self):
        return self.poc_addr

    '''
    Return RTT Vector
    '''
    def get_rtt_vector(self):
        return self.rtt_vector

    '''
    Update/Add a key, value pair to the star map
    '''
    def update_starmap(self, key, value):
        self.star_map[key] = value

    '''
    Return value stored in star map
    '''
    def lookup_starmap(self, key):
        return self.star_map[key]

    '''
    Return current star map
    '''
    def get_starmap(self):
        return self.star_map

    '''
    Invert the truth value of hub
    '''
    def flip_hub(self):
        self.hub = not self.hub

    '''
    Return the identity string
    '''
    def get_identity(self):
        return self.identity

    '''
    Return whether transmission queue is empty
    '''
    def is_tq_empty(self):
        if len(self.trans_q) > 0:
            return True
        return False

    '''
    Return whether send queue is empty
    '''
    def is_sq_empty(self):
        if len(self.send_q) > 0:
            return True
        return False

    '''
    Return whether print queue is empty
    '''
    def is_pq_empty(self):
        if len(self.print_q) > 0:
            return True
        return False

    '''
    Append item to transmission queue
    '''
    def append_tq(self, item):
        self.trans_q.append(item)

    '''
    Append item to send queue
    '''
    def append_sq(self, item):
        self.send_q.append(item)

    '''
    Append item to print queue
    '''
    def append_pq(self, item):
        self.print_q.append(item)

    '''
    Remove and return item from front of transmission queue
    '''
    def pop_tq(self):
        return self.trans_q.popleft()

    '''
    Remove and return item from front of send queue
    '''
    def pop_sq(self):
        return self.send_q.popleft()

    '''
    Remove and return item from front of print queue
    '''
    def pop_pq(self):
        return self.print_q.popleft()

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

    # initialize locks
    map_lock = threading.Lock()
    transq_lock = threading.Lock()
    sendq_lock = threading.Lock()
    printq_lock = threading.Lock()
    pipe_lock = threading.Lock()

    # regex initialization for different send message matching
    string_pattern = re.compile("^send \".+\"$")
    file_pattern = re.compile("^send .+[.][a-z]+$")

    # let's make some threads :)
    args = (node, map_lock, transq_lock, sendq_lock, printq_lock, pipe_lock)
    trans_thread = threading.Thread(target=packet_transmission.functional_method, name="trans", args=args)
    recv_thread = threading.Thread(target=packet_retrieval.functional_method, name="recv", args=args)

    # start the threads :)
    try:
        trans_thread.start()
        recv_thread.start()
    except:
        # :(
        print("Error occurred when starting threads")

    # gonna put command line stuff here, feel free to move it
    while 1:
        user_input = input("Star-node command: ")

        # is send message?
        if string_pattern.match(user_input):
            # gets stuff between "'s -> send "<message>"
            message = user_input[user_input.find("(")+1:user_input.find(")")]
            print("Sending message {:s} to all nodes.".format(message))
        # is send file?
        elif file_pattern.match(user_input):
            # gets filename -> |s|e|n|d| |<filename>|
            filename = user_input[5:]
            print("Sending file {:s} to all nodes.".format(filename))
        elif user_input == "show-status":
            print("Node status:")
            curr_map = node.get_starmap()
            rtt_vector = node.get_rtt_vector()
            for key, value in curr_map.items():
                print("ADDRESS: {:s} PORT: {:s} RTT: {:s}".format(key, value, rtt_vector.get(key)))
            # need some way to display the currently selected hub as well
        elif user_input == "disconnect":
            print("Disconnecting...")
            break
            # might want to close some shit too
        elif user_input == "show-log":
            print("Hi. I'm a log.")
            # print log
        else:
            print("Unknown command. Please use one of the following commands: send \"<message>\", "
                  "send <filename>, show-status, disconnect, or show-log.")

    # execute this to make the master thread wait on the other threads
    # trans_thread.join()
    # recv_thread.join()
