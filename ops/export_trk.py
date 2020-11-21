import bpy, bmesh, os
import mathutils
import base64
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

def slice(bm, start, end, segments):
    if segments == 1:
        return
    def geom(bm):
        return bm.verts[:] + bm.edges[:] + bm.faces[:]
    planes = [start.lerp(end, f / segments) for f in range(1, segments)]

    plane_no = (end - start).normalized() 
    while planes: 
        p0 = planes.pop(0)                 
        ret = bmesh.ops.bisect_plane(bm, 
                geom=geom(bm),
                plane_co=p0, 
                plane_no=plane_no)
        bmesh.ops.split_edges(bm, 
                edges=[e for e in ret['geom_cut'] 
                if isinstance(e, bmesh.types.BMEdge)])

def create_folders(filepath):
    def dir(filepath):
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

    dir(filepath + '//content//models//')
    dir(filepath + '//content//tiles//')
    dir(filepath + '//content//textures//')

def slice_separate_objects(context, use_selection=False):
    # dg = bpy.context.evaluated_depsgraph_get()
    col = bpy.context.scene.collection

    trk_width = context.scene.cdtrk.width
    trk_height = context.scene.cdtrk.height

    print('-slice start-')

    objects = []
    for ob in col.all_objects:
         if ob.visible_get():
            if not use_selection:
                # apply modifiers if needed and store object
                objects.append(ob)
            elif ob.select_get():
                objects.append(ob)

    print('got {} scene objects'.format(len(objects)))

    for ob in objects:
        if ob.type == 'MESH':
            bm = bmesh.new()
            me = ob.data
            bm.from_mesh(me)

            o = Vector((-(trk_width/2.0)*20, (trk_height/2.0)*20, 0.0)) - ob.location
            x = Vector(( (trk_width/2.0)*20, (trk_height/2.0)*20, 0.0)) - ob.location
            y = Vector((-(trk_width/2.0)*20, -(trk_height/2.0)*20, 0.0)) - ob.location

            slice(bm, o, x, trk_width)
            slice(bm, o, y, trk_height)
            bm.to_mesh(me)

            print('done slicing mesh: {}'.format(ob.name))

            ob.select_set(True)
            bpy.ops.mesh.separate(type='LOOSE')
            ob.select_set(False)

            print('loose parts separated\n')

    print('-slice end-')

def separate_objects_into_collections(context, use_selection=False):
    print('-started collection separation-')

    # create collection for sliced meshes
    export_col = bpy.data.collections.get('TRK Exported Tiles')
    if export_col is None:
        export_col = bpy.data.collections.new('TRK Exported Tiles')
        bpy.context.scene.collection.children.link(export_col)

    col = bpy.context.scene.collection

    trk_width = context.scene.cdtrk.width
    trk_height = context.scene.cdtrk.height

    # get new list of sliced objects
    objects = []
    for ob in col.all_objects:
         if ob.visible_get():
            if not use_selection:
                # apply modifiers if needed and store object
                objects.append(ob)
            elif ob.select_get():
                objects.append(ob)

    print('got all objects again')

    def get_grid_position(pos):
        def clamp(num, min_value, max_value):
            return max(min(num, max_value), min_value)

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

        return (int_x, int_y)

    # sort every mesh into grid tile collection based on position
    for ob in objects:
        local_bbox_center = 0.125 * sum((Vector(b) for b in ob.bound_box), Vector())
        global_bbox_center = ob.matrix_world @ local_bbox_center

        pos = get_grid_position(global_bbox_center)
        
        # center object origin to tile grid center for correct export
        if ob.type == 'MESH':
            new_origin = Vector(((pos[0] - trk_width/2)*20 + 10, (pos[1] - trk_height/2)*20 + 10, 0.0)) - ob.location
            ob.data.transform(mathutils.Matrix.Translation(-new_origin))
            ob.matrix_world.translation += new_origin

        col_name = str(pos[0]) + '_' + str(pos[1])

        tile_col = bpy.data.collections.get(col_name)
        if tile_col is None:
            tile_col = bpy.data.collections.new(col_name)
            export_col.children.link(tile_col)

        ob.users_collection[0].objects.unlink(ob)
        tile_col.objects.link(ob)

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

