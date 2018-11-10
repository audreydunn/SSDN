import logging
import json

def core(Print_queue, Recv_queue, Trans_queue, map_lock, hub_lock, identity, poc_info, n, start_pings):
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
                if node.is_hub():
                    # need to broadcast
                    with map_lock:
                        map = Star_map

                    for node in map:


                Print_queue.put(packet["Payload"])

            elif type == "MSG_HUB":
                pass
            elif type == "FILE":
                # not currently implemented
                pass
            elif type == "RTT_REQ":
                pass
            elif type == "RTT_RESP" or type == "MAP":
                pass
