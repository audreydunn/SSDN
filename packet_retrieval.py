import logging
import socket


def core(Recv_queue, identity):
    logger = logging.getLogger('node')
    name, l_addr, l_port = identity.split(":")
    l_port = int(l_port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((l_addr, l_port))
    while(True):
        data, addr = s.recvfrom(1024)
        logger.info("Received packet from {:s}.".format(addr))
        Recv_queue.put(data)
