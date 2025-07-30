from bpy.types import Operator
from ..core.classes.mesh import TOON_SHADER_INDEX
import bpy


def toggle_shadeless(context: bpy.types.Context):
    object = context.active_object
    material = object.active_material
    toon_shader_node = material.node_tree.nodes['Toon Shader']
    if toon_shader_node.inputs[TOON_SHADER_INDEX['emission strength']].default_value >= 100:
        toon_shader_node.inputs[TOON_SHADER_INDEX['emission strength']].default_value = 0
    else:
        toon_shader_node.inputs[TOON_SHADER_INDEX['emission color']].default_value = (1.0, 1.0, 1.0, 1.0)
        toon_shader_node.inputs[TOON_SHADER_INDEX['emission strength']].default_value = 100
        toon_shader_node.inputs[TOON_SHADER_INDEX['preserve color']].default_value = True
    return {'FINISHED'}


class ToggleShadeless(Operator):
    """Toggle material shadeless"""
    bl_idname = "io3d.toggle_shadeless"
    bl_label = "Toggle material into shadeless or shaded (only for losa shader)"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        return toggle_shadeless(context)


def register():
    bpy.utils.register_class(ToggleShadeless)


def unregister():
    bpy.utils.unregister_class(ToggleShadeless)
