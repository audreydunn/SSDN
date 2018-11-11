import logging
import socket


def core(Trans_queue, hi):
    logger = logging.getLogger('node')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        if not Trans_queue.empty():
            priority, packet = Trans_queue.get()
            data = packet.get_as_string()
            s.sendto(data, (addr, port))
            logger.info("Sent packet to {:s}".format((addr, port)))
