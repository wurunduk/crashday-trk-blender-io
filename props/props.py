import bpy

class CDTRKProps(bpy.types.PropertyGroup):
    author          : bpy.props.StringProperty (
        name        = 'Author',
        default     = 'Author'
    )

    comment         : bpy.props.StringProperty (
        name        = 'Comment',
        default     = 'Made with wurun\'s blender .trk exporter'
    )

    style           : bpy.props.IntProperty (
        name        = 'Style',
        description = 'Which modes this track is available in. Leave at 0 for all modes.',
        default     = 0,
        min         = 0,
        max         = 128
    )

    ambience        : bpy.props.StringProperty (
        name        = 'Ambience',
        description = 'Ambience file to be used by default. This field is overwritten by the in-game setting',
        default     = 'day.amb'
    )

    scenery         : bpy.props.EnumProperty (
        name        = 'Scenery',
        description = 'Background scenery used in game',
        items       = (
            ('0',     'Highlands', '', 0),
            ('1',     'The Alps', '', 1),
            ('2',     'Race Track', '', 2)
        ),
        default     = '0'
    )

    width           : bpy.props.IntProperty (
        name        = 'Width',
        default     = 5,
        min         = 3,
        max         = 90,
        soft_max    = 40
    )

    height          : bpy.props.IntProperty (
        name        = 'Height',
        default     = 5,
        min         = 3,
        max         = 90,
        soft_max    = 40
    )

    def register():
        bpy.types.Scene.cdtrk = bpy.props.PointerProperty(type=CDTRKProps)

class CDTRKGridProps(bpy.types.PropertyGroup):
    enabled         : bpy.props.BoolProperty (
        name        = 'Enabled',
        default     = True
    )

    color           : bpy.props.FloatVectorProperty (
        name        = 'Color',
        subtype     = 'COLOR',
        default     = (0.28, 0.56, 0.06, 1.0),
        size        = 4,
        min         = 0.0,
        max         = 1.0
    )

    def register():
        bpy.types.Scene.cdtrk_grid = bpy.props.PointerProperty(type=CDTRKGridProps)
