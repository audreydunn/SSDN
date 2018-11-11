import packet_transmission
import packet_retrieval
import packet_ping
import packet_processing
import sys
import socket
import re
import logging
import logging.handlers
import os

import threading
from queue import Queue, PriorityQueue

from packets import Packet
from packets import FilePacket
from packets import json_to_packet

# Globals needing locks
Hub = [None, None]
Star_map = {}

# Global Queues
Trans_queue = PriorityQueue()
Recv_queue = Queue()

'''
Helper method for calculating RTT sum of this node
Star_map lock needs to be acquired
'''
def update_rtt_sum(self, map, l_addr, l_port):
    sum = 0
    for key in map:
        if key != (l_addr, l_port):
            sum += map[key][0]
    map[(l_addr, l_port)] = (0, sum)

'''
Helper method for calculating which node is the current Hub
Both Locks need to be acquired when this method is run
'''
def update_hub(self, Hub, map):
    min = 99999999999
    hub = None
    for key in map:
        if map[key][1] < min:
            min = map[key][1]
            hub = (key[0], int(key[1]))
    Hub[0] = hub[0]
    Hub[1] = hub[1]

'''
Helper method checking whether this node is the Hub
Hub lock needs to be acquired
'''
def is_hub(self, l_addr, l_port):
    if Hub == (l_addr, l_port):
        return True
    return False

if __name__ == "__main__":
    name = sys.argv[1]
    l_addr = socket.gethostbyname(socket.gethostname())
    l_port = sys.argv[2]
    max_nodes = sys.argv[5]
    poc_addr = sys.argv[3]
    poc_port = sys.argv[4]

    # Initialize logger
    logger = logging.getLogger('node')
    logger.setLevel(logging.DEBUG)
    logging_filename = 'node-{:s}.log'.format(name)
    # create file handler which logs even debug messages
    # fh = logging.FileHandler('node-{:s}.log'.format(name))
    should_roll_over = os.path.isfile(logging_filename)
    fh = logging.handlers.RotatingFileHandler(logging_filename, mode='w', backupCount=0)
    if should_roll_over:  # log already exists, roll over!
        fh.doRollover()
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # regex initialization for different send message matching
    string_pattern = re.compile("^send \".+\"$")
    file_pattern = re.compile("^send .+[.][a-z]+$")

    # initialize static variables (these never change)
    identity = name + ":" + l_addr + ":" + l_port
    poc_info = None
    if poc_addr is not None:
        poc_info = (poc_addr, int(poc_port))
    n = max_nodes

    # create our initial node entry in the star map
    Star_map[(l_addr, int(l_port))] = [0, 0]

    # initialize Hub to our node
    Hub[0], Hub[1] = l_addr, int(l_port)

    logger.info("Initialized node {:s} on {:s}:{:s}, max nodes {:s}, POC: {:s}:{:s}.".format(name, l_addr, l_port, max_nodes, poc_addr, poc_port))

    # initialize locks
    map_lock = threading.Lock()
    hub_lock = threading.Lock()

    # create event for Ping Thread
    start_pings = threading.Event()

    # let's make some threads :)
    args1 = (Trans_queue, 0)
    args2 = (Recv_queue, identity)
    args3 = (Star_map, Trans_queue, map_lock, identity, start_pings)
    args4 = (Star_map, Hub, Recv_queue, Trans_queue, map_lock, hub_lock, identity, poc_info, n, start_pings)
    trans_thread = threading.Thread(target=packet_transmission.core, name="trans", args=args1)
    recv_thread = threading.Thread(target=packet_retrieval.core, name="recv", args=args2)
    ping_thread = threading.Thread(target=packet_ping.core, name="ping", args=args3)
    proc_thread = threading.Thread(target=packet_processing.core, name="proc", args=args4)

    # start the threads :)
    try:
        trans_thread.start()
        recv_thread.start()
        ping_thread.start()
        proc_thread.start()
    except:
        # :(
        logger.error("Error occurred when starting threads")

    # gonna put command line stuff here, feel free to move it
    while 1:
        user_input = input("\nStar-node command: ")

        # is send message?
        if string_pattern.match(user_input):
            # gets stuff between "'s -> send "<message>"
            message = user_input[user_input.find('"')+1:user_input.find('"', user_input.find('"')+1)]

            with hub_lock:
                packet = Packet(message, "MSG_HUB", l_addr, l_port, Hub[0], Hub[1])

            Trans_queue.put((0, packet))

            logger.info("Added packet with message \"{:s}\" to send queue.".format(message))
        # is send file?
        elif file_pattern.match(user_input):
            # gets filename -> |s|e|n|d| |<filename>|
            filename = user_input[5:]

            with hub_lock:
                packet = FilePacket(filename, l_addr, l_port, Hub[0], Hub[1])

            Trans_queue.put((0, packet))

            logger.info("Added packet with file \"{:s}\" to send queue.".format(filename))
        elif user_input == "show-status":
            print("--BEGIN STATUS--")
            with map_lock:
                curr_map = Star_map
                for key, value in curr_map.items():
                    print("IDENTITY: {:s} RTT: {:s}".format(key, value))
            with hub_lock:
                print("HUB: {:s}", Hub)
            print("--END STATUS--")
            logger.debug("Printed status.")
        elif user_input == "disconnect":
            logger.info("Node disconnected.")
            break
            # might want to close some shit too
        elif user_input == "show-log":
            print("--BEGIN LOG--")
            f = open(logging_filename, 'r')
            file_contents = f.read()
            print(file_contents.strip())
            f.close()
            print("--END LOG--")
            logger.debug("Printed log.")
        else:
            logger.error("Unknown command. Please use one of the following commands: send \"<message>\", "
                         "send <filename>, show-status, disconnect, or show-log.")
