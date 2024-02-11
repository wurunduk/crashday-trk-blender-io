import bpy, bmesh, os
import mathutils
import base64
import time
from bpy import context
from mathutils import Vector
from ..crashday import cfl, trk

if 'bpy' in locals():
    import importlib
    importlib.reload(trk)
    importlib.reload(cfl)

def error_no_cdp3d(self, context):
    self.layout.label(text='You need to install cdp3d plugin to export trk maps!!')

# cutting
# https://blender.stackexchange.com/questions/80460/slice-up-terrain-mesh-into-chunks/133258

def new_object(bm, original_ob, new_name):
    me = bpy.data.meshes.new(new_name)
    bm.to_mesh(me)

    ob = bpy.data.objects.new(new_name, me)

    ob.data.materials.clear() # ensure the target material slots are clean
    for mat in original_ob.data.materials:
        ob.data.materials.append(mat)
    return ob

def slice(bisect_outer, original_ob, start, end, segments, new_objects):
    def geom(bm):
        return bm.verts[:] + bm.edges[:] + bm.faces[:]

    planes = [start.lerp(end, f / segments) for f in range(1, segments)]
    plane_normal = (end - start).normalized()

    for i, p in enumerate(planes):
        bisect_inner = bisect_outer.copy()

        bmesh.ops.bisect_plane(bisect_outer,geom=geom(bisect_outer),
                plane_co=p, plane_no=plane_normal, clear_inner=True)

        bmesh.ops.bisect_plane(bisect_inner,geom=geom(bisect_inner),
                plane_co=p, plane_no=plane_normal, clear_outer=True)

        if len(geom(bisect_inner)) > 0:
            new_objects.append(new_object(bisect_inner, original_ob, original_ob.name + '_' + str(i)))
        bisect_inner.free()
    bisect_outer.free()

def create_folders(filepath):
    def dir(filepath):
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

    dir(filepath + '//content//models//')
    dir(filepath + '//content//tiles//')
    dir(filepath + '//content//textures//')

def get_grid_position_by_world_pos(pos):
    def clamp(num, min_value, max_value):
        return max(min(num, max_value), min_value)

    trk_width = bpy.context.scene.cdtrk.width
    trk_height = bpy.context.scene.cdtrk.height

    # get float positions on the map
    x = clamp(pos[0], -(trk_width/2.0)*20, (trk_width/2.0)*20)
    y = clamp(pos[1], -(trk_height/2.0)*20, (trk_height/2.0)*20)

    # round to grid positions
    int_x = int((x + (trk_width/2.0)*20)/20)
    if int_x == trk_width:
        int_x -=1
    int_y = int((y + (trk_height/2.0)*20)/20)
    if int_y == trk_height:
        int_y -=1

    return [int_x, int_y]

