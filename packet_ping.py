import logging
import time
import datetime
import json
from packets import Packet


def core(Star_map, Trans_queue, History, history_lock, map_lock, identity, start_pings, End, end_lock):
    logger = logging.getLogger('node')
    name, l_addr, l_port = identity.split(":")
    l_port = int(l_port)
    start_pings.wait()
    counter = 0
    while(True):
        with end_lock:
            if End[0]:
                break
        with history_lock:
            for curr_packet in History:
                if (datetime.datetime.now() - curr_packet.get_timestamp()).microseconds >= 500000:
                    History.remove(curr_packet)
                    Trans_queue.put((0, curr_packet))
        counter = counter + 1
        if counter == 10:  # we start pinging now
            # load queue with low priority packets
            with map_lock:
                for node in Star_map:
                    if node != (l_addr, l_port):
                        payload = json.dumps({
                            "Map": Star_map.__repr__(),
                            "Timestamp": datetime.datetime.now().__repr__()
                        })
                        packet = Packet(payload, "RTT_REQ", l_addr, l_port, node[0], node[1])
                        Trans_queue.put((2, packet))
        # wait for 1 sec
        time.sleep(1)
