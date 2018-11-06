import socket
import logging

def functional_method(node, map_lock, recvq_lock, sendq_lock, printq_lock, pipe_lock):
    logger = logging.getLogger('node')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    state = 0
    if node.get_poc_addr() is not None:
        state = 1
    while(True):
        if (state == 0):
            # wait for signal from packet_retrieval
            pass
        if (state == 1):
            # wait for signal from packet_retieval
            pipe_lock.acquire()
            node.load_pipe(0, "map")
            pipe_lock.release()
            # not sure if read needs to be locked will have to debug
            # safely locking it right now to be safe
            go_agane = True
            new_map = None
            while(go_agane):
                pipe_lock.acquire()
                if node.get_pipe()[0] == 1:
                    new_map = node.get_pipe()[1]
                    go_agane = False
                pipe_lock.release()

            broadcast = False

            map_lock.acquire()
            # iterate over keys in both maps
            for key in new_map:
                if key not in node.get_starmap():
                    broadcast =  True
                    node.update_starmap(key, new_map[key])
                    logger.info("Discovered new star-node {:s}.".format(key))

            map_for_send = node.get_starmap()
            map_lock.release()
            # send out new map packets in broadcast if needed

            if broadcast:
                # make packet
                pass

                for n in map_for_send:
                    addr, port = map_for_send[n]
                    s.sendto(packet, (addr, port))

            # always switch to state 2
            state = 2
        if (state == 2):
            map_lock.acquire()
            map_for_send = node.get_starmap()
            map_lock.release()

            for n in map_for_send:
                addr, port = map_for_send[n]
                # TODO
                # make packets with intent to get back RTT
                s.sendto(packet, (addr, port))

            if not node.is_sq_empty():
                state = 3
        if (state == 3):
            packet, addr, port = node.pop_sq()
            s.sendto(packet, (addr, port))
            logger.info("Sent packet to {:s}".format((addr, port)))
            if node.is_sq_empty():
                state = 2
