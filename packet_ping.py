import logging
import time
import datetime
import json
from packets import Packet
from helper_methods import update_rtt_sum, update_hub


def core(Star_map, Hub, Trans_queue, History, history_lock, map_lock, hub_lock, identity, start_pings, End, end_lock, default_threshold):
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
                    logger.debug("Attempting to resend packet sent at time {0}".format(curr_packet.get_timestamp()))
                    Trans_queue.put((0, curr_packet))

        with map_lock:
            update = False
            repeat = True
            i = 0
            keys = list(Star_map.keys())
            while repeat and i < len(keys):
                if Star_map[keys[i]][2] > Star_map[keys[i]][3]:
                    logger.debug("Node {0} is now apparently down/offline.".format(Star_map[keys[i]]))
                    update = True
                    repeat = False
                i += 1
            if update:
                # if node was deleted we need to update our values
                update_rtt_sum(Star_map, l_addr, l_port, default_threshold)

                with hub_lock:
                    update_hub(Hub, Star_map, default_threshold)

        counter += 1
        if counter == 3:  # we start pinging now
            # load queue with low priority packets
            pinglist = []
            with map_lock:
                for node in Star_map:
                    if node != (l_addr, l_port) and Star_map[node][2] < Star_map[node][3]:
                        payload = json.dumps({
                            "Map": Star_map.__repr__(),
                            "Timestamp": datetime.datetime.now().__repr__()
                        })
                        packet = Packet(payload, "RTT_REQ", l_addr, l_port, node[0], node[1])
                        Trans_queue.put((2, packet))
                        pinglist.append(str(node))
            counter = 0
            logger.debug("Pinging the following nodes for RTT: {0}".format(pinglist))
        # wait for 1 sec
        time.sleep(1)
