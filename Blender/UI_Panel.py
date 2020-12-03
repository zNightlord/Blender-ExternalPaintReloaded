import os

import bpy
from bpy.types import Panel

from .Paint_Operators import *

### properties
bpy.types.Scene.blenderextpaint_autorefresh_runid = bpy.props.IntProperty(name="", description="", default=-8000)
bpy.types.Scene.blenderextpaint_autorefresh_active = bpy.props.BoolProperty(name="", description="",default=False)
bpy.types.Scene.blenderextpaint_autorefresh_pause_blender = bpy.props.FloatProperty(name="Pause Blender", description="How many seconds Blender waits between attempts to save/reload the image. Stop autorefresh before changing.", default=1)
bpy.types.Scene.blenderextpaint_autorefresh_pause_external = bpy.props.FloatProperty(name="Pause External", description="How many seconds external program waits between attempts to save/reload the image. Stop autorefresh before changing.", default=1, update=pause_external_helper)
bpy.types.Scene.blenderextpaint_export_uv = bpy.props.BoolProperty(name="Export UVs", description="Export UVs to external program", default=False, update=export_uv_helper)
bpy.types.Scene.blenderextpaint_place = bpy.props.BoolProperty(name="Place Image", description="Load image into active layer in external program", default=False, update=place_helper)

## INFO
def addonInfo():
    global version
    version = '0.2 - Blender 2.8x'
    global versionInfo
    versionInfo = "Working - GIMP"
    global scriptInfo
    scriptInfo = "Thành công nâng lên cho bản 2.8"
    
class IMAGEUI_PT_Paint(bpy.types.Panel):
    bl_label = "External Paint Reloaded "
    bl_idname = "IMAGEUI_PT_Paint"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_context = ".paint_common_2d"
    bl_category = "EPR"
    
    def draw(self, context):
        addonInfo()
        box = self.layout.box()
        box.label(text='Version : ' + version, icon='COLLAPSEMENU')
        box.label(text='Info : ' + versionInfo, icon='TEXTURE')
        box.label(text=scriptInfo)
        row = self.layout.row()
        col = self.layout.column()
        

        col.scale_y=2
        col.operator("image.blenderextpaint_autorefresh_status", text=IMAGE_OT_blenderextpaint_autorefresh_status.status, icon='QUESTION')

        box = self.layout.box()
        row = box.row(align=True)
        row.scale_y=1.7
        row.prop(context.scene, "blenderextpaint_export_uv", icon='MOD_UVPROJECT')
        row.prop(context.scene, "blenderextpaint_place", icon='IMAGE_PLANE')

        col = self.layout.column(align=True)
        col.scale_y=1.5
        row = col.row(align=True)
        row.operator("image.blenderextpaint_autorefresh_modal", text = "On", icon='BLENDER')
        row.operator("image.blenderextpaint_autorefresh_off", text = "Off", icon='QUIT')

        col = self.layout.column(align=True)
        col.scale_y=1.2
        col.scale_x=0.9
        row = col.row(align=True)
        row.operator("image.blenderextpaint_autorefresh_switch_mode", text = "Mode", icon = 'TPAINT_HLT')
        row.operator("image.blenderextpaint_autorefresh_save", text = "Save", icon='FILE_TICK')

        row = col.row(align=True)
        row.prop(context.scene, "blenderextpaint_autorefresh_pause_external")
        row.prop(context.scene, "blenderextpaint_autorefresh_pause_blender")


def register():
    bpy.utils.register_class(IMAGEUI_PT_blenderpaint)


def unregister():
    #properties
    del bpy.types.Scene.blenderextpaint_autorefresh_runid
    del bpy.types.Scene.blenderextpaint_autorefresh_active
    del bpy.types.Scene.blenderextpaint_autorefresh_pause_blender
    del bpy.types.Scene.blenderextpaint_autorefresh_pause_external
    del bpy.types.Scene.blenderextpaint_export_uv
    del bpy.types.Scene.blenderextpaint_place
    #classes
    bpy.utils.unregister_class(IMAGEUI_PT_blenderpaint)
