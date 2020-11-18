import bpy

class CDTRKProps(bpy.types.PropertyGroup):
    author_name     : bpy.props.StringProperty (
        name        = 'Author',
        default     = 'wurunduk :)'
    )

    comment         : bpy.props.StringProperty (
        name        = 'Comment',
        default     = ''
    )

    style           : bpy.props.IntProperty (
        name        = 'Style',
        default     = 0
    )    

    ambience        : bpy.props.StringProperty (
        name        = 'Ambience',
        default     = ''
    )

    scenery         : bpy.props.IntProperty (
        name        = 'Scenery',
        default     = 0
    )

    width           : bpy.props.IntProperty (
        name        = 'Width',
        default     = 5
    )

    height          : bpy.props.IntProperty (
        name        = 'Height',
        default     = 5
    )

    def register():
        bpy.types.Scene.cdtrk = bpy.props.PointerProperty(type=CDTRKProps)