import bpy

class SCENE_PT_cdtrk(bpy.types.Panel):
    bl_idname       = 'SCENE_PT_cdtrk'
    bl_label        = 'CDRE - Track'
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