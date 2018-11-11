import logging
import socket
import json


def core(Trans_queue, hi):
    logger = logging.getLogger('node')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        if not Trans_queue.empty():
            priority, packet = Trans_queue.get()
            data = packet.get_as_string()
            json_data = json.loads(data)
            addr = json_data["Header"]["DestAddr"]
            port = json_data["Header"]["DestPort"]
            s.sendto(data.encode('utf-8'), (addr, port))
            logger.info("Sent packet of type {0} to {1}".format(json_data["Header"]["Type"], (addr, port)))