def get_tile_name_and_collection(x, y):
    tile_name = str(x) + '_' + str(y)
    if len(tile_name) <= 4:
        tile_name = tile_name + 'x'*(4-len(tile_name))
    tile_col = bpy.data.collections.get(tile_name)
    return tile_name, tile_col

def export_cfl_files(work_path, height, width, checkpoints_list, context):
    for y in range(height):
        for x in range(width):
            tile_name, tile_col = get_tile_name_and_collection(x, y)
            if tile_col is not None:
                c = cfl.CFL()
                c.tile_name = tile_name
                c.model = tile_name + '.p3d'
                c.can_respawn = 1
            
                if (x, y) in checkpoints_list:
                    c.is_checkpoint = 1
                    c.checkpoint_area = (-8.5, 4, 8.5, 0)

                file = open(work_path + '\\content\\tiles\\' + tile_name, 'w')
                c.write(file)
                file.close()

def export_p3d_files(work_path, use_mesh_modifiers, height, width, context):
    # export model of this tile
    for y in range(height):
        for x in range(width):
            tile_name, tile_col = get_tile_name_and_collection(x, y)
            if tile_col is not None:
                bpy.ops.object.select_all(action='DESELECT')

                tile_col = bpy.data.collections.get(tile_name)
                if tile_col:
                    for ob in tile_col.all_objects:
                        ob.select_set(True)
                else:
                    print('FAILED TO GET COLLECTION. THIS IS BAD?')

                try:
                    bpy.ops.export_scene.cdp3d(filepath=work_path + '\\content\\models\\' + tile_name + '.p3d',
                    use_selection=True, use_mesh_modifiers=use_mesh_modifiers, use_empty_for_floor_level=True)
                except AttributeError:
                    bpy.context.window_manager.popup_menu(error_no_cdp3d, title='No p3d plugin found!', icon='ERROR')

def export_trk_file(work_path, file_path, context):
    print('Started building trk file')
    track           = trk.Track()
    track.author    = context.scene.cdtrk.author
    track.comment   = context.scene.cdtrk.comment
    track.style     = context.scene.cdtrk.style
    track.ambience  = context.scene.cdtrk.ambience
    track.scenery   = context.scene.cdtrk.scenery
    track.width     = context.scene.cdtrk.width
    track.height    = context.scene.cdtrk.height

    track.field_files = []
    track.track_tiles = []
    
    # hardcoded start position for now, in tiles
    start_position = [int(track.width/2), int(track.height/2)]

    empty_tile_name = 'wvoid'

    for y in range(track.height):
        for x in range(track.width):
            tile_name, tile_col = get_tile_name_and_collection(x, y)
            if tile_col is None:
                # this tile is empty, create a void tile if not present yet
                if empty_tile_name not in track.field_files:
                    track.field_files.append(empty_tile_name)
                    create_void_tile_files(work_path, empty_tile_name)
            else:
                track.field_files.append(tile_name)

    for y in range(track.height):
        for x in range(track.width):
            tt = trk.TrackTile()
            tile_name, tile_col = get_tile_name_and_collection(x, y)
            if tile_col is None:
                tt.field_id = track.field_files.index(empty_tile_name)
            else:
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
    track.close()

def export_trk(operator, context, file_path='',
                use_selection=False,
                use_mesh_modifiers=False):

    work_path = '\\'.join(file_path.split('\\')[0:-1])
    print('\nExporting trk to {}'.format(file_path))

    create_folders(work_path)

    # enter object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    
    #slice objects with tile grid
    slice_separate_objects(context, use_selection)

    # separate all sliced object into corresponding collections
    separate_objects_into_collections(context, use_selection=use_selection)

    # TODO: check if floor_level exists
    obj = bpy.data.objects.new('floor_level', None)
    bpy.context.scene.collection.objects.link(obj)

    obj.location = (0.0,0.0,0.0)
    obj.empty_display_type = 'PLAIN_AXES'

    h = context.scene.cdtrk.height
    w = context.scene.cdtrk.width

    cp_pos = (int(w/2), int(h/2))

    export_trk_file(work_path, file_path, context)
    export_cfl_files(work_path, h, w, [cp_pos],context)
    export_p3d_files(work_path, use_mesh_modifiers, h, w, context)

    print('Finished exporting .trk')

    #bpy.ops.object.select_all(action='DESELECT')
    #bpy.ops.ed.undo()
    return