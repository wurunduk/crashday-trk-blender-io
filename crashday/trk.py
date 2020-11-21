import struct

def rf(file, format):
    answer = struct.unpack(format, file.read(struct.calcsize(format)))
    return answer[0] if len(answer) == 1 else answer

def rf_str(file):
    string = b''
    while True:
        char = struct.unpack('<c', file.read(1))[0]
        if char == b'\x00':
            break
        string += char
    return str(string, 'utf-8', 'replace')

def wf(file, format, *args):
    file.write(struct.pack(format, *args))

def wf_str(file, st):
    wf(file, '<%ds' % (len(st)+1), st.encode('ASCII', 'replace'))

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
        (self.field_id,
        self.rotation,
        self.is_mirrored,
        self.height,
        ) = rf(file, '<H3B')

    def write(self, file):
        wf(file, '<H3B', self.field_id, 
        self.rotation, self.is_mirrored, self.height)

class DynamicObject:
    def __init__(self):
        self.object_id = 0
        self.position = [0.0,0.0,0.0]
        self.rotation = 0

    def __str__(self):
        formated_pos = ['{0:0.2f}'.format(i) for i in self.position]
        return 'dynamic: {}, pos: {}, rotation: {}'.format(self.object_id, formated_pos, self.rotation)

    def read(self, file):
        (self.object_id,
        self.position[0], self.position[2], self.position[1],
        self.rotation) = rf(file, '<H4f')

    def write(self, file):
        wf(file, '<H4f', self.object_id,
        self.position[0], self.position[2], self.position[1], self.rotation)

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
            return rf(file, format)

        def r_str():
            return rf_str(file)

        # CDTRK or CDTR2 signature
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

        self.style = r('<B')
        self.ambience = r_str()
        self.field_files_num = r('<H')
        
        for i in range(self.field_files_num):
            self.field_files.append(r_str())

        self.width, self.height = r('<HH')
        for i in range(self.width*self.height):
            tile = TrackTile()
            tile.read(file)
            self.track_tiles.append(tile)

        self.dyn_object_files_num = r('<H')
        for i in range(self.dyn_object_files_num):
            self.dyn_object_files.append(r_str())

        self.dyn_objects_num = r('<H')
        for i in range(self.dyn_objects_num):
            d = DynamicObject()
            d.read(file)
            self.dyn_objects.append(d)

        self.checkpoints_num = r('<H')
        for i in range(self.checkpoints_num):
            self.checkpoints.append(r('<H'))

        self.permission, self.ground_bumpyness, self.scenery = r('<BfB')

        for i in range(self.width*self.height*16 + (self.width + self.height)*4 + 1):
           self.heightmap.append(r('<f'))

    def write(self, file):
        def w(format, *args):
            wf(file, format, *args)

        def w_str(st):
            wf_str(file, st)

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

        for i in range(self.width*self.height*16 + (self.width + self.height)*4 + 1):
            w('<f', self.heightmap[i])

def test_load_trk(path):
    file = open(path, 'rb')
    trk = Track()
    trk.read(file)
    print(trk)
    file.close()

# test_load_trk('H:\\SteamLibrary\\steamapps\\common\\Crashday\\user\\SA_map2.trk')