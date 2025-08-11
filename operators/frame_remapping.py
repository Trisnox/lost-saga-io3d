import bpy


def is_using_newer_version():
    return bpy.app.version >= (4, 4, 0)

def frame_remap_checks(context: bpy.types.Context):
    scene = context.scene

    if scene.render.frame_map_old == scene.render.frame_map_new:
        def draw(self, context):
            self.layout.label(text='Scene does not use time stretching')

        context.window_manager.popup_menu(draw, title='INFO', icon='INFO')
        return {'FINISHED'}
    
    fps = scene.render.fps
    new_fps = scene.render.frame_map_new
    old_fps = scene.render.frame_map_old
    mode = ''
    if old_fps < new_fps:
        mode = 'STRETCH'
    else:
        mode = 'SHRINK'
        
    return mode, old_fps, fps

def frame_remap(context: bpy.types.Context, mode: str, target_fps: int, fps: int):
    scene = context.scene
    scene.render.frame_map_old = 100
    scene.render.frame_map_new = 100

    for object in context.selected_objects:
        animation_data = object.animation_data
        if not animation_data:
            continue

        action = animation_data.action
        if is_using_newer_version:
            fcurves = action.layers[0].strips[0].channelbag(action.slots[0]).fcurves
        else:
            fcurves = action.fcurves

        for fcurve in fcurves:
            if mode == 'STRETCH':
                keyframe_iter = reversed(list(fcurve.keyframe_points))
            else:
                keyframe_iter = fcurve.keyframe_points

            for keyframe in keyframe_iter:
                frame, data = keyframe.co
                frame = (frame/target_fps) * 1000
                frame = int(round((frame/1000) * fps))
                keyframe.co = frame, data

    return {'FINISHED'}

from bpy.props import StringProperty, IntProperty
from bpy.types import Operator

class FrameRemapOps(Operator):
    """Checks if user attempting to shrink keyframes"""
    bl_idname = "io3d.frame_remap_ops"
    bl_label = "WARNING"
    bl_options = {'REGISTER', 'INTERNAL'}

    mode: StringProperty()
    target_fps: IntProperty()
    fps: IntProperty()

    def execute(self, context):
        return frame_remap(context, self.mode, self.target_fps, self.fps)
    
    def invoke(self, context, event):
        check = self.mode == 'SHRINK'
        
        if check:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text='Script has detected that you\'re attempting to ')
        col.label(text='shrink keyframes. This can lead to data loss, ')
        col.label(text='Are you sure you still want to remap keyframes?')

class FrameRemapping(Operator):
    """Remap frames if user uses time stretching"""
    bl_idname = "io3d.frame_remap" 
    bl_label = "Remap keyframes"

    @classmethod
    def poll(self, context):
        object = context.active_object
        if not object:
            return False

        return object.animation_data

    def execute(self, context):
        mode, target_fps, fps = frame_remap_checks(context)
        bpy.ops.io3d.frame_remap_ops('INVOKE_DEFAULT', mode=mode, target_fps=target_fps, fps=fps)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(FrameRemapping)
    bpy.utils.register_class(FrameRemapOps)

def unregister():
    bpy.utils.unregister_class(FrameRemapOps)
    bpy.utils.unregister_class(FrameRemapping)
