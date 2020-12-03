import os

import bpy
from mathutils import *

#from .UI_Panel import IMAGEUI_PT_Paint


### Helper things
##########################
#class that sets up files           
##########################
class AppFiles:
    sync_filepath = None
    pause_filepath = None
    mode_filepath = None
    uv_filepath = None
    place_filepath = None
    
    @classmethod
    def setup_files(cls, context):
        appdir = os.path.expanduser('~')+"/_blenderextpaint_autorefresh"
        try: os.mkdir(appdir)
        except: pass

        cls.sync_filepath = appdir+"/sync.txt"
        cls.pause_filepath = appdir+"/pause.txt"
        cls.mode_filepath = appdir+"/mode.txt"
        cls.uv_filepath = appdir+"/uv.png"
        cls.place_filepath = appdir+"/place.txt"

        #init sync file
        syncf=open(cls.sync_filepath, 'w')
        syncf.write("extpaint")
        syncf.close() 
        #init pause file
        pausef=open(cls.pause_filepath, 'w')
        pausef.write("{0:.2f}".format(context.scene.blenderextpaint_autorefresh_pause_external))
        pausef.close()
        #init mode file
        modef=open(cls.mode_filepath, 'w')
        modef.write(str(context.scene.blenderextpaint_autorefresh_runid)+"  extpaint_to_blender")
        modef.close()   
        #init place file
        placef=open(cls.place_filepath, 'w')
        placef.write("1") if context.scene.blenderextpaint_place else placef.write("-1")
        placef.close()
        
## Functions
        
# export UV as new layer
def export_uv_helper(self, context):
    appdir = os.path.expanduser('~')+"/_blenderextpaint_autorefresh"
    try: os.mkdir(appdir)
    except: pass
    AppFiles.uv_filepath = appdir+"/uv.png"
    if context.scene.blenderextpaint_export_uv:
        try: bpy.ops.uv.export_layout(filepath=AppFiles.uv_filepath, check_existing=False, size=(512, 512))
        except: pass
    return None

# placing image into layer
def place_helper(self, context):
    appdir = os.path.expanduser('~')+"/_blenderextpaint_autorefresh"
    try: os.mkdir(appdir)
    except: pass
    AppFiles.place_filepath = appdir+"/place.txt"
    try:
        placef=open(AppFiles.place_filepath, 'w')
        placef.write("1") if context.scene.blenderextpaint_place else placef.write("-1")
        placef.close()
    except: pass
    return None

# external paint pause
def pause_external_helper(self, context):
    try:
        pausef=open(AppFiles.pause_filepath, 'w')
        pausef.write("{0:.2f}".format(context.scene.blenderextpaint_autorefresh_pause_external))
        pausef.close()
    except:
        AppFiles.setup_files(context)
    return None

### Display Status

class IMAGE_OT_blenderextpaint_autorefresh_status(bpy.types.Operator):
    bl_idname = "image.blenderextpaint_autorefresh_status"
    bl_label = "Autorefresh_Status"
    bl_description = "Autorefresh status"
    bl_options = {'REGISTER', 'UNDO'}

    status = "Not active"

    @classmethod
    def poll(cls, context): return True
    def execute(self, context): return {'FINISHED'}

### Disable Auto Reload

class IMAGE_OT_blenderextpaint_autorefresh_off(bpy.types.Operator):
    bl_idname = "image.blenderextpaint_autorefresh_off"
    bl_label = "Autorefresh_Off"
    bl_description = "Stop autorefresh both in Blender and the external program"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        context.scene.blenderextpaint_autorefresh_active = False

        #update run id and mode file. setting a new run id causes external paint program to stop.
        context.scene.blenderextpaint_autorefresh_runid += 1
        if context.scene.blenderextpaint_autorefresh_runid >= 8000:
            context.scene.blenderextpaint_autorefresh_runid = -8000
        try:
            modef=open(AppFiles.mode_filepath, 'r')
            [runid_from_file, current_mode] = modef.readline().rstrip().split()
            modef.close()
            modef=open(AppFiles.mode_filepath, 'w')
            modef.write(str(context.scene.blenderextpaint_autorefresh_runid)+"  "+current_mode)
            modef.close()
        except:
            AppFiles.setup_files(context)
            return {'CANCELLED'}
        
        IMAGE_OT_blenderextpaint_autorefresh_status.status = "Not active"
        return {'FINISHED'}