def slice_objects(context, tiles_dict, use_selection=False):
    col = bpy.context.scene.collection

    trk_width = context.scene.cdtrk.width
    trk_height = context.scene.cdtrk.height

    def move_origin_to_tile_position(ob, tile_position):
        new_origin = Vector(((tile_position[0] - trk_width/2)*20 + 10,
                            (tile_position[1] - trk_height/2)*20 + 10,
                            0.0)) - ob.location
        ob.data.transform(mathutils.Matrix.Translation(-new_origin))
        ob.matrix_world.translation += new_origin

    time_start = time.time()
    print('-slice start-')

    objects = []
    for ob in col.all_objects:
         if ob.visible_get():
            if not use_selection:
                # apply modifiers if needed and store object
                objects.append(ob)
            elif ob.select_get():
                objects.append(ob)

    print('Got {} scene objects'.format(len(objects)))

    o = Vector((-(trk_width/2.0)*20, (trk_height/2.0)*20, 0.0))
    x = Vector(( (trk_width/2.0)*20, (trk_height/2.0)*20, 0.0))
    y = Vector((-(trk_width/2.0)*20, -(trk_height/2.0)*20, 0.0))

    total_vertical_slice_objects = []

    for ob in objects:
        if ob.type == 'MESH':
            bm = bmesh.new()
            me = ob.data
            bm.from_mesh(me)

            vertical_slices = []

            tile_objects = []

            slice(bm, ob, o - ob.location, x - ob.location, trk_width, vertical_slices)
            for nob in vertical_slices:
                nbm = bmesh.new()
                nbm.from_mesh(nob.data)
                slice(nbm, nob, o - nob.location, y - nob.location, trk_height, tile_objects)
                nbm.free()

            bm.free()

            print('{:.2f}\t sliced object: {}\n -> split into {} meshes'.format(
                time.time() - time_start, ob.name, len(tile_objects)))
            print(' - {}'.format(ob.matrix_world))
            for b in tile_objects:
                # without this checks it somehow threw an error that the object was already in the collection
                # maybe it was the same as the orginal, check this TODO
                if b not in ob.users_collection[0].objects.keys():
                    ob.users_collection[0].objects.link(b)

                local_bbox_center = 0.125 * sum((Vector(bv) for bv in b.bound_box), Vector())
                global_bbox_center = b.matrix_world @ local_bbox_center

                pos = get_grid_position_by_world_pos(global_bbox_center)

                if (pos[0], pos[1]) not in tiles_dict:
                    tiles_dict[(pos[0], pos[1])] = []
                tiles_dict[(pos[0], pos[1])].append(b)

                move_origin_to_tile_position(b, pos)

                print(' {} --> assigned to tile {} {}'.format(b.name, pos[0], pos[1]))

            total_vertical_slice_objects.extend(vertical_slices)

        if ob.type == 'LIGHT':

            pos = get_grid_position_by_world_pos(ob.location)

            if (pos[0], pos[1]) not in tiles_dict:
                tiles_dict[(pos[0], pos[1])] = []
            tiles_dict[(pos[0], pos[1])].append(ob)

            print('Light {} assigned to tile {} {}'.format(ob.name, pos[0], pos[1]))

    print('Removing old and temp meshes')

    for ob in total_vertical_slice_objects:
        bpy.data.objects.remove(ob)
    for ob in objects:
        if ob.type == 'MESH':
            bpy.data.objects.remove(ob, do_unlink=True)

    print('-slice end-')

def create_void_tile_files(path, name):
    void_model = 'UDNEAqCTGz0AGi04oJMbPVRFWDkFAAABdHJhbnNwLnRnYQBMSUdIVFM5BQAAAABNRVNIRVM5BQAAAQBTVUJNRVNIOQUAAG1haW4ADwAAAAAAAAAAAAAAAAAAAKCTGz0AGi04oJMbPQAAAgAAAAAAAAAAAAAABACgk5s8AAAAAKCTmzygk5u8AAAAAKCTmzygk5s8AAAAAKCTm7ygk5u8AAAAAKCTm7wCAAMAAAAAAAAAgD8AAAAAgD8AAAAAAQAAAAAAAAAAAAMAAAAAAAAAgD8CAAAAgD8AAIA/AAAAAIA/AAAAAFVTRVI5BQAAAAAAAA=='

    # create and save .cfl
    c = cfl.CFL()
    c.tile_name = name
    c.model = name + '.p3d'

    file = open(path + '\\content\\tiles\\' + name, 'w')
    c.write(file)
    file.close()

    b64bytes = void_model.encode('ascii')
    model_bytes = base64.b64decode(b64bytes)
    file = open(path + '\\content\\models\\' + name + '.p3d', 'wb')
    file.write(model_bytes)
    file.close()

def get_tile_name(x, y):
    tile_name = str(x) + '_' + str(y)
    if len(tile_name) <= 5:
        tile_name = tile_name + 'x'*(5-len(tile_name))
    return tile_name

def export_cfl_files(work_path, context, checkpoints_list, tiles_dict):
    for pos in tiles_dict:
        tile_name = get_tile_name(pos[0], pos[1])
        c = cfl.CFL()
        c.tile_name = tile_name
        c.model = tile_name + '.p3d'
        c.can_respawn = 1

        if pos in checkpoints_list:
            c.is_checkpoint = 1
            c.checkpoint_area = (-8.5, 4, 8.5, 0)

        file = open(work_path + '\\content\\tiles\\' + tile_name, 'w')
        c.write(file)
        file.close()

