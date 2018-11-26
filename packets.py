import hashlib
import json
import logging
import datetime


class Packet(object):

    def __init__(self, payload, packet_type, s_addr, s_port, d_addr, d_port):
        self.payload = payload
        self.packet_type = packet_type
        self.s_addr = s_addr
        self.s_port = s_port
        self.d_addr = d_addr
        self.d_port = d_port
        self.checksum = hashlib.md5(payload.encode('utf-8')).hexdigest()
        self.timestamp = datetime.datetime.now()
        self.json = json.dumps({})

        # sets length based off of packet-type
        if packet_type == "FILE":
            self.length = 0  # TODO: get FILESIZE
        elif packet_type == "MSG":
            self.length = len(payload)
        else:
            self.length = 0  # TODO: decide if other packets need it (MAP???)

        # makes packet data into a json
        self.update_json()

    def __eq__(self, other):
        return self.length == other.length

    def __lt__(self, other):
        return self.length < other.length

    def __gt__(self, other):
        return self.length > other.length

    #######################
    # GETTERS AND SETTERS #
    #######################

    '''
    Return packet as a json string
    '''
    def get_as_string(self):
        return self.json

    '''
    Get timestamp
    '''
    def get_timestamp(self):
        return self.timestamp

    '''
    Get checksum
    '''
    def get_checksum(self):
        return self.checksum

    '''
    Set timestamp
    '''
    def set_timestamp(self, new_time):
        self.timestamp = new_time
        self.update_json()

    def update_json(self):
        self.json = json.dumps({
            "Header": {
                "Type": self.packet_type,
                "Checksum": self.checksum,
                "Length": self.length,
                "SourceAddr": self.s_addr,
                "SourcePort": self.s_port,
                "DestAddr": self.d_addr,
                "DestPort": self.d_port,
                "Timestamp": self.timestamp
            },
            "Payload": self.payload
        })


class FilePacket(Packet):

    def __init__(self, filename, s_addr, s_port, d_addr, d_port, isHub):
        file_max = 64000
        file = open(filename, "rb")
        data = file.read(file_max)
        # logger = logging.getLogger('node')
        # if file.read():
        #     logger.error("File-size of file {:s} is larger than 64KB.".format(filename))
        # else:
        payload = json.dumps({
            "Filename": filename,
            "Data": data.__repr__()
        })
        file.close()

        if isHub:
            super(FilePacket, self).__init__(payload, "FILE", s_addr, s_port, d_addr, d_port)
        else:
            super(FilePacket, self).__init__(payload, "FILE_HUB", s_addr, s_port, d_addr, d_port)


def json_to_packet(json_string):
    packet_json = json.loads(json_string)
    return Packet(packet_json["Payload"], packet_json["Header"]["Type"], packet_json["Header"]["SourceAddr"],
                  packet_json["Header"]["SourcePort"], packet_json["Header"]["DestAddr"],
                  packet_json["Header"]["DestPort"])
