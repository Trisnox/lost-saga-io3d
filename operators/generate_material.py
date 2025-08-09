import os
import bpy
from bpy.types import Operator

from ..core.classes.mesh import MeshType, TOON_SHADER_INDEX


def generate_material(context: bpy.types.Context, shader_type: int, is_skin: bool = False):
    file_dir = os.path.dirname(os.path.abspath(__file__))
    addon_directory = os.path.dirname(file_dir)
    blend_location = addon_directory + '/losa shader.blend'
    try:
        toon_shader_data = bpy.data.node_groups['Toon Shader']
    except KeyError:
        bpy.ops.wm.append(filename='NodeTree/Toon Shader', directory=blend_location)
        toon_shader_data = bpy.data.node_groups['Toon Shader']
    
    shader_type_keys = {
        0: 'Static',
        1: 'AnimateToonShade',
        2: 'LightMap',
        3: 'Animate'
        }
    
    mesh_type = shader_type_keys[shader_type]

    object = context.active_object
    material = bpy.data.materials.new(name=object.name)
    material['Shader Type'] = mesh_type
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

    if mesh_type == 'LightMap':
        target_node_name = 'LightMap Setup'

        if len(object.data.uv_layers) <= 1:
            object.data.uv_layers.new(name='LightMap')
        lightmap_uv = object.data.uv_layers[1].name
    elif is_skin:
        target_node_name = 'Skin Setup'
    else:
        target_node_name = 'Texture Setup'

    try:
        target_data = bpy.data.node_groups[target_node_name]
    except KeyError:
        bpy.ops.wm.append(filename=f'NodeTree/{target_node_name}', directory=blend_location)
        target_data = bpy.data.node_groups[target_node_name]

    target_node = material.node_tree.nodes.new('ShaderNodeGroup')
    target_node.node_tree = target_data
    if mesh_type == 'LightMap':
        target_node.location = (-850, 0)
    elif is_skin:
        target_node.location = (-750, 150)
    else:
        target_node.location = (-300, 250)

    context.view_layer.objects.active = object
    old_area = context.area.ui_type
    context.area.ui_type = 'ShaderNodeTree'
    for node in material.node_tree.nodes:
        node.select = False
    target_node.select = True
    material.node_tree.nodes.active = target_node
    bpy.ops.node.group_ungroup()
    context.area.ui_type = old_area

    if mesh_type == 'LightMap':
        uv_map_node = material.node_tree.nodes['UV Map']
        uv_map_node.uv_map = lightmap_uv

        color_mix_node = material.node_tree.nodes['Mix']
        links.new(color_mix_node.outputs['Result'], toon_shader_node.inputs[TOON_SHADER_INDEX['color/texture']])
    elif is_skin:
        color_mix_output = material.node_tree.nodes['Mix Output']
        links.new(color_mix_output.outputs['Result'], toon_shader_node.inputs[TOON_SHADER_INDEX['color/texture']])
    else:
        texture_node = material.node_tree.nodes['Diffuse Texture']
        links.new(texture_node.outputs['Color'], toon_shader_node.inputs[TOON_SHADER_INDEX['color/texture']])

    return {'FINISHED'}


class GenerateMaterial(Operator):
    """Generate material with toon shade"""
    bl_idname = "io3d.generate_material"
    bl_label = "Generate material with losa toon shader, which can be later exported"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.draw_menu, title="Choose Type", icon='SHADING_WIRE')
        return {'FINISHED'}

    def draw_menu(self, menu, context):
        layout = menu.layout
        
        layout.operator("io3d.generate_material_animation", text="Animation", icon='OUTLINER_OB_ARMATURE')
        layout.operator("io3d.generate_material_static", text="Static", icon='MESH_CUBE')
        layout.operator("io3d.generate_material_skin", text="Skin", icon='COLORSET_14_VEC')
        layout.operator("io3d.generate_material_lightmap", text="Lightmap", icon='OUTLINER_OB_LIGHTPROBE')
    
class GenerateStatic(Operator):
    """Generate Material with static setup. Use this setup if mesh contains UV and texture"""
    bl_idname = "io3d.generate_material_static"
    bl_label = "Generate material with static setup"

    def execute(self, context):
        return generate_material(context, 0)
    
class GenerateAnimation(Operator):
    """Generate Material with Animation setup. Use this setup if mesh contains UV, texture, and weights"""
    bl_idname = "io3d.generate_material_animation"
    bl_label = "Generate material with animation setup"

    def execute(self, context):
        return generate_material(context, 1)
    
class GenerateSkin(Operator):
    """Generate Material with static setup. Use this setup if mesh only contains UV, texture, weights, and if the mesh should adapt to skin color"""
    bl_idname = "io3d.generate_material_skin"
    bl_label = "Generate material with skin setup"

    def execute(self, context):
        return generate_material(context, 1, True)

class GenerateLightmap(Operator):
    """Generate Material with static setup. Use this setup if mesh only contains UV, lightmap UV, and texture"""
    bl_idname = "io3d.generate_material_lightmap"
    bl_label = "Generate material with lightmap setup"

    def execute(self, context):
        return generate_material(context, 2)

def register():
    bpy.utils.register_class(GenerateStatic)
    bpy.utils.register_class(GenerateAnimation)
    bpy.utils.register_class(GenerateSkin)
    bpy.utils.register_class(GenerateLightmap)
    bpy.utils.register_class(GenerateMaterial)


def unregister():
    bpy.utils.unregister_class(GenerateMaterial)
    bpy.utils.unregister_class(GenerateLightmap)
    bpy.utils.unregister_class(GenerateSkin)
    bpy.utils.unregister_class(GenerateAnimation)
    bpy.utils.unregister_class(GenerateStatic)
