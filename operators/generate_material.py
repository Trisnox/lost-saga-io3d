from bpy.types import Operator
from ..core.classes.mesh import TOON_SHADER_INDEX
import bpy
import os


def generate_material(context: bpy.types.Context):
    file_dir = os.path.dirname(os.path.abspath(__file__))
    addon_directory = os.path.dirname(file_dir)
    blend_location = addon_directory + '/losa shader.blend'
    try:
        toon_shader_data = bpy.data.node_groups['Toon Shader']
    except KeyError:
        bpy.ops.wm.append(filename='NodeTree/Toon Shader', directory=blend_location)
        toon_shader_data = bpy.data.node_groups['Toon Shader']
    
    object = context.active_object
    material = bpy.data.materials.new(name=object.name)
    material['Shader Type'] = 'AnimateToonShade'
    object.data.materials.append(material)
    material.use_nodes = True
    material.surface_render_method = 'DITHERED'
    principled = material.node_tree.nodes['Principled BSDF']
    material_output = material.node_tree.nodes['Material Output']

    material.node_tree.nodes.remove(principled)

    toon_shader_node = material.node_tree.nodes.new('ShaderNodeGroup')
    toon_shader_node.name = 'Toon Shader'
    toon_shader_node.node_tree = toon_shader_data
    toon_shader_node.location = (0, 300)
    toon_shader_node.width = 250

    links = material.node_tree.links
    links.new(toon_shader_node.outputs['Shader'], material_output.inputs['Surface'])

    outline_rgb_node = material.node_tree.nodes.new('ShaderNodeRGB')
    outline_rgb_node.name = 'Outline Color'
    outline_rgb_node.location = (300, 133)
    outline_rgb_node.outputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)

    outline_value_node = material.node_tree.nodes.new('ShaderNodeValue')
    outline_value_node.name = 'Outline Thickness'
    outline_value_node.location = (300, -100)
    outline_value_node.outputs['Value'].default_value = 1.45

    return {'FINISHED'}


class GenerateMaterial(Operator):
    """Generate material with toon shade"""
    bl_idname = "io3d.generate_material"
    bl_label = "Generate material with losa toon shader, which can be later exported"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        return generate_material(context)


def register():
    bpy.utils.register_class(GenerateMaterial)


def unregister():
    bpy.utils.unregister_class(GenerateMaterial)
