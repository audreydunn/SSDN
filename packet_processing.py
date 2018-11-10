import logging
import json
import datetime
import copy

def core(Star_map, Print_queue, Recv_queue, Trans_queue, map_lock, hub_lock, identity, poc_info, n, start_pings):
    logger = logging.getLogger('node')
    name, l_addr, l_port = identity.split(":")
    while(True):
        if not Recv_queue.empty():
            data, addr = Recv_queue.get()

            packet = json.loads(data)

            type = packet["Header"]["Type"]

            if type == "ACK":
                # no packet loss in Milestone 2
                pass
            elif type == "NACK":
                # no packet loss in Milestone 2
                pass
            elif type == "END":
                # no losing nodes in Milestone 2
                pass
            elif type == "MSG":
                Print_queue.put(packet["Payload"])

            elif type == "MSG_HUB":
                for node in Star_map:
                    pass
            elif type == "FILE":
                # not currently implemented
                pass
            elif type == "RTT_REQ":
                packet = Packet((Star_map, packet["Payload"]), "RTT_RESP", l_addr, l_port, packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
                Trans_queue.put((1, packet))
            elif type == "RTT_RESP":
                activate_thread = False
                if len(Star_map) == 1:
                    activate_thread = True

                # update copy of map
                sent_map, sent_time = packet["Payload"]
                source_node = (packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
                RTT = (datetime.datetime.now() - sent_time).seconds

                with map_lock:
                    # update source node in our mapping
                    map[source_node] = [sent_map[source_node][0], RTT]
                    # add new node to our map if known by other node
                    for i in sent_map:
                        if i not in map:
                            map[i] = [sent_map[i][0], 0]

                if activate_thread:
                    start_pings.set()