def export_p3d_files(work_path, use_mesh_modifiers, context, tiles_dict):
    # export model of this tile
    for pos in tiles_dict:
        tile_name = get_tile_name(pos[0], pos[1])

        bpy.ops.object.select_all(action='DESELECT')

        for ob in tiles_dict[pos]:
            ob.select_set(True)

        try:
            bpy.ops.export_scene.cdp3d(filepath=work_path + '\\content\\models\\' + tile_name + '.p3d',
            use_selection=True, use_mesh_modifiers=use_mesh_modifiers, use_empty_for_floor_level=True,
            bbox_mode='ALL', force_main_mesh=True)
        except AttributeError:
            bpy.context.window_manager.popup_menu(error_no_cdp3d, title='No p3d plugin found!', icon='ERROR')

def export_trk_file(work_path, file_path, context, tiles_dict):
    print('Started building trk file')
    track           = trk.Track()
    track.author    = context.scene.cdtrk.author
    track.comment   = context.scene.cdtrk.comment
    track.style     = context.scene.cdtrk.style
    track.ambience  = context.scene.cdtrk.ambience
    track.scenery   = int(context.scene.cdtrk.scenery)
    track.width     = context.scene.cdtrk.width
    track.height    = context.scene.cdtrk.height

    track.field_files = []
    track.track_tiles = []

    # hardcoded start position for now, in tiles
    start_position = [int(track.width/2), int(track.height/2)]

    empty_tile_name = 'wvoid'

    # fill tile list data
    for pos in tiles_dict:
        tile_name = get_tile_name(pos[0], pos[1])
        track.field_files.append(tile_name)

    empty_index = -1

    for y in range(track.height):
        for x in range(track.width):
            tt = trk.TrackTile()
            tile_name = get_tile_name(x, y)

            # check if there was an empty tile
            if (x, y) not in tiles_dict:
                # check if there was no empty tiles bofore
                if empty_index == -1:
                    # create a new empty tile if none, and save the index
                    track.field_files.append(empty_tile_name)
                    empty_index = len(track.field_files) - 1
                    create_void_tile_files(work_path, empty_tile_name)

                tt.field_id = empty_index
            else:
                # non empty tile, just add to the list
                tt.field_id = track.field_files.index(tile_name)

            track.track_tiles.append(tt)

    track.field_files_num = len(track.field_files)

    track.checkpoints_num = 1
    track.checkpoints = [start_position[0] + (track.height - 1 - start_position[1])*20]

    track.heightmap = []
    for i in range(track.width*track.height*16 + (track.width + track.height)*4 + 1):
        track.heightmap.append(0.0)

    print('Finished building .trk')

    file = open(file_path, 'wb')
    track.write(file)
    file.close()

def export_trk(operator, context, filepath='',
                use_selection=False,
                use_mesh_modifiers=False):

    work_path = '\\'.join(filepath.split('\\')[0:-1])
    print('\nExporting trk to {}'.format(filepath))

    create_folders(work_path)

    # enter object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    tiles_dict = {}

    #slice objects with tile grid
    slice_objects(context, tiles_dict, use_selection)

    # TODO: check if floor_level exists
    obj = bpy.data.objects.new('floor_level', None)
    bpy.context.scene.collection.objects.link(obj)

    obj.location = (0.0,0.0,0.0)
    obj.empty_display_type = 'PLAIN_AXES'

    h = context.scene.cdtrk.height
    w = context.scene.cdtrk.width

    cp_pos = (int(w/2), int(h/2))

    export_trk_file(work_path, filepath, context, tiles_dict)
    export_cfl_files(work_path, context, [cp_pos], tiles_dict)
    export_p3d_files(work_path, use_mesh_modifiers, context, tiles_dict)

    print('Finished exporting .trk')

    #bpy.ops.object.select_all(action='DESELECT')
    #bpy.ops.ed.undo()
    return