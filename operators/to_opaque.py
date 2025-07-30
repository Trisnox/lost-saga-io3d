from bpy.types import Operator
from ..core.classes.mesh import TOON_SHADER_INDEX
import bpy


def to_opaque(context: bpy.types.Context):
    object = context.active_object
    material = object.active_material
    toon_shader_node = material.node_tree.nodes['Toon Shader']
    toon_shader_node.inputs[TOON_SHADER_INDEX['opacity']].default_value = 0
    toon_shader_node.inputs[TOON_SHADER_INDEX['invert opacity']].default_value = False
    toon_shader_node.inputs[TOON_SHADER_INDEX['is transparent']].default_value = False

    return {'FINISHED'}


class ToOpaque(Operator):
    """Turn material opaque"""
    bl_idname = "io3d.to_opaque"
    bl_label = "Turn material opaque (only for losa shader)"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        return to_opaque(context)


def register():
    bpy.utils.register_class(ToOpaque)


def unregister():
    bpy.utils.unregister_class(ToOpaque)
