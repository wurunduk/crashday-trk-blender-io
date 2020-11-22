import bpy

class CDTRKProps(bpy.types.PropertyGroup):
    author          : bpy.props.StringProperty (
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

class CDTRKGridProps(bpy.types.PropertyGroup):
    enabled         : bpy.props.BoolProperty (
        name        = 'enabled',
        default     = True
    )

    color           : bpy.props.FloatVectorProperty (
        name        = 'color',
        subtype     = 'COLOR',
        default     = (0.28, 0.56, 0.06, 1.0),
        size        = 4,
        min         = 0.0, 
        max         = 1.0
    )

    def register():
        bpy.types.Scene.cdtrk_grid = bpy.props.PointerProperty(type=CDTRKGridProps)