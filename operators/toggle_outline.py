from bpy.types import Operator
import bpy


def toggle_outline(context: bpy.types.Context):
    scene = context.scene
    outline_toggle = scene.io3d_msh_props.outline_active = not scene.io3d_msh_props.outline_active
    for object in bpy.data.objects:
        solidify_mod = object.modifiers.get('Losa Outline', None)
        if solidify_mod:
            solidify_mod.show_viewport = outline_toggle

    return {'FINISHED'}


class ToggleOutline(Operator):
    """Setup Blender scene to match with Lost Saga scene"""
    bl_idname = "io3d.toggle_outline"
    bl_label = "Toggle Transparency Overlap for all aplicable material"

    def execute(self, context):
        return toggle_outline(context)


def register():
    bpy.utils.register_class(ToggleOutline)


def unregister():
    bpy.utils.unregister_class(ToggleOutline)