### Auto Reload
class IMAGE_OT_blenderextpaint_autorefresh_modal(bpy.types.Operator):
    bl_idname = "image.blenderextpaint_autorefresh_modal"
    bl_label = "Autorefresher"
    bl_description = "Activate autorefresh in Blender. Autorefresh needs to be activated separately in the external paint program."
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        #make sure autorefresh is not already active
        if context.scene.blenderextpaint_autorefresh_active==True: return {'CANCELLED'}
        context.scene.blenderextpaint_autorefresh_active=True
        IMAGE_OT_blenderextpaint_autorefresh_status.status = "Active: external paint"
        #setup file paths, reset everything to default initial state (to make sure everything syncs up)
        AppFiles.setup_files(context)
        
        self._runid = context.scene.blenderextpaint_autorefresh_runid
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(context.scene.blenderextpaint_autorefresh_pause_blender, window=context.window)
        self._prev_time_duration = self._timer.time_duration #for timer identification (time_duration updates only when timer updates)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        #check if should stop
        if not context.scene.blenderextpaint_autorefresh_active:
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}

        if event.type=='TIMER' and self._prev_time_duration!=self._timer.time_duration:
            self._prev_time_duration = self._timer.time_duration #for timer identification

            try:
                error_happened = False
                modef=open(AppFiles.mode_filepath, 'r')
                [runid_from_file, current_mode] = modef.readline().rstrip().split()
                modef.close()
            except: error_happened = True
            if error_happened or int(runid_from_file)!=self._runid:
                context.window_manager.event_timer_remove(self._timer)
                return {'FINISHED'}
                
            ######################################
            #currently painting in external paint
            ######################################
            if current_mode == "extpaint_to_blender":
                IMAGE_OT_blenderextpaint_autorefresh_status.status = "Active: external paint"

                #sync with external paint program, check that it's not saving/reloading the image file
                syncf=open(AppFiles.sync_filepath, 'r')
                if syncf.readline().rstrip() != "blender":
                    syncf.close()
                    return {'PASS_THROUGH'}
                syncf.close()    

                try: bpy.ops.image.reload()
                except: pass

                #let external paint program go
                syncf=open(AppFiles.sync_filepath, 'w')
                syncf.write("extpaint")
                syncf.close()

            ###############################
            #currently painting in blender 
            ###############################
            else:
                IMAGE_OT_blenderextpaint_autorefresh_status.status = "Active: Blender paint"

                #sync with external paint program, check that it's saving/reloading the image file
                syncf=open(AppFiles.sync_filepath, 'r')
                if syncf.readline().rstrip() != "blender":
                    syncf.close()
                    return {'PASS_THROUGH'}
                syncf.close()

                #check if image was updated
                for area in bpy.context.screen.areas:
                    if area.type == 'IMAGE_EDITOR':
                        if not area.spaces[0].image.is_dirty: return {'PASS_THROUGH'}
                        else: break
                #save_dirty uses the user-defined compression setting for png's
                try: bpy.ops.image.save_dirty()
                except: pass
                #below prevents "blinking" in blender gui
                for areas in bpy.context.screen.areas: areas.tag_redraw()

                #let external paint program go
                syncf=open(AppFiles.sync_filepath, 'w')
                syncf.write("extpaint")
                syncf.close()
                
        return {'PASS_THROUGH'}

### Switch Modes
class IMAGE_OT_blenderextpaint_autorefresh_switch_mode(bpy.types.Operator):
    bl_idname = "image.blenderextpaint_autorefresh_switch_mode"
    bl_label = "Switch_Mode"
    bl_description = "Switch between external painting and Blender painting"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        #get current mode, switch it
        try:
            modef=open(AppFiles.mode_filepath, 'r')
            [runid_from_file, current_mode] = modef.readline().rstrip().split()
            modef.close()
        except:
            AppFiles.setup_files(context)
            return {'CANCELLED'}
        if current_mode=="extpaint_to_blender": new_mode="  blender_to_extpaint"
        else: new_mode="  extpaint_to_blender"
        modef=open(AppFiles.mode_filepath, 'w')
        modef.write(runid_from_file+new_mode)
        modef.close()

        #update status
        if context.scene.blenderextpaint_autorefresh_active:
            IMAGE_OT_blenderextpaint_autorefresh_status.status = "Active: external paint" if new_mode=="  extpaint_to_blender" else "Active: Blender paint"

        return {'FINISHED'}

### Save image and let external paint continue

class IMAGE_OT_blenderextpaint_autorefresh_save(bpy.types.Operator):
    bl_idname = "image.blenderextpaint_autorefresh_save"
    bl_label = "Autorefresh_save"
    bl_description = "Save the image using the most recent compression setting. Then let external program reload."
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):

        try: bpy.ops.image.save()
        except: pass
        #below prevents "blinking" in blender gui
        for areas in bpy.context.screen.areas: areas.tag_redraw()

        #let external paint program go
        syncf=open(AppFiles.sync_filepath, 'w')
        syncf.write("extpaint")
        syncf.close()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(IMAGE_OT_blenderextpaint_autorefresh_status)
    bpy.utils.register_class(IMAGE_OT_blenderextpaint_autorefresh_off)
    bpy.utils.register_class(IMAGE_OT_blenderextpaint_autorefresh_modal)
    bpy.utils.register_class(IMAGE_OT_blenderextpaint_autorefresh_switch_mode)
    bpy.utils.register_class(IMAGE_OT_blenderextpaint_autorefresh_save)


def unregister():
    bpy.utils.unregister_class(IMAGE_OT_blenderextpaint_autorefresh_status)
    bpy.utils.unregister_class(IMAGE_OT_blenderextpaint_autorefresh_off)
    bpy.utils.unregister_class(IMAGE_OT_blenderextpaint_autorefresh_modal)
    bpy.utils.unregister_class(IMAGE_OT_blenderextpaint_autorefresh_switch_mode)
    bpy.utils.unregister_class(IMAGE_OT_blenderextpaint_autorefresh_save)
