import bpy


def scene_setup(context: bpy.types.Context):
    scene = context.scene

    scene.render.fps = 100
    scene.render.frame_map_old = 100
    scene.render.frame_map_new = 100

    context.space_data.clip_start = 1
    context.space_data.clip_end = 10000
    scene.unit_settings.scale_length = 0.01

    return {'FINISHED'}


from bpy.types import Operator


class SceneSetup(Operator):
    """Setup Blender scene to match with Lost Saga scene"""
    bl_idname = "io3d.scene_setup" 
    bl_label = "Setup scene to match Lost Saga scene"

    def execute(self, context):
        return scene_setup(context)

def register():
    bpy.utils.register_class(SceneSetup)

def unregister():
    bpy.utils.unregister_class(SceneSetup)
