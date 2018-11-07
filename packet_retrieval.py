import logging
import socket

def core(Print_queue, Recv_queue):
    logger = logging.getLogger('node')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((node.get_l_addr(), node.get_l_port()))
    while(True):
        data, addr = s.recvfrom(1024)

        Recv_queue.put(data)
