from bpy.types import Operator
import bpy
import os


def import_nodes(context: bpy.types.Context):
    file_dir = os.path.dirname(os.path.abspath(__file__))
    addon_directory = os.path.dirname(file_dir)
    blend_location = addon_directory + '/losa shader.blend'
    try:
        toon_shader_data = bpy.data.node_groups['Toon Shader']
    except KeyError:
        bpy.ops.wm.append(filename='NodeTree/Toon Shader', directory=blend_location)
        toon_shader_data = None

    try:
        skin_setup_data = bpy.data.node_groups['Skin Setup']
    except KeyError:
        bpy.ops.wm.append(filename='NodeTree/Skin Setup', directory=blend_location)
        skin_setup_data = None

    try:
        texture_setup_data = bpy.data.node_groups['Texture Setup']
    except KeyError:
        bpy.ops.wm.append(filename='NodeTree/Texture Setup', directory=blend_location)
        texture_setup_data = None

    try:
        lightmap_setup_data = bpy.data.node_groups['LightMap Setup']
    except KeyError:
        bpy.ops.wm.append(filename='NodeTree/LightMap Setup', directory=blend_location)
        lightmap_setup_data = None
    
    if all((toon_shader_data, skin_setup_data, texture_setup_data, lightmap_setup_data)):
        def draw(self, context):
            self.layout.label(text='Node group already imported')

        context.window_manager.popup_menu(draw, title='INFO', icon='INFO')

    return {'FINISHED'}


class ImportLosaNodes(Operator):
    """Import toon shader and node groups to quickly setup textures"""
    bl_idname = "io3d.import_nodes"
    bl_label = "Import node groups to current project file"

    def execute(self, context):
        return import_nodes(context)


def register():
    bpy.utils.register_class(ImportLosaNodes)


def unregister():
    bpy.utils.unregister_class(ImportLosaNodes)
