import bpy, bmesh, os
from bpy import context
from mathutils import Vector
from ..crashday import cfl, trk
# https://blender.stackexchange.com/questions/80460/slice-up-terrain-mesh-into-chunks/133258
# bounding box helper methods

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

    objects = []
    for ob in col.all_objects:
         if ob.visible_get():
            if not use_selection:
                # apply modifiers if needed and store object
                objects.append(ob)
            elif ob.select_get():
                objects.append(ob)

    for ob in objects:
        if ob.type == 'MESH':
            print(ob.name)
            bm = bmesh.new()
            me = ob.data
            bm.from_mesh(me)

            o = Vector((-(trk_height/2.0)*40, (trk_width/2.0)*40, 0.0)) - ob.location
            x = Vector(( (trk_height/2.0)*40, (trk_width/2.0)*40, 0.0)) - ob.location
            y = Vector((-(trk_height/2.0)*40, -(trk_width/2.0)*40, 0.0)) - ob.location

            slice(bm, o, x, trk_height)
            slice(bm, o, y, trk_width)
            bm.to_mesh(me)

            ob.select_set(True)
            bpy.ops.mesh.separate(type='LOOSE')
            ob.select_set(False)

    export_col = bpy.data.collections.new('TRK Exported Tiles')
    bpy.context.scene.collection.children.link(export_col)

    for x in range(trk_width):
        for y in range(trk_height):
            tile_col = bpy.data.collections.new('Tile_' + str(x) + '_' + str(y))
            export_col.children.link(tile_col)

    objects = []
    for ob in col.all_objects:
         if ob.visible_get():
            if not use_selection:
                # apply modifiers if needed and store object
                objects.append(ob)
            elif ob.select_get():
                objects.append(ob)

    for ob in objects:
        local_bbox_center = 0.125 * sum((Vector(b) for b in ob.bound_box), Vector())
        global_bbox_center = ob.matrix_world @ local_bbox_center

        def clamp(num, min_value, max_value):
            return max(min(num, max_value), min_value)

        x = clamp(global_bbox_center[0], -(trk_height/2.0)*40, (trk_height/2.0)*40)
        y = clamp(global_bbox_center[1], -(trk_width/2.0)*40, (trk_width/2.0)*40)

        int_x = int((x + (trk_height/2.0)*40)/40)
        if int_x == trk_height:
            int_x -=1
        int_y = int((y + (trk_width/2.0)*40)/40)
        if int_y == trk_width:
            int_y -=1

        if int_x < 0 or int_x >= trk_height or int_y < 0 or int_y >= trk_width:
            print(ob.name, str(int_x), str(int_y), str(x), str(y), str(global_bbox_center))

        tile_col = bpy.data.collections.get('Tile_' + str(int_x) + '_' + str(int_y))
        if tile_col:
            ob.users_collection[0].objects.unlink(ob)
            tile_col.objects.link(ob)

def export_trk(operator, context, filepath='',
                use_selection=True,
                use_mesh_modifiers=True):

    work_path = '\\'.join(filepath.split('\\')[0:-1])
    print('\nExporting trk to {}'.format(filepath))

    create_folders(work_path)

    # enter object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
            
    slice_separate_objects(context, use_selection)

    track           = trk.Track()
    track.author    = context.scene.cdtrk.author
    track.comment   = context.scene.cdtrk.comment
    track.style     = context.scene.cdtrk.style
    track.ambience  = context.scene.cdtrk.ambience
    track.scenery   = context.scene.cdtrk.scenery
    track.width     = context.scene.cdtrk.width
    track.height    = context.scene.cdtrk.height

    track.field_files_num = track.width*track.height
    track.field_files = []
    track.track_tiles = []
    for x in range(track.width):
        for y in range(track.height):
            track.field_files.append('Tile_' + str(x) + '_' + str(y) + '.cfl')
            tt = trk.TrackTile()
            tt.field_id = x + y*track.width
            track.track_tiles.append(tt)

    track.heightmap = []
    for i in range(track.width*track.height*16 + 1):
        track.heightmap.append(1.0)
    
    file = open(filepath, 'wb')
    track.write(file)
    file.close()

    #bpy.ops.object.select_all(action='DESELECT')
    #bpy.ops.ed.undo()
    return