import bpy

class SCENE_PT_cdtrk(bpy.types.Panel):
    bl_idname       = 'SCENE_PT_cdtrk'
    bl_label        = 'Crashday - Track'
    bl_space_type   = 'PROPERTIES'
    bl_region_type  = 'WINDOW'
    bl_context      = 'scene'

    def draw(self, context):
        if not context.scene or not context.scene.cdtrk:
            return

        layout = self.layout
        settings = context.scene.cdtrk

        layout.prop(settings, 'author')
        layout.prop(settings, 'comment')
        layout.prop(settings, 'style')
        layout.prop(settings, 'ambience')
        layout.prop(settings, 'scenery')
        layout.prop(settings, 'width')
        layout.prop(settings, 'height')

class VIEW3D_PT_view3d_cdtrkgrid(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'View'
    bl_label = 'Crashday - Grid'

    def draw(self, context):
        layout = self.layout

        settings = context.scene.cdtrk_grid

        layout.prop(settings, 'enabled', text='Enabled')
        layout.prop(settings, 'color', text='Grid Color')