import bpy, bmesh
from bpy import context
from  mathutils import Vector
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

def export_trk(operator, context, filepath='',
                use_selection=True,
                use_mesh_modifiers=True):

    work_path = '\\'.join(filepath.split('\\')[0:-1])
    print('\nExporting trk to {}'.format(filepath))

    # enter object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

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
            
    #bpy.ops.object.select_all(action='DESELECT')

    #bpy.ops.ed.undo()
    return