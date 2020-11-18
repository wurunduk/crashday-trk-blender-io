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