import logging
import json
import datetime
import copy
import os
from node import update_rtt_sum, update_hub
from packets import Packet
from packets import FilePacket


def core(Star_map, Hub, Recv_queue, Trans_queue, map_lock, hub_lock, identity, n, start_pings):
    logger = logging.getLogger('node')
    name, l_addr, l_port = identity.split(":")
    l_port = int(l_port)
    while(True):
        if not Recv_queue.empty():
            data = Recv_queue.get()

            packet = json.loads(data.strip())

            type = packet["Header"]["Type"]

            if type == "ACK":
                # no packet loss in Milestone 2
                pass
            elif type == "NACK":
                # no packet loss in Milestone 2
                pass
            elif type == "END":
                # no losing nodes in Milestone 2
                pass
            elif type == "MSG":
                source_identity = "{:s}:{:s}".format(packet["Header"]["SourceAddr"],packet["Header"]["SourcePort"])
                logger.info("Received message from {:s}: {:s}".format(source_identity, packet["Payload"]))
            elif type == "MSG_HUB":
                flag = False
                with hub_lock:
                    if Hub == [l_addr, l_port]:
                        flag = True

                if flag:
                    with map_lock:
                        for node in Star_map:
                            if node != (l_addr, l_port):
                                packet = Packet(packet["Payload"], "MSG", l_addr, l_port, node[0], node[1])
                                Trans_queue.put((0, packet))
                    source_identity = "{:s}:{:s}".format(packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
                    logger.info("Received message from {:s}: {:s}".format(source_identity, packet["Payload"]))

                else:
                    # if we're not the hub let's send the packet to who we think is the hub until hub converges in the network
                    with hub_lock:
                        packet = Packet(packet["Payload"], "MSG_HUB", l_addr, l_port, Hub[0], Hub[1])

                    Trans_queue.put((0, packet))
            elif type == "FILE":
                if not os.path.exists("downloads"):
                    os.mkdir("downloads")

                filename = "downloads/{:s}".format(packet["Payload"]["Filename"])
                file = open(filename, "wb")
                file.write(packet["Payload"]["Data"])
                file.close()

                source_identity = "{:s}:{:s}".format(packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
                logger.info("Received file from {:s}. Saved in {:s}".format(source_identity, filename))
                pass
            elif type == "RTT_REQ":
                activate_thread = False

                payload_json = json.loads(packet["Payload"])
                sent_map = payload_json["Map"]
                sent_time = payload_json["Timestamp"]

                with map_lock:
                    if len(Star_map) == 1:
                        activate_thread = True

                    # add new node to our map if known by other node
                    for i in sent_map:
                        if i not in Star_map:
                            Star_map[i] = [sent_map[i][0], 0]

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
                activate_thread = False

                payload_json = json.loads(packet["Payload"])
                sent_map = eval(payload_json["Map"])
                sent_time = payload_json["Timestamp"]
                source_node = (packet["Header"]["SourceAddr"], packet["Header"]["SourcePort"])
                logger.info("Received RTT response from {0}".format(source_node))
                diff = (datetime.datetime.now() - eval(sent_time))
                RTT = float(diff.seconds) + (diff.microseconds / 1000000.0)

                with map_lock:
                    # update source node in our mapping
                    Star_map[source_node] = [sent_map[source_node][0], RTT]

                    update_rtt_sum(Star_map, l_addr, l_port)

                    with hub_lock:
                        update_hub(Hub, Star_map)
