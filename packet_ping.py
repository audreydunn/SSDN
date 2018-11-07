import logging

def core(Print_queue, Trans_queue, map_lock, identity, start_pings):
    start_pings.wait()
    while(True):
        # load queue with packets
        # wait for 60 sec
