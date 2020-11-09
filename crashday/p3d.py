from ..utils import binary_parser
from enum import Enum

def int_to_color(value):
    return (((value >> 16) & 255)/255.0, ((value >> 8) & 255)/255.0, (value & 255)/255.0)

def color_to_int(value):
    return int('%02x%02x%02x' % (int(value[0]*255), int(value[1]*255), int(value[2]*255)), 16)

class P3DTextureInfo:
    def __init__(self):
        self.texture_start = 0
        self.num_flat = 0
        self.num_flat_metal = 0
        self.num_gouraud = 0
        self.num_gouraud_metal = 0
        self.num_gouraud_metal_env = 0
        self.num_shining = 0

    def __str__(self):
        return 'tex info: {} {} {} {} {} {} {}'.format(
            self.texture_start, self.num_flat, self.num_flat_metal,
            self.num_gouraud, self.num_gouraud_metal, self.num_gouraud_metal_env,
            self.num_shining)

class P3DLight:
    def __init__(self):
        self.name = ''
        self.pos = [0.0, 0.0, 0.0]
        self.range = 1.0
        self.color = 255

        self.show_corona = True
        self.show_lens_flares = True
        self.lightup_environment = True

    def __str__(self):
        formated_pos = ['{0:0.2f}'.format(i) for i in self.pos]
        return '''{}\nrange: {:.2f}, color: {}\ncorona {}, flares {}, environment {}\npos: {}\n'''.format(
            self.name[0] if type(self.name) is tuple else self.name, 
            self.range, int_to_color(self.color), 
            self.show_corona, self.show_lens_flares, self.lightup_environment,
            formated_pos
        )

class P3DPolygon:
    def __init__(self):
        self.texture = ''
        self.material = 0

        self.p1 = 0
        self.u1 = 0.0
        self.v1 = 0.0

        self.p2 = 0
        self.u2 = 0.0
        self.v2 = 0.0

        self.p3 = 0
        self.u3 = 0.0
        self.v3 = 0.0

    def __str__(self):
        return str(self.__class__) + ': ' + str(self.__dict__)

class P3DMesh:
    def __init__(self):
        self.name = ''
        self.flags = 0
        self.pos = [0.0, 0.0, 0.0]

        self.length = 0.0
        self.height = 0.0
        self.depth = 0.0

        #this is not in the default p3d format
        self.materials_used = []

        self.texture_infos = []

        self.num_vertices = 0
        self.vertices = []

        self.num_polys = 0
        self.polys = []

    def __str__(self):
        formated_pos = ['{0:0.2f}'.format(i) for i in self.pos]
        return '''{}\nflags: {}, vertices: {}, polys: {}
pos: {}\nsize: {:.2f} {:.2f} {:.2f} \n'''.format(
            self.name[0] if type(self.name) is tuple else self.name, 
            self.flags, self.num_vertices, self.num_polys,
            formated_pos, 
            self.length, self.height, self.depth
        )

