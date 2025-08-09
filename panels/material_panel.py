import bpy
import os
from ..core.classes.mesh import TOON_SHADER_INDEX

class MATERIAL_PANEL(bpy.types.Panel):
    bl_category = 'IO3D'
    bl_idname = 'OBJECT_PT_io3d_material_panel'
    bl_label = 'Material Info'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options ={'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('io3d.material_export', text='Export Material', icon='MATERIAL')
        col = layout.column()

        materials = []
        for object in sorted(context.selected_objects, key=lambda x: x.name):
            if not object.type == 'MESH':
                continue
            try:
                material = object.data.materials[0]
                toon_shader = material.node_tree.nodes['Toon Shader']
                materials.append((material, toon_shader, object.name))
            except IndexError:
                materials.append((None, None, object.name))
        
        for material, toon_shader, name in materials:
            box = layout.box()
            box.label(text=name, icon='NODE_MATERIAL')
            if not toon_shader:
                col = box.column()
                col.label(text='Toon Shader not found')
                continue
            
            row = box.row()
            row.prop(material, '["Shader Type"]', text='Shader Type')

            if tuple(toon_shader.inputs[TOON_SHADER_INDEX['diffuse blend']].default_value) != (0.0, 0.0, 0.0, 1.0):
                row = box.row()
                row.prop(toon_shader.inputs[TOON_SHADER_INDEX['diffuse blend']], 'default_value', text='Diffuse Blend')
            
            if toon_shader.inputs[TOON_SHADER_INDEX['ambient strength']].default_value > 0:
                row = box.row()
                row.prop(toon_shader.inputs[TOON_SHADER_INDEX['ambient color']], 'default_value', text='Ambient Color')

            if toon_shader.inputs[TOON_SHADER_INDEX['emission strength']].default_value >= 100:
                row = box.row()
                if toon_shader.inputs[TOON_SHADER_INDEX['preserve color']].default_value:
                    row.label(text='Shadeless', icon='OUTLINER_OB_LIGHTPROBE')
                else:
                    row.prop(toon_shader.inputs[TOON_SHADER_INDEX['emission color']], 'default_value', text='Emission Color')

            if toon_shader.inputs[TOON_SHADER_INDEX['is transparent']].default_value:
                row = box.column()
                row.label(text='Transparency: black', icon='IMAGE_ALPHA')
            elif toon_shader.inputs[TOON_SHADER_INDEX['alpha']].is_linked:
                row = box.column()
                row.label(text='Transparency: source', icon='IMAGE_ALPHA')

            try:
                outline_color = material.node_tree.nodes['Outline Color']
                outline_thickness = material.node_tree.nodes['Outline Thickness']
                row = box.row()
                row.prop(outline_color.outputs['Color'], 'default_value', text='Outline Color')
                col = box.column()
                col.prop(outline_thickness.outputs['Value'], 'default_value', text='Outline Thickness')
            except KeyError:
                pass

            try:
                texture = material.node_tree.nodes['Skin Texture']
                if not texture.image:
                    continue
                texture_name = os.path.basename(texture.image.filepath)
                col = box.column()
                col.label(text='This shader is using skin color', icon='COLORSET_14_VEC')
                if texture_name:
                    row = col.split(factor=0.25)
                    row.alignment = 'LEFT'
                    row.label(text='Texture:')
                    row = row.box()
                    row.scale_y = 0.65
                    row.label(text=texture_name, icon='IMAGE_DATA')
                else:
                    col.label(text='(Image not saved)')
                    col.prop(texture.image, 'name', text='Texture', icon='IMAGE_DATA')
                continue
            except KeyError:
                pass

            try:
                texture = material.node_tree.nodes['Diffuse Texture']
                lightmap_texture = material.node_tree.nodes['LightMap Texture']
                if not texture.image or not lightmap_texture.image:
                    continue

                texture_name = os.path.basename(texture.image.filepath)
                lightmap_texture_name = os.path.basename(lightmap_texture.image.filepath)
                col = box.column()
                col.label(text='This shader is using lightmap', icon='LIGHTPROBE_VOLUME')
                if texture_name:
                    row = col.split(factor=0.25)
                    row.alignment = 'LEFT'
                    row.label(text='Texture:')
                    row = row.box()
                    row.scale_y = 0.65
                    row.label(text=texture_name, icon='IMAGE_DATA')
                else:
                    col.label(text='(Image not saved)')
                    col.prop(texture.image, 'name', text='Texture', icon='IMAGE_DATA')
                if lightmap_texture_name:
                    row = col.split(factor=0.25)
                    row.alignment = 'LEFT'
                    row.label(text='Lightmap Texture:')
                    row = row.box()
                    row.scale_y = 0.65
                    row.label(text=lightmap_texture_name, icon='IMAGE_DATA')
                else:
                    col.label(text='(Image not saved)')
                    col.prop(lightmap_texture.image, 'name', text='Lightmap Texture', icon='IMAGE_DATA')
                continue
            except KeyError:
                pass

            try:
                texture = material.node_tree.nodes['Diffuse Texture']
                if not texture.image:
                    continue

                texture_name = os.path.basename(texture.image.filepath)
                col = box.column()
                if texture_name:
                    row = col.split(factor=0.25)
                    row.alignment = 'LEFT'
                    row.label(text='Texture:')
                    row = row.box()
                    row.scale_y = 0.65
                    row.label(text=texture_name, icon='IMAGE_DATA')
                else:
                    col.label(text='(Image not saved)')
                    col.prop(texture.image, 'name', text='Texture', icon='IMAGE_DATA')
                continue
            except KeyError:
                pass

            try:
                texture = material.node_tree.nodes['Image Texture']
                if not texture.image:
                    continue

                texture_name = os.path.basename(texture.image.filepath)
                col = box.column()
                if texture_name:
                    row = col.split(factor=0.25)
                    row.alignment = 'LEFT'
                    row.label(text='Texture:')
                    row = row.box()
                    row.scale_y = 0.65
                    row.label(text=texture_name, icon='IMAGE_DATA')
                else:
                    col.label(text='(Image not saved)')
                    col.prop(texture.image, 'name', text='Texture', icon='IMAGE_DATA')
                continue
            except KeyError:
                pass
            
            # scroll_anim = False
            # rotate_anim = False
            # try:
            #     action = material.node_tree.animation_data.action
            #     for fcurve in action.fcurves:
            #         if fcurve.data_path == 'nodes["Mapping"].inputs[1].default_value':
            #             scroll_anim = True
            #         elif fcurve.data_path == 'nodes["Mapping"].inputs[2].default_value':
            #             rotate_anim = True
            # except AttributeError:
            #     pass
            
            # if scroll_anim:
            #     col = box.column()
            #     col.label(text='Scrolling Animation', icon='ANIM')
            # if rotate_anim:
            #     col = box.column()
            #     col.label(text='Rotating Animation', icon='ANIM')


def register():
    bpy.utils.register_class(MATERIAL_PANEL)


def unregister():
    bpy.utils.unregister_class(MATERIAL_PANEL)