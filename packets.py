import hashlib
import json


class Packet(object):

    def __init__(self, payload, packet_type, s_addr, s_port, d_addr, d_port):
        self.payload = payload
        self.packet_type = packet_type
        self.s_addr = s_addr
        self.s_port = s_port
        self.d_addr = d_addr
        self.d_port = d_port
        self.checksum = hashlib.md5(payload.encode('utf-8')).hexdigest()

        # sets length based off of packet-type
        if packet_type == "FILE":
            self.length = 0  # TODO: get FILESIZE
        elif packet_type == "MSG":
            self.length = len(payload)
        else:
            self.length = 0  # TODO: decide if other packets need it (MAP???)

        # makes packet data into a json
        self.json = json.dumps({
            "Header": {
                "Type": self.packet_type,
                "Checksum": self.checksum,
                "Length": self.length,
                "SourceAddr": self.s_addr,
                "SourcePort": self.s_port,
                "DestAddr": self.d_addr,
                "DestPort": self.d_port
            },
            "Payload": self.payload
        })

    def __eq__(self, other):
        return self.length == other.length

    def __lt__(self, other):
        return self.length < other.length

    def __gt__(self, other):
        return self.length > other.length

    ###########
    # GETTERS #
    ###########

    '''
    Return packet as a json string
    '''
    def get_as_string(self):
        return self.json


class FilePacket(Packet):

    def __init__(self, filename, s_addr, s_port, d_addr, d_port):
        payload = filename  # TODO: SERIALIZE THIS
        super(FilePacket, self).__init__(payload, "FILE", s_addr, s_port, d_addr, d_port)


def json_to_packet(json_string):
    packet_json = json.loads(json_string)
    return Packet(packet_json["Payload"], packet_json["Header"]["Type"])