class P3D:
    def __init__(self):
        self.length = 0.0
        self.height = 0.0
        self.depth = 0.0

        self.num_textures = 0
        self.textures = []

        self.num_lights = 0
        self.lights = []

        self.num_meshes = 0
        self.meshes = []

        self.user_data_size = 0
        self.user_data = ''

    def __str__(self):
        print('\n{} textures:'.format(self.num_textures))
        for i in self.textures:
            print(i[0] if type(i) is tuple else i)

        print('\n{} lights:'.format(self.num_lights))
        for i in self.lights:
            print(i)
        
        print('\n{} meshes:'.format(self.num_meshes))
        for i in self.meshes:
            print(i)
        return 'model size: {:.2f} {:.2f} {:.2f}\n{} lights, {} meshes, {} textures\n'.format(self.length, self.height, self.depth, self.num_lights, self.num_meshes, self.num_textures)

    def load(self, file):
        file.read(4)
        self.length = read_float(file)
        self.height = read_float(file)
        self.depth = read_float(file)

        #texture list
        file.read(7)
        self.num_textures = read_byte(file)
        self.textures = []
        for i in range(self.num_textures):
            self.textures.append('')
            tex_name = read_null_string(file)
            if tex_name.endswith('.tga'):
                tex_name = tex_name[0:-4]
            self.textures[i] = tex_name

        #lights list
        file.read(10)
        self.num_lights = read_short(file)
        self.lights = []
        for i in range(self.num_lights):
            self.lights.append(P3DLight())
            self.lights[i].name = read_null_string(file)
            self.lights[i].pos = read_vector(file)
            self.lights[i].range = read_float(file)
            self.lights[i].color = read_int(file)

            self.lights[i].show_corona = read_byte(file)
            self.lights[i].show_lens_flares = read_byte(file)
            self.lights[i].lightup_environment = read_byte(file)

        #meshes list
        file.read(10)
        self.num_meshes = read_short(file)
        self.meshes = []
        for i in range(self.num_meshes):
            self.meshes.append(P3DMesh())
            #submesh
            file.read(11)
            self.meshes[i].name = read_null_string(file)

            self.meshes[i].flags = read_uint(file)
            self.meshes[i].pos = read_vector(file)

            self.meshes[i].length = read_float(file)
            self.meshes[i].height = read_float(file)
            self.meshes[i].depth = read_float(file)

            self.meshes[i].texture_infos = []
            for ti in range(self.num_textures):
                self.meshes[i].texture_infos.append(P3DTextureInfo())
                self.meshes[i].texture_infos[ti].texture_start = read_short(file)
                self.meshes[i].texture_infos[ti].num_flat = read_short(file)
                self.meshes[i].texture_infos[ti].num_flat_metal = read_short(file)
                self.meshes[i].texture_infos[ti].num_gouraud = read_short(file)
                self.meshes[i].texture_infos[ti].num_gouraud_metal = read_short(file)
                self.meshes[i].texture_infos[ti].num_gouraud_metal_env = read_short(file)
                self.meshes[i].texture_infos[ti].num_shining = read_short(file)

            self.meshes[i].num_vertices = read_short(file)
            self.meshes[i].vertices = []
            for v in range(self.meshes[i].num_vertices):
                self.meshes[i].vertices.append(read_vector(file))

            self.meshes[i].num_polys = read_short(file)
            self.meshes[i].polys = []
            for p in range(self.meshes[i].num_polys):
                self.meshes[i].polys.append(P3DPolygon())
                self.meshes[i].polys[p].p1 = read_short(file)
                self.meshes[i].polys[p].u1 = read_float(file)
                self.meshes[i].polys[p].v1 = 1.0 - read_float(file)

                self.meshes[i].polys[p].p3 = read_short(file)
                self.meshes[i].polys[p].u3 = read_float(file)
                self.meshes[i].polys[p].v3 = 1.0 - read_float(file)

                self.meshes[i].polys[p].p2 = read_short(file)
                self.meshes[i].polys[p].u2 = read_float(file)
                self.meshes[i].polys[p].v2 = 1.0 - read_float(file)

            #at this point we have read everything but we need to fill
            #texture and materials of every polygon from the packed data
            #of the p3d model
            self.meshes[i].materials_used = []
            for ji, j in enumerate(self.meshes[i].texture_infos):
                polys_in_tex = j.texture_start

                for n in range(j.num_flat):
                    if(('FLAT', self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append(('FLAT', self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = 'FLAT'
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_flat

                for n in range(j.num_flat_metal):
                    if(('FLAT_METAL', self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append(('FLAT_METAL', self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = 'FLAT_METAL'
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_flat_metal

                for n in range(j.num_gouraud):
                    if(('GOURAUD', self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append(('GOURAUD', self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = 'GOURAUD'
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_gouraud

                for n in range(j.num_gouraud_metal):
                    if(('GOURAUD_METAL', self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append(('GOURAUD_METAL', self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = 'GOURAUD_METAL'
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_gouraud_metal

                for n in range(j.num_gouraud_metal_env):
                    if(('GOURAUD_METAL_ENV', self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append(('GOURAUD_METAL_ENV', self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = 'GOURAUD_METAL_ENV'
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_gouraud_metal_env    

                for n in range(j.num_shining):
                    if(('SHINING', self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append(('SHINING', self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = 'SHINING'
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

        file.read(8)
        self.user_data_size = read_int(file)

    def save(self, file):
        write_string(file, b'P3D\x02')
        write_float(file, self.length)
        write_float(file, self.height)
        write_float(file, self.depth)

        #texture list
        write_string(file, b'TEX')
        write_uint(file, 1337)
        write_byte(file, self.num_textures)
        for i in range(self.num_textures):
            tn = self.textures[i] + '.tga'
            write_null_string(file, sanitise_string(tn.lower()))

        #lights list
        write_string(file, b'LIGHTS')
        write_uint(file, 1337)
        write_short(file, self.num_lights)
        for i in range(self.num_lights):
            write_null_string(file, sanitise_string(self.lights[i].name.lower()))
            write_vector(file, self.lights[i].pos)
            write_float(file, self.lights[i].range)
            write_int(file, self.lights[i].color)

            write_byte(file, self.lights[i].show_corona)
            write_byte(file, self.lights[i].show_lens_flares)
            write_byte(file, self.lights[i].lightup_environment)

        #meshes list
        write_string(file, b'MESHES')
        write_uint(file, 1337)
        write_short(file, self.num_meshes)
        for i in range(self.num_meshes):
            write_string(file, b'SUBMESH')
            write_uint(file, 1337)
            write_null_string(file, sanitise_string(self.meshes[i].name.lower()))

            write_uint(file, self.meshes[i].flags)
            write_vector(file, self.meshes[i].pos)

            write_float(file, self.meshes[i].length)
            write_float(file, self.meshes[i].height)
            write_float(file, self.meshes[i].depth)

            for ti in range(self.num_textures):
                write_short(file, self.meshes[i].texture_infos[ti].texture_start)
                write_short(file, self.meshes[i].texture_infos[ti].num_flat)
                write_short(file, self.meshes[i].texture_infos[ti].num_flat_metal)
                write_short(file, self.meshes[i].texture_infos[ti].num_gouraud)
                write_short(file, self.meshes[i].texture_infos[ti].num_gouraud_metal)
                write_short(file, self.meshes[i].texture_infos[ti].num_gouraud_metal_env)
                write_short(file, self.meshes[i].texture_infos[ti].num_shining)

            write_short(file, self.meshes[i].num_vertices)
            for v in range(self.meshes[i].num_vertices):
                write_vector(file, self.meshes[i].vertices[v])

            write_short(file, self.meshes[i].num_polys)
            for p in range(self.meshes[i].num_polys):
                write_short(file, self.meshes[i].polys[p].p1)
                write_float(file, self.meshes[i].polys[p].u1)
                write_float(file, 1.0 - self.meshes[i].polys[p].v1)

                write_short(file, self.meshes[i].polys[p].p3)
                write_float(file, self.meshes[i].polys[p].u3)
                write_float(file, 1.0 - self.meshes[i].polys[p].v3)

                write_short(file, self.meshes[i].polys[p].p2)
                write_float(file, self.meshes[i].polys[p].u2)
                write_float(file, 1.0 - self.meshes[i].polys[p].v2)


        write_string(file, b'USER')
        write_uint(file, 1337)
        write_int(file, 0)
            