import bpy
from .gui import gui
from .ops import ops
from .props import props

if 'bpy' in locals():
    import importlib
    importlib.reload(gui)
    importlib.reload(ops)
    importlib.reload(props)

bl_info = {
    'name': 'Crashday Track Exporter',
    'author': 'Wurunduk',
    'blender': (2, 83, 0),
    'location': 'File > Import-Export',
    'version': (1, 1, 0),
    'support': 'COMMUNITY',
    'category': 'Import-Export'}

classes = [
    ops.EXPORT_OT_cdtrk,
    gui.SCENE_PT_cdtrk,
    gui.VIEW3D_PT_view3d_cdtrkgrid,
    props.CDTRKProps,
    props.CDTRKGridProps
]

def menu_func_export(self, context):
    self.layout.operator(ops.EXPORT_OT_cdtrk.bl_idname, text='Crashday Track (.trk)')
    return

handle = None

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    global handle
    handle = bpy.types.SpaceView3D.draw_handler_add(
                ops.draw_callback, (), 'WINDOW', 'POST_VIEW')

def unregister():
    if handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_export)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()