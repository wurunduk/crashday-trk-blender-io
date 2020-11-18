import bpy

from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

class EXPORT_OT_cdtrk(bpy.types.Operator, ExportHelper):
    bl_idname       = 'export_scene.cdtrk'
    bl_label        = 'Export TRK'
    bl_description  = 'Export Crashday RE .trk map'

    filename_ext    = '.trk'
    filter_globals  : StringProperty(default='*.trk',
                                        options={'HIDDEN'})

    def execute(self, context):
        return {'FINISHED'}