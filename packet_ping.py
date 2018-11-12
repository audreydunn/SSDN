import logging
import time
import datetime
import json
from packets import Packet


def core(Star_map, Trans_queue, map_lock, identity, start_pings, End, end_lock):
    logger = logging.getLogger('node')
    name, l_addr, l_port = identity.split(":")
    l_port = int(l_port)
    start_pings.wait()
    while(True):
        with end_lock:
            if End[0]:
                break
        # load queue with low priority packets
        with map_lock:
            for node in Star_map:
                if node != (l_addr, l_port):
                    payload = json.dumps({
                        "Map": Star_map.__repr__(),
                        "Timestamp": datetime.datetime.now().__repr__()
                    })
                    packet = Packet(payload, "RTT_REQ", l_addr, l_port, node[0], node[1])
                    Trans_queue.put((1, packet))
        # wait for 60 sec
        time.sleep(20)
