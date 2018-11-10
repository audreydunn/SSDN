import logging
import time
import datetime

def core(Star_map, Print_queue, Trans_queue, map_lock, identity, start_pings):
    logger = logging.getLogger('node')
    name, l_addr, l_port = identity.split(":")
    l_port = int(l_port)
    start_pings.wait()
    while(True):
        # load queue with low priority packets
        for node in Star_map:
            if node != (l_addr, l_port)
                packet = Packet(datetime.datetime.now(), "RTT_REQ", l_addr, l_port, node[0], node[1])
                Trans_queue.put((1, packet))
        # wait for 60 sec
        time.sleep(60)
