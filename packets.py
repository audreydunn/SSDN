import hashlib
import json


class Packet(object):

    def __init__(self, payload, packet_type):
        self.payload = payload
        self.packet_type = packet_type
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
                "Length": self.length
            },
            "Payload": self.payload
        })

    ###########
    # GETTERS #
    ###########

    '''
    Return packet as a json string
    '''
    def get_as_string(self):
        return self.json


class FilePacket(Packet):

    def __init__(self, filename):
        payload = filename  # TODO: SERIALIZE THIS
        super(FilePacket, self).__init__(payload, "FILE")


def json_to_packet(json_string):
    packet_json = json.loads(json_string)
    return Packet(packet_json["Payload"], packet_json["Header"]["Type"])
