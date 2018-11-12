import logging
import socket
import json


def core(Recv_queue, identity, End, end_lock):
    logger = logging.getLogger('node')
    name, l_addr, l_port = identity.split(":")
    l_port = int(l_port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((l_addr, l_port))
    while 1:
        data, addr = s.recvfrom(1024)
        with end_lock:
            if End[0]:
                break
        # data_json = json.loads(data)
        # logger.info("Received packet of type {0} from {1}.".format(data_json["Header"]["Type"], addr))
        Recv_queue.put(data)
