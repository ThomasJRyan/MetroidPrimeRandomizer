import re
from functools import reduce

import gciso
from MetroidFile import *

def bytes_to_int(bytes):
    return int(bytes.hex(), 16)

def bytes_to_array(bytes, size=4):
    return [bytes[i:i+size] for i in range(0, len(bytes), size)]

def break_up_bytes(bytes, sizes):
    old_size = 0
    for size in sizes:
        yield bytes[old_size:old_size+size]
        old_size += size

class SCLY_Object():
    def __init__(self, obj_type, size, instance_id, connection_count, connections, property_count, property_data):
        self.obj_type = obj_type
        self.size = size
        self.instance_id = instance_id
        self.connection_count = connection_count
        self.connections = connections
        self.property_count = property_count
        self.property_data = property_data
        if obj_type == 17:
            self.name = property_data.split(b'\x00')[0]
            self.item = bytes_to_int(property_data[len(self.name):][61:65])

class SCLY_Layer():
    def __init__(self, data):
        self.object_count = bytes_to_int(data[1:5])
        self.data = data
        self.scly_objects = [obj for obj in self.get_objects()]

    def get_objects(self):
        start = 5
        for i in range(self.object_count):
            obj_type = self.data[start]

            size = bytes_to_int(self.data[start+1:start+5])
            start += 5

            instance_id = self.data[start:start+4]
            start += 4

            connection_count = bytes_to_int(self.data[start:start+4])
            start += 4

            connections_size = 12*connection_count
            connections = bytes_to_array(self.data[start:start+connections_size], size=12)
            start += connections_size

            property_count = bytes_to_int(self.data[start:start+4])
            start += 4

            remaining_size = size - (connections_size + 17)
            property_data = self.data[start:start+size]
            start += remaining_size + 5

            yield SCLY_Object(
                obj_type,
                size,
                instance_id,
                connection_count,
                connections,
                property_count,
                property_data
            )

class SCLY():
    def __init__(self, pak, offset):
        self.offset = offset
        self.layer_count = bytes_to_int(pak[offset+8 : offset+12])

        self.header_size = 12 + (4*self.layer_count)
        self.layer_sizes = [bytes_to_int(group) for group in bytes_to_array(pak[offset+12 : offset+self.header_size], 4)]
        self.total_size =  + reduce(lambda x,y: x+y, self.layer_sizes)

        self.layer_data = pak[offset+self.header_size: offset+self.total_size+self.header_size]

        # print([len(data) for data in break_up_bytes(self.layer_data, self.layer_sizes)])
        # print(len(self.layer_data))
        self.scly_layers = [SCLY_Layer(data) for data in break_up_bytes(self.layer_data, self.layer_sizes)]

class Location():
    def __init__(self, offset):
        self.offset = offset

Locations = {

}

def get_objects_of_type(scly_list, obj_type):
    obj_list = list()
    for scly in scly_list:
        for layer in scly.scly_layers:
            for obj in layer.scly_objects:
                if obj.obj_type == obj_type and b'Small' not in obj.property_data and b'Large' not in obj.property_data and b'Powerbomb' not in obj.property_data and b'100 Health' not in obj.property_data:# and b'P_Missile_Launcher' not in obj.property_data:
                    # if b'Missile' in obj.property_data:
                    #     obj_list.append(obj)
                    obj_list.append(obj)
    return obj_list

if __name__ == '__main__':
    scly = list()

    iso = MetroidFile('./Metroid/MP_Editable.iso')

    iso.seekFile(b'Metroid4.pak')
    clean_data = iso.readBytes(20)
    clean_data = b'\x00\x03\x00\x05\x00\x00\x00\x00\x00\x00\x00\x01MLVL9\xf2\xde('
    print(clean_data)

    iso.seekFile(b'Metroid4.pak')
    data = b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'
    iso.writeBytes(data)

    iso.seekFile(b'Metroid4.pak')
    print(iso.readBytes(20))

    iso.seekFile(b'Metroid4.pak')
    iso.writeBytes(clean_data)

    iso.seekFile(b'Metroid4.pak')
    print(iso.readBytes(20))

    # metroid3 = iso.readFile(b'Metroid3.pak', offset=0)

    # pattern = re.compile(b'SCLY.{12}')

    # scly = list()

    # for m in pattern.finditer(metroid3):
    #     scly.append(SCLY(metroid3, m.span()[0]))

    # for fil in iso.listDir(b'/'):
    #     if b'.pak' not in fil:
    #         continue
    #     fil_data = iso.readFile(fil, offset=0)
    #     for m in pattern.finditer(fil_data):
    #         # print(m.span()[0])
    #         scly.append(SCLY(fil_data, m.span()[0]))
    #         # print(scly.layer_sizes)
    #         # print(scly.layer_count, len(scly.scly_layers), scly.layer_sizes, [scly.object_count for scly in scly.scly_layers])
    #         # print(scly.layer_sizes)
    #         # print(m.span()[0], m.group())
    #         # import pdb; pdb.set_trace()

    # obj_list = get_objects_of_type(scly, 17)