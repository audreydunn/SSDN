import logging

'''
Helper method for calculating RTT sum of this node
Star_map lock needs to be acquired
'''
def update_rtt_sum(map, l_addr, l_port, default_threshold):
    sum = 0
    for key in map:
        if key != (l_addr, l_port):
            sum += map[key][1]
    map[(l_addr, l_port)] = (sum, 0, 0, default_threshold)
    logger_internal = logging.getLogger('node')
    logger_internal.info("Updated RTT sum to {0}".format(sum))


'''
Helper method for calculating which node is the current Hub
Both Locks need to be acquired when this method is run
'''
def update_hub(Hub, map, default_threshold):
    oldhub = Hub
    min = 99999999999
    hub = None
    for key in map:
        if map[key][0] < min:
            min = map[key][0]
            hub = (key[0], int(key[1]))
    Hub[0] = hub[0]
    Hub[1] = hub[1]

    if oldhub != Hub:
        map[(Hub[0], Hub[1])] = [map[(Hub[0], Hub[1])][0], map[(Hub[0], Hub[1])][1],
                                        map[(Hub[0], Hub[1])][2], map[(Hub[0], Hub[1])][3] + 1]
                                        
        map[(oldhub[0], oldhub[1])] = [map[(oldhub[0], oldhub[1])][0], map[(oldhub[0], oldhub[1])][1],
                                        map[(oldhub[0], oldhub[1])][2], default_threshold]
        logger_internal = logging.getLogger('node')
        logger_internal.info("Hub has changed to {0}".format(Hub))
