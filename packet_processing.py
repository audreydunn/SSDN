import logging
import json
import datetime
import copy
import os
import hashlib
from packets import Packet
from packets import FilePacket
from helper_methods import update_rtt_sum, update_hub


def core(Star_map, Hub, History, history_lock, Recv_queue, Trans_queue, map_lock, hub_lock, identity, n, start_pings, End, end_lock, default_threshold):
    logger = logging.getLogger('node')
    name, l_addr, l_port = identity.split(":")
    l_port = int(l_port)
    while(True):
        with end_lock:
            if End[0]:
                break
        if not Recv_queue.empty():
            data = Recv_queue.get()

            packet = json.loads(data.strip())
            source_node = (packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
            with map_lock:
                # if we get a message, reset counter to 0
                if source_node in Star_map:
                    Star_map[source_node] = [Star_map[source_node][0], Star_map[source_node][1], 0,
                                             Star_map[source_node][3]]

            header_checksum = packet["Header"]["Checksum"]
            calc_checksum = hashlib.md5(packet["Payload"].encode('utf-8')).hexdigest()
            is_corrupted = header_checksum != calc_checksum
            if is_corrupted:
                # send NACK
                payload = json.dumps({
                    "Timestamp": packet["Header"]["Timestamp"],
                    "Checksum": packet["Header"]["Checksum"]
                })
                resp_packet = Packet(payload, "NACK", l_port, l_addr, packet["Header"]["SourceAddr"],
                                     packet["Header"]["SourcePort"])
                Trans_queue.put((1, resp_packet))
            else:
                type = packet["Header"]["Type"]
                if type != "ACK" and type != "NACK" and type != "RTT_REQ":
                    # send ACK
                    payload = json.dumps({
                        "Timestamp": packet["Header"]["Timestamp"],
                        "Checksum": packet["Header"]["Checksum"]
                    })
                    resp_packet = Packet(payload, "ACK", l_port, l_addr, packet["Header"]["SourceAddr"],
                                         packet["Header"]["SourcePort"])
                    Trans_queue.put((1, resp_packet))

                if type == "ACK":
                    payload_json = json.loads(packet["Payload"])
                    timestamp = payload_json["Timestamp"]
                    checksum = payload_json["Checksum"]

                    with history_lock:
                        for curr_packet in History:
                            if curr_packet.get_timestamp() == timestamp or curr_packet.get_checksum() == checksum:
                                History.remove(curr_packet)

                    source_identity = "{0}:{1}".format(packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
                    logger.debug("Received ACK from {0}: {1}".format(source_identity, packet["Payload"]))
                elif type == "NACK":
                    payload_json = json.loads(packet["Payload"])
                    timestamp = payload_json["Timestamp"]
                    checksum = payload_json["Checksum"]

                    with history_lock:
                        for curr_packet in History:
                            if curr_packet.get_timestamp() == timestamp or curr_packet.get_checksum() == checksum:
                                History.remove(curr_packet)
                                Trans_queue.put((0, curr_packet))

                    source_identity = "{0}:{1}".format(packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
                    logger.debug("Received NACK from {0}: {1}".format(source_identity, packet["Payload"]))
                elif type == "MSG":
                    source_identity = "{0}:{1}".format(packet["Header"]["SourceAddr"],packet["Header"]["SourcePort"])
                    logger.info("Received message from {0}: {1}".format(source_identity, packet["Payload"]))
                    print("Received message from {0}: {1}".format(source_identity, packet["Payload"]))
                elif type == "MSG_HUB":
                    flag = False
                    with hub_lock:
                        if Hub == [l_addr, l_port]:
                            flag = True

                    if flag:
                        with map_lock:
                            for node in Star_map:
                                if node != (l_addr, l_port) and node != (packet["Header"]["SourceAddr"],
                                                                         int(packet["Header"]["SourcePort"])):
                                    new_packet = Packet(packet["Payload"], "MSG", packet["Header"]["SourceAddr"],
                                                        packet["Header"]["SourcePort"], node[0], node[1])
                                    Trans_queue.put((0, new_packet))
                        source_identity = "{:s}:{:s}".format(packet["Header"]["SourceAddr"],
                                                             packet["Header"]["SourcePort"])
                        logger.info("Received message from {0}: {1}".format(source_identity, packet["Payload"]))
                        print("Received message from {0}: {1}".format(source_identity, packet["Payload"]))

                    else:
                        # if we're not the hub let's send the packet to who we think is the hub until hub converges in the network
                        with hub_lock:
                            new_packet = Packet(packet["Payload"], "MSG_HUB", packet["Header"]["SourceAddr"],
                                                packet["Header"]["SourcePort"], Hub[0], Hub[1])
                            Trans_queue.put((0, new_packet))
                elif type == "FILE":
                    if not os.path.exists("downloads"):
                        os.mkdir("downloads")

                    payload_json = json.loads(packet["Payload"])

                    filename = "downloads/{:s}".format(payload_json["Filename"])
                    file = open(filename, "wb")
                    file.write(eval(payload_json["Data"]))
                    file.close()

                    source_identity = "{0}:{1}".format(packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
                    logger.info("Received file from {0}. Saved in {1}".format(source_identity, filename))
                    print("Received file from {0}. Saved in {1}".format(source_identity, filename))
                    pass
                elif type == "FILE_HUB":
                    flag = False
                    with hub_lock:
                        if Hub == [l_addr, l_port]:
                            flag = True

                    if flag:
                        with map_lock:
                            for node in Star_map:
                                if node != (l_addr, l_port) and node != (packet["Header"]["SourceAddr"],
                                                                         int(packet["Header"]["SourcePort"])):
                                    new_packet = Packet(packet["Payload"], "FILE", packet["Header"]["SourceAddr"],
                                                        packet["Header"]["SourcePort"], node[0], node[1])
                                    Trans_queue.put((0, new_packet))

                        if not os.path.exists("downloads"):
                            os.mkdir("downloads")

                        payload_json = json.loads(packet["Payload"])

                        filename = "downloads/{:s}".format(payload_json["Filename"])
                        file = open(filename, "wb")
                        file.write(eval(payload_json["Data"]))
                        file.close()

                        source_identity = "{0}:{1}".format(packet["Header"]["SourceAddr"],
                                                           packet["Header"]["SourcePort"])
                        logger.info("Received file from {0}. Saved in {1}".format(source_identity, filename))
                        print("Received file from {0}. Saved in {1}".format(source_identity, filename))

                    else:
                        # if we're not the hub let's send the packet to who we think is the hub until hub converges in the network
                        with hub_lock:
                            new_packet = Packet(packet["Payload"], "FILE_HUB", packet["Header"]["SourceAddr"],
                                                packet["Header"]["SourcePort"], Hub[0], Hub[1])
                            Trans_queue.put((0, new_packet))
                elif type == "RTT_REQ":
                    activate_thread = False

                    payload_json = json.loads(packet["Payload"])
                    sent_map = eval(payload_json["Map"])
                    sent_time = payload_json["Timestamp"]

                    with map_lock:
                        if len(Star_map) == 1:
                            activate_thread = True

                        # add new node to our map if known by other node
                        for i in sent_map:
                            if i not in Star_map:
                                Star_map[i] = [sent_map[i][0], 0, 0, default_threshold]

                    payload = json.dumps({
                        "Map": Star_map.__repr__(),
                        "Timestamp": str(sent_time)
                    })
                    packet = Packet(payload, "RTT_RESP", l_addr, l_port, packet["Header"]["SourceAddr"],
                                    packet["Header"]["SourcePort"])
                    Trans_queue.put((1, packet))
                    packet_json = json.loads(packet.get_as_string())
                    source_identity = "{0}:{1}".format(packet_json["Header"]["SourceAddr"],
                                                       packet_json["Header"]["SourcePort"])
                    logger.info("Received RTT request from {:s}".format(source_identity))

                    if activate_thread:
                        start_pings.set()
                elif type == "RTT_RESP":
                    payload_json = json.loads(packet["Payload"])
                    sent_map = eval(payload_json["Map"])
                    sent_time = payload_json["Timestamp"]
                    source_node = (packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
                    logger.info("Received RTT response from {0}".format(source_node))
                    diff = (datetime.datetime.now() - data.get_timestamp()).microseconds
                    RTT = float(diff.seconds) + (diff.microseconds / 1000000.0)

                    with map_lock:
                        # update source node in our mapping
                        Star_map[source_node] = [sent_map[source_node][0], RTT, Star_map[source_node][2], Star_map[source_node][3]]

                        update_rtt_sum(Star_map, l_addr, l_port, default_threshold)

                        with hub_lock:
                            update_hub(Hub, Star_map, default_threshold)
