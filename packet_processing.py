import logging
import json

def core(Print_queue, Recv_queue, Trans_queue, map_lock, hub_lock, identity, poc_info, n, start_pings):
    logger = logging.getLogger('node')
    while(True):
        check = False
        recvq_lock.acquire()
        if not node.is_rq_empty():
            check = True
        recvq_lock.release()
        if check:
            recvq_lock.acquire()
            data, addr = node.pop_rq()
            recvq_lock.release()

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
                    map_lock.acquire()
                    map = node.get_starmap()
                    map_lock.release()

                    for node in map:


                printq_lock.acquire()
                node.append_pq(packet["Payload"])
                printq_lock.release()
            elif type == "FILE":
                # not currently implemented
                pass
            elif type == "RTT_REQ":
                pass
            elif type == "RTT_RESP" or type == "MAP":
                pass
