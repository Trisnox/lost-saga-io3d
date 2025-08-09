from bpy.types import Operator
from ..core.classes.mesh import TOON_SHADER_INDEX
import bpy


def to_transparent(context: bpy.types.Context):
    object = context.active_object
    material = object.active_material
    toon_shader_node = material.node_tree.nodes['Toon Shader']
    toon_shader_node.inputs[TOON_SHADER_INDEX['opacity']].default_value = 100
    toon_shader_node.inputs[TOON_SHADER_INDEX['is transparent']].default_value = True

    return


class ToTransparent(Operator):
    """Turn material Transparent"""
    bl_idname = "io3d.to_transparent"
    bl_label = "Turn material transparent, black color will be used for transparency (only for losa shader)"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        to_transparent(context)
        self.report({'INFO'}, 'Successfully set material into transparent')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ToTransparent)


def unregister():
    bpy.utils.unregister_class(ToTransparent)
