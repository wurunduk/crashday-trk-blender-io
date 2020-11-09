import bpy

class MATERIAL_PT_p3d_materials(bpy.types.Panel):
    bl_idname      = "MATERIAL_PT_p3d_materials"
    bl_label       = "CDRE - Material"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "material"

    def draw(self, context):
        if not context.material or not context.material.cdp3d:
            return

        layout = self.layout
        settings = context.material.cdp3d

        layout.prop(settings, "material_name")
        layout.prop(settings, "material_type", text="Material Type")

class DATA_PT_p3d_lights(bpy.types.Panel):
    bl_idname      = "DATA_PT_p3d_lights"
    bl_label       = "CDRE - Light"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "data"

    def draw(self, context):
        if not context.light or not context.light.cdp3d:
            return
        
        layout = self.layout
        settings = context.light.cdp3d

        layout.prop(context.light, 'color')
        layout.prop(context.light, 'energy', text='Range')

        layout.prop(settings, 'corona')
        layout.prop(settings, 'lens_flares')
        layout.prop(settings, 'lightup_environment')

class CDP3DMaterialProps(bpy.types.PropertyGroup):
    material_name   : bpy.props.StringProperty (
        name        = 'Texture Name',
        default     = 'colwhite',
        description = 'Name of the .tga or .dds texture to be used'
    )

    material_type   : bpy.props.EnumProperty(
        name        = 'Material Type',
        items       = (
            ('FLAT', 'Flat', 'Flat shading'),
            ('FLAT_METAL', 'Flat Metal', 'Flat shading for metals?'),
            ('GOURAUD', 'Gouraud', 'Smooth shading'),
            ('GOURAUD_METAL', 'Gouraud Metal', 'Smooth shading for metals?'),
            ('GOURAUD_METAL_ENV', 'Gouraud Metal Env', 'Smooth shading for environment metals'),
            ('SHINING', 'Shining', 'Shining material. Used for glowing signs, makes colors shinier.')
        ),
        default     = 'GOURAUD'
    )

    def register():
        bpy.types.Material.cdp3d = bpy.props.PointerProperty(type=CDP3DMaterialProps)

class CDP3DLightProps(bpy.types.PropertyGroup):
    corona          : bpy.props.BoolProperty(
        name        = 'Enable Corona',
        default     = True,
        description = "Enable corona effect for this light"
    )

    lens_flares     : bpy.props.BoolProperty(
        name        = 'Enable Lens Flares',
        default     = True,
        description = "Enable lens flares for this light"
    )

    lightup_environment : bpy.props.BoolProperty(
        name        = 'Enable Environment Lighting',
        default     = True,
        description = "Should this lamp lightup environment (only works for tiles)"
    )

    def register():
        bpy.types.Light.cdp3d = bpy.props.PointerProperty(type=CDP3DLightProps)