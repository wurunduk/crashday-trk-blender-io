import struct

class TrackTile:
    def __init__(self):
        self.field_id = 0
        self.rotation = 0
        self.is_mirrored = 0
        self.height = 0

    def __str__(self):
        return 'tile: {}, rot: {}, mirrored: {}, height: {:0.2f}'.format(
            self.field_id, self.rotation, self.is_mirrored, self.height
        )

    def read(self, file):
        data = struct.unpack('<H3B', file.read(struct.calcsize('<H3B')))
        self.field_id = data[0]
        self.rotation = data[1]
        self.is_mirrored = data[2]
        self.height = data[3]

    def write(self, file):
        data = struct.pack('<H3B', self.field_id, 
        self.rotation, self.is_mirrored, self.height)
        file.write(data)

class DynamicObject:
    def __init__(self):
        self.object_id = 0
        self.position = (0.0,0.0,0.0)
        self.rotation = 0

    def __str__(self):
        formated_pos = ['{0:0.2f}'.format(i) for i in self.position]
        return 'dynamic: {}, pos: {}, rotation: {}'.format(self.object_id, formated_pos, self.rotation)

    def read(self, file):
        data = struct.unpack('<H4f', file.read(struct.calcsize('<H4f')))
        self.object_id = data[0]
        self.position = (data[1], data[2], data[3])
        self.rotation = data[4]

    def write(self, file):
        data = struct.pack('<H4f', self.object_id,
        self.position[0], self.position[1], self.position[2], self.rotation)
        file.write(data)

class Track:
    def __init__(self):
        self.current_time = 0
        self.author = 'wurunduk'
        self.comment = ''

        self.style = 0
        self.ambience = 'morn.amb'

        self.field_files_num = 0
        self.field_files = []
        self.width = 0
        self.height = 0
        self.track_tiles = []

        self.dyn_object_files_num = 0
        self.dyn_object_files = []
        self.dyn_objects_num = 0
        self.dyn_objects = []

        self.checkpoints_num = 0
        self.checkpoints = []

        self.permission = 0
        self.ground_bumpyness = 0
        self.scenery = 0
        self.heightmap = []

    def __str__(self):
        print_tiles = False
        print_dynamics = False
        track_tiles_print = '\n'.join([str(s) for s in self.track_tiles]) if print_tiles else 'Tile printing disabled'
        dynamics_print = '\n'.join([str(d) for d in self.dyn_objects]) if print_dynamics else 'Dynamics printing disabled'
        s = '''time: {}\nauthor: {}\ncomment: {}\nstyle: {}\nambience: {}
permission: {}, scenery: {}, ground_bumpyness: {}
width: {}, height: {}
field files: {}\n{}
tiles: \n{}
dynamics files: {}\n{}
dynamics: {}\n{}
checkpoints: {}\n{}
        '''.format(self.current_time, self.author, self.comment, self.style, self.ambience,
        self.permission, self.scenery, self.ground_bumpyness,
        self.width, self.height,
        self.field_files_num, self.field_files,
        track_tiles_print,
        self.dyn_object_files_num, self.dyn_object_files,
        self.dyn_objects_num, dynamics_print,
        self.checkpoints_num, self.checkpoints)
        return s

    def read(self, file):
        def r(format):
            answer = struct.unpack('<' + format, file.read(struct.calcsize('<' + format)))
            return answer[0] if len(answer) == 1 else answer

        def r_str():
            string = b''
            while True:
                char = struct.unpack('<c', file.read(1))[0]
                if char == b'\x00':
                    break
                string += char
            return str(string, "utf-8", "replace")

        signature = file.read(5)

        if signature == b'CDTRK':
            print('Reading CD TRK version 1')
        elif signature == b'CDTR2':
            print('Reading CD TRK version 2')
        else:
            print('Unknown TRK version, cant read')
            return

        self.current_time = r('i')
        self.author = r_str()
        self.comment = r_str()

        # this block is unused by the game
        for i in range(20):
            r('i')
            r_str()

        self.style = r('B')
        self.ambience = r_str()
        self.field_files_num = r('H')
        
        for i in range(self.field_files_num):
            self.field_files.append(r_str())

        self.width, self.height = r('HH')

        for i in range(self.width*self.height):
            tile = TrackTile()
            tile.read(file)
            self.track_tiles.append(tile)

        self.dyn_object_files_num = r('H')
        for i in range(self.dyn_object_files_num):
            self.dyn_object_files.append(r_str())

        self.dyn_objects_num = r('H')
        for i in range(self.dyn_objects_num):
            d = DynamicObject()
            d.read(file)
            self.dyn_objects.append(d)

        self.checkpoints_num = r('H')
        for i in range(self.checkpoints_num):
            self.checkpoints.append(r('H'))

        self.permission, self.ground_bumpyness, self.scenery = r('BfB')

        for i in range(self.width*self.height*16 + 1):
           self.heightmap.append(r('f'))

    def write(self, file):
        def w(format, *args):
            file.write(struct.pack(format, *args))

        def w_str(st):
            w('<%ds' % (len(st)+1), st.encode("ASCII", "replace"))

        file.write(b'CDTRK')

        w('<i', self.current_time)
        w_str(self.author)
        w_str(self.comment)

        # this block is unused by the game
        for i in range(20):
            #int and a null terminated string
            file.write(b'\x00\x00\x00\x00\x00')

        w('<B', self.style)
        w_str(self.ambience)

        w('<H', self.field_files_num)
        for s in self.field_files:
            w_str(s)

        w('<HH', self.width, self.height)
        for tile in self.track_tiles:
            tile.write(file)

        w('<H', self.dyn_object_files_num)
        for df in self.dyn_object_files:
            w_str(df)

        w('<H', self.dyn_objects_num)
        for d in self.dyn_objects:
            d.write(file)

        w('<H', self.checkpoints_num)
        for c in self.checkpoints:
            w('<H', c)

        w('<BfB', self.permission, self.ground_bumpyness, self.scenery)

        for i in range(self.width*self.height*16 + 1):
            w('<f', self.heightmap[i])

import base64

file = open('H://SteamLibrary//steamapps//common//Crashday//user//mod_testing//de_dust2//wvoid.p3d', 'rb')
encode = base64.b64encode(file.read())
print(encode.decode('ascii'))

st = 'UDNEAqCTGz0AGi04oJMbPVRFWDkFAAABdHJhbnNwLnRnYQBMSUdIVFM5BQAAAABNRVNIRVM5BQAAAQBTVUJNRVNIOQUAAG1haW4ADwAAAAAAAAAAAAAAAAAAAKCTGz0AGi04oJMbPQAAAgAAAAAAAAAAAAAABACgk5s8AAAAAKCTmzygk5u8AAAAAKCTmzygk5s8AAAAAKCTm7ygk5u8AAAAAKCTm7wCAAMAAAAAAAAAgD8AAAAAgD8AAAAAAQAAAAAAAAAAAAMAAAAAAAAAgD8CAAAAgD8AAIA/AAAAAIA/AAAAAFVTRVI5BQAAAAAAAA=='
b64b = st.encode('ascii')
mb = base64.b64decode(b64b)
print(mb)
# t = Track()
# t.read(file)
# print(str(t))