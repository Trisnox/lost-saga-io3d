import bpy
from ....core.classes.mesh import TOON_SHADER_INDEX


def export_material(context: bpy.types.Context, filepath: str):
    data = []
    materials = []
    for object in sorted(context.selected_objects, key=lambda x: x.name):
        if not object.type == 'MESH':
            continue

        try:
            material = object.data.materials[0]
            toon_shader = material.node_tree.nodes['Toon Shader']
            materials.append((material, toon_shader, material['Shader Type']))
        except IndexError:
            pass

    for material, toon_shader, shader_type in materials:
        use_skin = False
        diffuse_color = str(tuple(round(x, 3) for x in tuple(toon_shader.inputs[TOON_SHADER_INDEX['diffuse blend']].default_value)[:3])).strip('()').replace(',', '')
        diffuse_color = 'diffuse ' + diffuse_color if diffuse_color != '0.0 0.0 0.0' else ''
        
        if toon_shader.inputs[TOON_SHADER_INDEX['ambient strength']].default_value > 0:
            ambient_color = 'ambient ' + str(tuple(round(x, 3) for x in tuple(toon_shader.inputs[TOON_SHADER_INDEX['ambient color']].default_value)[:3])).strip('()').replace(',', '')
        else:
            ambient_color = ''

        if toon_shader.inputs[TOON_SHADER_INDEX['emission strength']].default_value >= 100:
            if toon_shader.inputs[TOON_SHADER_INDEX['preserve color']].default_value:
                emissive_color = 'emissive 1.0 1.0 1.0'
            else:
                emissive_color = 'emissive ' + str(tuple(round(x, 3) for x in tuple(toon_shader.inputs[TOON_SHADER_INDEX['emission color']].default_value)[:3])).strip('()').replace(',', '')
        else:
            emissive_color = ''

        if toon_shader.inputs[TOON_SHADER_INDEX['is transparent']].default_value:
            scene_blend = 'scene_blend add src_alpha one'
        elif toon_shader.inputs[TOON_SHADER_INDEX['alpha']].is_linked:
            scene_blend = 'scene_blend add src_alpha inv_src_alpha'
        else:
            scene_blend = 'scene_blend add zero src_color'

        try:
            outline_color_node = material.node_tree.nodes['Outline Color']
            outline_thickness_node = material.node_tree.nodes['Outline Thickness']

            outline_color = 'custom_param OutLineColor colorvalue ' + str(tuple(round(x, 3) for x in tuple(outline_color_node.outputs['Color'].default_value)[:3])).strip('()').replace(',', '')
            outline_thickness = 'custom_param OutLineThickness float ' + str(round(outline_thickness_node.outputs['Value'].default_value, 3))
        except KeyError:
            outline_color = ''
            outline_thickness = ''

        try:
            texture_node = material.node_tree.nodes['Skin Texture']
            texture = 'texture ' + texture_node.image.name
            lightmap_texture = ''
            use_skin = True
        except KeyError:
            lightmap_texture = ''
            if any(shader_type in x for x in ('AnimateToonShade', 'Static', 'Animate')):
                texture_node = material.node_tree.nodes['Image Texture']
                texture = 'texture ' + texture_node.image.name
            elif shader_type == 'LightMap':
                texture_node = material.node_tree.nodes['Diffuse Texture']
                lightmap_texture_node = material.node_tree.nodes['LightMap Texture']
                texture = texture_node.image.name
                lightmap_texture = lightmap_texture_node.image.name
            else:
                # try doing it anyway, assuming it's unrecognizeable shader type, which likely use the regular texture setup
                shader_type = 'AnimateToonShade'
                texture_node = material.node_tree.nodes['Image Texture']
                texture = 'texture ' + texture_node.image.name

        data.append((shader_type, ambient_color, diffuse_color, emissive_color, scene_blend, outline_color, outline_thickness, texture, lightmap_texture, use_skin))

    text = ''
    for item in data:
        shader_type, ambient_color, diffuse_color, emissive_color, scene_blend, outline_color, outline_thickness, texture, lightmap_texture, use_skin = item
        if outline_color:
            outline_pass = f"""pass
		{{
			cull clockwise
			shader_group AnimateOutLine
			{outline_color}
			{outline_thickness}
			texture_unit
			{{
				color_blend selectarg2 texture diffuse
				alpha_blend selectarg2 texture diffuse
            }}
        }}"""
        else:
            outline_pass = ''

        newline = '\n    '
        text += f"""material
{{{newline + ambient_color if ambient_color else ''}{newline + diffuse_color if diffuse_color else ''}{newline + emissive_color if emissive_color else ''}
    technique
    {{"""
        
        if shader_type == 'AnimateToonShade' and not use_skin:
            text += f"""
        pass
		{{
			cull none
			shader_group AnimateToonShade
			shadow_cast true
			light_iterate true
			texture_unit
			{{
				use_light_texture true
				tex_address_mode clamp
				alpha_blend selectarg2 texture diffuse
			}}
			texture_unit
			{{
				{texture}
				tex_coord_set 1
				custom_value 1
				color_blend add current tfactor
				alpha_blend modulate current texture
			}}
		}}
		pass
		{{
			{scene_blend}
			depth_write false
			cull none
			lighting false
			shader_group Animate
			texture_unit
			{{
				{texture}
				custom_value 1
			}}
        }}
		{outline_pass}
    }}
}}
"""
        elif shader_type == 'AnimateToonShade' and use_skin:
            text += f"""
        pass
		{{
			shader_group AnimateToonShade
			shadow_cast true
			light_iterate true
			texture_unit
			{{
				use_light_texture true
				tex_address_mode clamp
				alpha_blend selectarg2 texture diffuse
			}}
			texture_unit
			{{
				{texture}
				tex_coord_set 1
				color_blend add current tfactor
				alpha_blend modulate current texture
			}}
		}}
		pass
		{{
			{scene_blend}
			depth_write false
			lighting false
			shader_group Animate
			texture_unit
			{{
				{texture}
				color_blend blend_texture_alpha texture tfactor
				alpha_blend selectarg1 diffuse diffuse
			}}
			texture_unit
			{{
				tex_coord_set 1
				color_blend modulate current diffuse
				alpha_blend selectarg1 diffuse current
			}}
		}}
		{outline_pass}
	}}
}}
"""
        elif shader_type == 'LightMap':
            text += f"""
		pass
		{{
			shader_group LightMap
			texture_unit
			{{
				{lightmap_texture}
				color_blend add texture diffuse
			}}
			texture_unit
			{{
				{texture}
				tex_coord_set 1
				filtering none
				color_blend modulate texture current
            }}
        }}
	}}
}}
"""
        elif shader_type == 'Static':
            text += f"""
        pass
		{{
			shader_group Static
			texture_unit
			{{
				{texture}
				filtering none
            }}
		}}
    }}
}}
"""
        elif shader_type == 'Animate':
            text += f"""
        pass
		{{
			{scene_blend}
			shader_group Animate
			texture_unit
			{{
				{texture}
			}}
		}}
        """ # You can insert animation after the texture

    with open(filepath, 'w+') as f:
        f.write(text)
    
    return {'FINISHED'}

from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper


class MatExport(Operator, ExportHelper):
    """Export Lost Saga Material (.txt)"""
    bl_idname = "io3d.material_export"
    bl_label = "Export Lost Saga Material (.txt)"

    filename_ext = ".txt"

    filter_glob: StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        return export_material(context, self.filepath)

def menu_func_export(self, context):
    self.layout.operator(MatExport.bl_idname, text="Lost Saga Material (.txt)", icon='MATERIAL')


def register():
    bpy.utils.register_class(MatExport)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(MatExport)
