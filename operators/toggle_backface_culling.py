from bpy.types import Operator
import bpy


def toggle_backface_culling(context: bpy.types.Context):
    scene = context.scene
    backface_culling = scene.io3d_msh_props.backface_culling = not scene.io3d_msh_props.backface_culling
    for material in bpy.data.materials:
        if material.name.endswith('Outline'):
            continue
        material.use_backface_culling = backface_culling

    return {'FINISHED'}


class ToggleBackfaceCulling(Operator):
    """Toggle backface culling for all applicable material"""
    bl_idname = "io3d.toggle_backface_culling"
    bl_label = "Toggle Backface Culling for all applicable material"

    def execute(self, context):
        return toggle_backface_culling(context)


def register():
    bpy.utils.register_class(ToggleBackfaceCulling)


def unregister():
    bpy.utils.unregister_class(ToggleBackfaceCulling)
