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

from . import export_trk

if "bpy" in locals():
    import importlib
    importlib.reload(export_trk)

class EXPORT_OT_cdtrk(bpy.types.Operator, ExportHelper):
    bl_idname       = 'export_scene.cdtrk'
    bl_label        = 'Export TRK'
    bl_description  = 'Export Crashday RE .trk map'
    bl_options      = {'UNDO'}

    filename_ext    = '.trk'
    filter_glob     : StringProperty(default='*.trk',
                                     options={'HIDDEN'})

    # use_selection   : BoolProperty(
    #     name        = "Selection Only",
    #     description = "Export selected objects only",
    #     default     = False
    # )

    use_mesh_modifiers: BoolProperty(
        name        = "Apply Mesh Modifiers",
        description = "Apply modifiers",
        default     = False
    )

    def execute(self, context):
        keywords = self.as_keywords(ignore=('filter_glob',
                                            "check_existing",))

        export_trk.export_trk(self, context, **keywords)

        return {'FINISHED'}