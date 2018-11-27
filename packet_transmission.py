import logging
import socket
import json
import datetime


def core(Trans_queue, Star_map, map_lock, History, history_lock, End, end_lock):
    logger = logging.getLogger('node')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        with end_lock:
            if End[0]:
                break
        if not Trans_queue.empty():
            priority, packet = Trans_queue.get()
            packet.set_timestamp(str(datetime.datetime.now()))
            data = packet.get_as_string()
            json_data = json.loads(data)
            addr = json_data["Header"]["DestAddr"]
            port = json_data["Header"]["DestPort"]
            type = json_data["Header"]["Type"]
            source_node = (addr, port)
            s.sendto(data.encode('utf-8'), (addr, int(port)))
            if type != "ACK" and type != "NACK" and type != "RTT_REQ":
                with history_lock:
                    History.append(packet)
                with map_lock:
                    Star_map[source_node] = [Star_map[source_node][0], Star_map[source_node][1],
                                             (Star_map[source_node][2] + 1), Star_map[source_node][3]]
            logger.info("Sent packet of type {0} to {1}".format(json_data["Header"]["Type"], (addr, port)))
