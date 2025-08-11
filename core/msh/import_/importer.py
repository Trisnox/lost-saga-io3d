import bpy
import bmesh
import math
import numpy as np
import os
import pathlib
import struct


from ..ogre3d_parser import Ogre3DMaterialParser

from ...classes.seeker import Seeker
from ...classes.mesh import VertexComponent, MeshData, MeshType, BlendWeight, SKIN_COLOR_DICT, TOON_SHADER_INDEX


def is_using_newer_version():
    return bpy.app.version >= (4, 4, 0)

def is_mesh_file(bytes):
    return bytes == 4739917

def is_collision_file(bytes):
    return bytes == 5459267

def import_mesh(context: bpy.types.Context, filepath: str, resource_folder: str = None, skin_color: str = None, generate_outline: bool = False, use_rim_light: bool = False, surpress_color: bool = False, separate_material: bool = False, merge_faces: bool = False):    
    MESH_VERSION = 2000
    VERTEX_COLOR_MESH_VERSION = 2001
    MESH_CONTROL_POINT_VERSION = 2002
    
    mesh_name = pathlib.Path(filepath).stem
    with open(filepath, 'rb') as f:
        msh = f.read()
    
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass
    
    s = Seeker()
    signature = struct.unpack('<I', msh[:s.i])[0]
    if not is_mesh_file(signature):
        raise RuntimeError('Not a mesh file')

    version = struct.unpack('<I', msh[s.o:s.i])[0]
    mesh_type = MeshType(struct.unpack('<I', msh[s.o:s.i])[0])
    vertex_mask = struct.unpack('<L', msh[s.o:s.L])[0]
    bounding_box_min = struct.unpack('<3f', msh[s.o:s.vpos])
    bounding_box_max = struct.unpack('<3f', msh[s.o:s.vpos])
    bound_radius = struct.unpack('<f', msh[s.o:s.f])[0]
    submesh_count = struct.unpack('<I', msh[s.o:s.i])[0]
    submesh = []

    for _ in range(submesh_count):
        min_index = struct.unpack('<I', msh[s.o:s.i])[0]
        vertex_count = struct.unpack('<I', msh[s.o:s.i])[0]
        index_start = struct.unpack('<I', msh[s.o:s.i])[0]
        face_count = struct.unpack('<I', msh[s.o:s.i])[0]
        submesh.append(MeshData(min_index, vertex_count, index_start, face_count))
        
    vertices = struct.unpack('<I', msh[s.o:s.i])[0]
    
    position = []
    normal = []
    tangent_list = []
    normal_list = []
    vertex_color = []
    texture_uv = []
    light_texture_uv = []
    vcomp = VertexComponent()
    if vertex_mask & vcomp.IOFVF_POSITION:
        position = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
        
    if vertex_mask & vcomp.IOFVF_NORMAL:
        normal = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
        
    if vertex_mask & vcomp.IOFVF_TANGENT:
        tangent_list = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
        
    if vertex_mask & vcomp.IOFVF_BINORMAL:
        normal_list = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
        
    if vertex_mask & vcomp.IOFVF_COLOR0:
        vertex_color = [struct.unpack('<L', msh[s.o:s.L])[0] for _ in range(vertices)]
        
    if vertex_mask & vcomp.IOFVF_UV0:
        texture_uv = [struct.unpack('<2f', msh[s.o:s.v2]) for _ in range(vertices)]
        
    if vertex_mask & vcomp.IOFVF_UV1:
        light_texture_uv = [struct.unpack('<2f', msh[s.o:s.v2]) for _ in range(vertices)]
    
    biped_list = []
    weights = []
    if vertex_mask & vcomp.IOFVF_WEIGHTS:
        biped_index_count = struct.unpack('<I', msh[s.o:s.i])[0]
        for _ in range(biped_index_count):
            name_length = struct.unpack('<I', msh[s.o:s.i])[0]
            if name_length:
                name = msh[s.o:s.char(name_length)]
                biped_list.append(name.decode('utf-8'))
        
        for _ in range(vertices):
            weight = struct.unpack('<4f', msh[s.o:s.weight])
            biped_id = struct.unpack('<4f', msh[s.o:s.bipedID])
            weights.append(BlendWeight(weight, biped_id))
        
        # Not really needed, but I did it for the sake of full coverage
        joint_weight_count = 0
        max_weight_count = 0
        for weight in weights:
            for j in range(4):
                if weight.weight[j] > 0.0:
                    joint_weight_count += 1
                else:
                    if max_weight_count < j:
                        max_weight_count = j
                    break
    
    # After recent discovery, it appears that none of losa mesh uses this,
    # despite it being exist on source code
    billboard_center = []
    if vertex_mask & vcomp.IOFVF_POSITION2:
        billboard_center = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
    
    # Faces was constructed using WORD, which is equivalent to unsigned short
    face_count = struct.unpack('<I', msh[s.o:s.i])[0]
    faces = [struct.unpack('<H', msh[s.o:s.H])[0] for _ in range(face_count*3)]
    
    # This is only for older mesh, especially weapons, none of newer mesh use this anymore
    points = []
    if version == MESH_CONTROL_POINT_VERSION:
        point_count = struct.unpack('<I', msh[s.o:s.i])[0]
        for _ in range(point_count):
            type_index_length = struct.unpack('<I', msh[s.o:s.i])[0]
            type_index = b''
            if type_index_length:
                type_index = msh[s.o:s.char(type_index_length)]
            linked_biped_name_length = struct.unpack('<I', msh[s.o:s.i])[0]
            linked_biped_name = b''
            if linked_biped_name_length:
                linked_biped_name = msh[s.o:s.char(linked_biped_name_length)]
            extra_info_length = struct.unpack('<I', msh[s.o:s.i])[0]
            extra_info = b''
            if extra_info_length:
                extra_info = msh[s.o:s.char(extra_info_length)]
                
            vector_point = struct.unpack('<3f', msh[s.o:s.vpos])
            points.append(type_index)
            points.append(linked_biped_name)
            points.append(extra_info)
            points.append(vector_point)

    mesh_data = bpy.data.meshes.new(name=mesh_name)
    bm = bmesh.new()

    for pos in position:
        bm.verts.new(pos)
    bm.verts.ensure_lookup_table()

    for i in range(0, len(faces), 3):
        try:
            face_verts = [bm.verts[faces[i]], bm.verts[faces[i+1]], bm.verts[faces[i+2]]]
            bm.faces.new(face_verts)
        except Exception as e:
            print(f"Error creating face {i//3}: {e}")

    bm.normal_update()
    bm.to_mesh(mesh_data)
    bm.free()

    mesh_object = bpy.data.objects.new(mesh_name, mesh_data)
    bpy.context.collection.objects.link(mesh_object)
    
    mesh_object["Bounding Box min"] = bounding_box_min
    mesh_object["Bounding Box max"] = bounding_box_max
    mesh_object["Bounding radius"] = bound_radius
        
    for prop_name in ["Bounding Box min", "Bounding Box max", "Bounding radius"]:
        mesh_object.id_properties_ui(prop_name).update(
            description=f"Mesh {prop_name}",
            default=mesh_object[prop_name]
        )

    if normal:
        mesh_data.shade_smooth()
        # It's much more convenient to just rotate the normal on edit mode instead of doing the raw values
        # normal = [(n[0], -n[2], n[1]) for n in normal]
        mesh_data.normals_split_custom_set_from_vertices(normal)

    # For whatever reason, they seem to swapped lightmap UVmap and mesh UVmap
    # don't ask why, they just did
    if light_texture_uv:
        mesh_data.uv_layers.new(name="UVMap")
        uv_layer = mesh_data.uv_layers[-1].data
        
        for face in mesh_data.polygons:
            for loop_idx in face.loop_indices:
                vertex_index = mesh_data.loops[loop_idx].vertex_index
                uv = light_texture_uv[vertex_index]
                uv_layer[loop_idx].uv = (uv[0], 1.0 - uv[1])

    if texture_uv:
        mesh_data.uv_layers.new(name="UVMap" if not light_texture_uv else "LightMap")
        uv_layer = mesh_data.uv_layers[-1].data
        
        for face in mesh_data.polygons:
            for loop_idx in face.loop_indices:
                vertex_index = mesh_data.loops[loop_idx].vertex_index
                uv = texture_uv[vertex_index]
                uv_layer[loop_idx].uv = (uv[0], 1.0 - uv[1])
                
    if weights and biped_list:
        for bone_name in biped_list:
            mesh_object.vertex_groups.new(name=bone_name)
        
        for vert_idx, weight_data in enumerate(weights):
            for i in range(4):
                if weight_data.weight[i] > 0:
                    bone_idx = int(weight_data.biped_id[i])
                    if 0 <= bone_idx < len(biped_list):
                        group_name = biped_list[bone_idx]
                        mesh_object.vertex_groups[group_name].add([vert_idx], weight_data.weight[i], 'REPLACE')
    
    bpy.ops.object.select_all(action='DESELECT')
    mesh_object.select_set(state=True)
    context.view_layer.objects.active = mesh_object
    
    mesh_object['Type'] = mesh_type.type

    mesh_object.rotation_euler.x = math.radians(90)
    mesh_object.rotation_euler.z = math.radians(180)
    mesh_object.scale.x = -1.0
    bpy.ops.object.transform_apply(location = False, rotation = True, scale = True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')

    meshes = []
    for index, submesh_data in reversed(list(enumerate(submesh[1:], 1))):
        min_index, vertex_count, _, _ = submesh_data
        
        bpy.ops.object.select_all(action='DESELECT')
        mesh_object.select_set(True)
        context.view_layer.objects.active = mesh_object
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='VERT')
        
        ebm = bmesh.from_edit_mesh(mesh_data)
        ebm.verts.ensure_lookup_table()
        for vertex_index in range(vertex_count):
            vertex_index += min_index
            vert = ebm.verts[vertex_index]
            vert.select_set(True)
            
        ebm.select_mode = {'VERT'}
        ebm.select_flush_mode()
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        separated_mesh = context.view_layer.objects.selected[-1]
        separated_mesh.name = mesh_name + '_' + str(index)
        meshes.append(separated_mesh)
        ebm.free()
    meshes.append(mesh_object)
    meshes = list(reversed(meshes))

    if merge_faces:
        for mesh in meshes:
            bpy.ops.object.select_all(action='DESELECT')
            mesh_object.select_set(True)
            context.view_layer.objects.active = mesh_object

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(type='VERT')
            
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()

            bpy.ops.object.mode_set(mode='OBJECT')

    if not resource_folder:
        return {'FINISHED'}

    material_path = pathlib.Path(resource_folder)
    material_path = material_path.joinpath('material')
    material_path = material_path.joinpath(mesh_name + '.txt')

    file_dir = os.path.dirname(os.path.abspath(__file__))
    addon_directory = os.path.dirname(os.path.dirname(os.path.dirname(file_dir)))
    blend_location = addon_directory + '/losa shader.blend'
    if material_path.exists():
        try:
            toon_shader_data = bpy.data.node_groups['Toon Shader']
        except KeyError:
            bpy.ops.wm.append(filename='NodeTree/Toon Shader', directory=blend_location)
            toon_shader_data = bpy.data.node_groups['Toon Shader']

        try:
            skin_setup_data = bpy.data.node_groups['Skin Setup']
        except KeyError:
            bpy.ops.wm.append(filename='NodeTree/Skin Setup', directory=blend_location)
            skin_setup_data = bpy.data.node_groups['Skin Setup']

        # try:
        #     texture_setup_data = bpy.data.node_groups['Texture Setup']
        # except KeyError:
        #     bpy.ops.wm.append(filename='NodeTree/Texture Setup', directory=blend_location)
        #     texture_setup_data = bpy.data.node_groups['Texture Setup']

        try:
            lightmap_setup_data = bpy.data.node_groups['LightMap Setup']
        except KeyError:
            bpy.ops.wm.append(filename='NodeTree/LightMap Setup', directory=blend_location)
            lightmap_setup_data = bpy.data.node_groups['LightMap Setup']


        # I found it hard and incovenient to insert keyframe using foreach_set
        def scroll_UV(scroll_anim, mapping_node, material):
            x_length, y_length = scroll_anim
            for index, length in enumerate((x_length, y_length)):
                if length == 0.0:
                    continue

                fps = context.scene.render.fps
                keyframe_count = int(fps / length)

                current_frame = context.scene.frame_current
                context.scene.frame_set(1)
                mapping_node.inputs['Location'].keyframe_insert(data_path='default_value')
                context.scene.frame_set(keyframe_count)
                mapping_node.inputs['Location'].default_value = (1.0 if index == 0 else 0.0, 1.0 if index == 1 else 0.0, 0.0)
                mapping_node.inputs['Location'].keyframe_insert(data_path='default_value')
                context.scene.frame_set(current_frame)

                action = material.node_tree.animation_data.action
                if is_using_newer_version:
                    fcurves = action.layers[0].strips[0].channelbag(action.slots[0]).fcurves
                else:
                    fcurves = action.fcurves

                for fcurve in fcurves:
                    if fcurve.data_path == 'nodes["Mapping"].inputs[1].default_value':
                        modifier = fcurve.modifiers.new(type='CYCLES')
                        fcurve.extrapolation = 'LINEAR'

        def rotate_UV(rotate_anim, mapping_node, material):
            fps = context.scene.render.fps
            keyframe_count = int((360 / abs(rotate_anim)) * fps)

            current_frame = context.scene.frame_current
            context.scene.frame_set(1)
            mapping_node.inputs['Rotation'].keyframe_insert(data_path='default_value')
            context.scene.frame_set(keyframe_count)
            mapping_node.inputs['Rotation'].default_value = (360.0 if rotate_anim > 0 else -360.0, 0.0, 0.0)
            mapping_node.inputs['Rotation'].keyframe_insert(data_path='default_value')
            context.scene.frame_set(current_frame)

            action = material.node_tree.animation_data.action
            if is_using_newer_version:
                fcurves = action.layers[0].strips[0].channelbag(action.slots[0]).fcurves
            else:
                fcurves = action.fcurves

            for fcurve in fcurves:
                if fcurve.data_path == 'nodes["Mapping"].inputs[2].default_value':
                    modifier = fcurve.modifiers.new(type='CYCLES')
                    fcurve.extrapolation = 'LINEAR'
        
        # Missing anim: color_xform, wave_xform, and possibly more

        parser = Ogre3DMaterialParser()
        material_file = parser.parse_file(material_path)
        for mesh, mat_file in zip(meshes, material_file):
            material = bpy.data.materials.new(name=mesh.name)
            mesh.data.materials.append(material)
            material.use_nodes = True
            # Even though blended mode is better for transparency, Lost Saga uses too much
            # transparency that it's much better off using dithered method
            # material.surface_render_method = 'BLENDED'
            # material.use_transparency_overlap = False
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

            diffuse = mat_file.properties.get('diffuse', None)
            ambient = mat_file.properties.get('ambient', None)
            emissive = mat_file.properties.get('emissive', None)
            preserve_color = True if emissive and all(x == emissive[0] for x in emissive) else False
            if diffuse:
                toon_shader_node.inputs[TOON_SHADER_INDEX['diffuse blend']].default_value = (*diffuse, 1.0)
            if ambient:
                toon_shader_node.inputs[TOON_SHADER_INDEX['ambient color']].default_value = (*ambient, 1.0)
                toon_shader_node.inputs[TOON_SHADER_INDEX['ambient strength']].default_value = 30
            if emissive:
                toon_shader_node.inputs[TOON_SHADER_INDEX['emission color']].default_value = (*emissive, 1.0)
                toon_shader_node.inputs[TOON_SHADER_INDEX['emission strength']].default_value = 100
            if preserve_color:
                toon_shader_node.inputs[TOON_SHADER_INDEX['preserve color']].default_value = True
            
            is_lightmap = False
            is_textured = False

            # Pre-defining the passes, whichever is the latest will be overwritten with newer ones
            shader_group = '' # LightMap/Static/AnimateToonShade/Animate/StaticToonShade
            scene_blend = ''
            texture_diffuse_name = ''
            texture_lightmap_name = ''
            color_blend = ''
            use_skin = False
            lightmap_color_blend = ''
            outline_color = ()
            outline_thickness = 0.0 # I have no idea how many unit is 1.0, let's just assume 1 meter
            scroll_anim = ''
            rotate_anim = ''
            lightmap_scroll_anim = ''
            lightmap_rotate_anim = ''
            for passes in mat_file.techniques[0].passes:
                new_shader_group = passes.properties.get('shader_group', '')
                new_scene_blend = passes.scene_blend
                if not shader_group:
                    shader_group = new_shader_group
                    material['Shader Type'] = shader_group
                if not scene_blend:
                    scene_blend = new_scene_blend

                if new_shader_group == 'AnimateOutLine':
                    param = passes.properties['custom_param']
                    outline_color, outline_thickness = param
                    outline_color = tuple(float(_) for _ in outline_color.split(' ')[-4::])
                    outline_thickness = float(outline_thickness.split(' ')[-1])

                    outline_rgb_node = material.node_tree.nodes.new('ShaderNodeRGB')
                    outline_rgb_node.name = 'Outline Color'
                    outline_rgb_node.location = (300, 133)
                    outline_rgb_node.outputs['Color'].default_value = outline_color

                    outline_value_node = material.node_tree.nodes.new('ShaderNodeValue')
                    outline_value_node.name = 'Outline Thickness'
                    outline_value_node.location = (300, -100)
                    outline_value_node.outputs['Value'].default_value = outline_thickness

                    if not generate_outline:
                        continue
                    if use_rim_light:
                        toon_shader_node.inputs[TOON_SHADER_INDEX['rim light color']].default_value = outline_color
                        toon_shader_node.inputs[TOON_SHADER_INDEX['rim light strength']].default_value = 100
                    else:
                        material_init = True
                        if surpress_color:
                            outline_color = (0.0, 0.0, 0.0, 1.0)
                        if separate_material or not surpress_color:
                            outline_material = bpy.data.materials.new(name=mesh.name + ' Outline')
                        else:
                            try:
                                outline_material = bpy.data.materials['Outline']
                                material_init = False
                            except KeyError:
                                outline_material = bpy.data.materials.new('Outline')

                        if material_init:
                            outline_material.use_nodes = True
                            material_output = outline_material.node_tree.nodes['Material Output']

                            principled = outline_material.node_tree.nodes['Principled BSDF']
                            outline_material.node_tree.nodes.remove(principled)
                            
                            emission_node = outline_material.node_tree.nodes.new('ShaderNodeEmission')
                            emission_node.location = (0, 300)
                            emission_node.inputs['Color'].default_value = outline_color

                            outline_links = outline_material.node_tree.links
                            outline_links.new(emission_node.outputs['Emission'], material_output.inputs['Surface'])

                            outline_material.diffuse_color = outline_color
                            outline_material.metallic = 1
                            outline_material.roughness = 1

                        mesh.data.materials.append(outline_material)

                        outline_modifier = mesh.modifiers.new(name='Losa Outline', type='SOLIDIFY')
                        outline_modifier.thickness = outline_thickness
                        outline_modifier.offset = 1.0
                        outline_modifier.use_rim_only = True
                        outline_modifier.use_flip_normals = True
                        outline_modifier.material_offset = 1
                        outline_modifier.material_offset_rim = 1
                    continue
                
                if shader_group == 'LightMap' and not texture_diffuse_name:
                    lightmap_unit = passes.texture_units[0]
                    diffuse_unit = passes.texture_units[1]

                    texture_diffuse_name = diffuse_unit.texture
                    texture_lightmap_name = lightmap_unit.texture
                    lightmap_color_blend = lightmap_unit.properties.get('color_blend')
                    scroll_anim = passes.texture_units[0].properties.get('scroll_anim', None)
                    rotate_anim = passes.texture_units[0].properties.get('rotate_anim', None)
                    lightmap_scroll_anim = passes.texture_units[1].properties.get('scroll_anim', None)
                    lightmap_rotate_anim = passes.texture_units[1].properties.get('rotate_anim', None)
                    break

                for unit in passes.texture_units:
                    if not texture_diffuse_name:
                            if unit.texture:
                                texture_diffuse_name = unit.texture

                    if not color_blend:
                        color_blend = unit.properties.get('color_blend', None)
                    else:
                        new_color_blend = unit.properties.get('color_blend', None)
                        if new_color_blend:
                            color_blend = new_color_blend
                        if new_color_blend == 'blend_texture_alpha texture tfactor':
                            use_skin = True
                    
                    if not scroll_anim:
                        scroll_anim = unit.properties.get('scroll_anim', None)
                    if not rotate_anim:
                        rotate_anim = unit.properties.get('rotate_anim', None)

            should_opaque = True if not scene_blend or scene_blend == 'add zero src_color' else False
            has_alpha = False
            if should_opaque and emissive:
                toon_shader_node.inputs[TOON_SHADER_INDEX['opacity']].default_value = 0
                toon_shader_node.inputs[TOON_SHADER_INDEX['invert opacity']].default_value = False
            elif scene_blend == 'add src_alpha one' or scene_blend == 'add inv_dest_color one':
                toon_shader_node.inputs[TOON_SHADER_INDEX['is transparent']].default_value = True
            elif scene_blend == 'add src_alpha inv_src_alpha' or scene_blend == 'add one src_alpha':
                has_alpha = True

            if shader_group == 'LightMap':
                texture_diffuse = bpy.data.images.get(texture_diffuse_name)
                texture_lightmap = bpy.data.images.get(texture_lightmap_name)

                texture_path = pathlib.Path(resource_folder)
                texture_path = texture_path.joinpath('texture')
                if not texture_diffuse:
                    texture_diffuse = bpy.data.images.load(str(texture_path.joinpath(texture_diffuse_name)))
                if not texture_lightmap:
                    texture_lightmap = bpy.data.images.load(str(texture_path.joinpath(texture_lightmap_name)))

                lightmap_node = material.node_tree.nodes.new('ShaderNodeGroup')
                lightmap_node.node_tree = lightmap_setup_data
                lightmap_node.location = (-850, 0)

                context.view_layer.objects.active = mesh
                old_area = context.area.ui_type
                context.area.ui_type = 'ShaderNodeTree'
                for node in material.node_tree.nodes:
                    node.select = False
                lightmap_node.select = True
                material.node_tree.nodes.active = lightmap_node
                bpy.ops.node.group_ungroup()
                context.area.ui_type = old_area

                uv_map_node = material.node_tree.nodes['UV Map']
                diffuse_mapping = material.node_tree.nodes['Diffuse Mapping']
                lightmap_mapping = material.node_tree.nodes['LightMap Mapping']
                diffuse_texture_node = material.node_tree.nodes['Diffuse Texture']
                lightmap_texture_node = material.node_tree.nodes['LightMap Texture']
                invert_alpha_node = material.node_tree.nodes['Invert Alpha']
                color_mix_node = material.node_tree.nodes['Mix']

                diffuse_texture_node.image = texture_diffuse
                lightmap_texture_node.image = texture_lightmap
                if scene_blend == 'add src_alpha inv_src_alpha':
                    invert_alpha_node.inputs[0].default_value = 0.0
                uv_map_node.uv_map = 'LightMap'
                links.new(color_mix_node.outputs['Result'], toon_shader_node.inputs[TOON_SHADER_INDEX['color/texture']])

                if scroll_anim:
                    scroll_UV(scroll_anim, diffuse_mapping, material)
                if rotate_anim:
                    rotate_UV(rotate_anim, diffuse_mapping, material)
                if lightmap_scroll_anim:
                    scroll_UV(lightmap_scroll_anim, lightmap_mapping, material)
                if lightmap_rotate_anim:
                    rotate_UV(lightmap_rotate_anim, lightmap_mapping, material)
            elif use_skin:
                texture = bpy.data.images.get(texture_diffuse_name)
                if not texture:
                    texture_path = pathlib.Path(resource_folder)
                    texture_path = texture_path.joinpath('texture')
                    texture_path = texture_path.joinpath(texture_diffuse_name)
                    texture = bpy.data.images.load(str(texture_path))

                skin_node = material.node_tree.nodes.new('ShaderNodeGroup')
                skin_node.node_tree = skin_setup_data
                skin_node.location = (-750, 150)
                
                context.view_layer.objects.active = mesh
                old_area = context.area.ui_type
                context.area.ui_type = 'ShaderNodeTree'
                for node in material.node_tree.nodes:
                    node.select = False
                skin_node.select = True
                material.node_tree.nodes.active = skin_node
                bpy.ops.node.group_ungroup()
                context.area.ui_type = old_area

                mapping_node = material.node_tree.nodes['Mapping']
                texture_node = material.node_tree.nodes['Skin Texture']
                color_mix_node = material.node_tree.nodes['Skin Mix']
                color_mix_output = material.node_tree.nodes['Mix Output']

                texture_node.image = texture
                color_mix_node.inputs['A'].default_value = SKIN_COLOR_DICT[skin_color][0]
                color_mix_node.inputs['B'].default_value = SKIN_COLOR_DICT[skin_color][1]
                toon_shader_node.inputs[TOON_SHADER_INDEX['shadow color']].default_value = SKIN_COLOR_DICT[skin_color][2]
                links.new(color_mix_output.outputs['Result'], toon_shader_node.inputs[TOON_SHADER_INDEX['color/texture']])

                if scroll_anim:
                    scroll_UV(scroll_anim, mapping_node, material)
                if rotate_anim:
                    rotate_UV(rotate_anim, mapping_node, material)
            else:
                texture = bpy.data.images.get(texture_diffuse_name)
                if not texture:
                    texture_path = pathlib.Path(resource_folder)
                    texture_path = texture_path.joinpath('texture')
                    texture_path = texture_path.joinpath(texture_diffuse_name)
                    texture = bpy.data.images.load(str(texture_path))

                texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
                texture_node.name = 'Diffuse Texture'
                texture_node.image = texture
                texture_node.location = (-300, 300)
                links.new(texture_node.outputs['Color'], toon_shader_node.inputs[TOON_SHADER_INDEX['color/texture']])

                if has_alpha:
                    links.new(texture_node.outputs['Alpha'], toon_shader_node.inputs[TOON_SHADER_INDEX['alpha']])

                mapping_node = material.node_tree.nodes.new('ShaderNodeMapping')
                mapping_node.location = (-500, 300)
                links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])

                tex_coord_node = material.node_tree.nodes.new('ShaderNodeTexCoord')
                tex_coord_node.location = (-700, 200)
                links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['Vector'])

                if scroll_anim:
                    scroll_UV(scroll_anim, mapping_node, material)
                if rotate_anim:
                    rotate_UV(rotate_anim, mapping_node, material)
    return {'FINISHED'}

def import_collision(context: bpy.types.Context, filepath: str):
    mesh_name = pathlib.Path(filepath).stem + '_collision'

    with open(filepath, 'rb') as f:
        msh = f.read()

    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass

    s = Seeker()
    signature = struct.unpack('<I', msh[:s.i])[0]
    if not is_collision_file(signature):
        raise RuntimeError('Not a collision mesh file')

    version = struct.unpack('<I', msh[s.o:s.i])[0]
    vertex_count = struct.unpack('<I', msh[s.o:s.i])[0]
    vertices = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertex_count)]
    face_count = struct.unpack('<I', msh[s.o:s.i])[0]
    faces = [struct.unpack('<H', msh[s.o:s.H])[0] for _ in range(face_count*3)]

    mesh_data = bpy.data.meshes.new(name=mesh_name)
    bm = bmesh.new()

    for pos in vertices:
        bm.verts.new(pos)
    bm.verts.ensure_lookup_table()

    for i in range(0, len(faces), 3):
        try:
            face_verts = [bm.verts[faces[i]], bm.verts[faces[i+1]], bm.verts[faces[i+2]]]
            bm.faces.new(face_verts)
        except Exception as e:
            print(f"Error creating face {i//3}: {e}")

    bm.normal_update()
    bm.to_mesh(mesh_data)
    bm.free()

    mesh_object = bpy.data.objects.new(mesh_name, mesh_data)
    bpy.context.collection.objects.link(mesh_object)

    bpy.ops.object.select_all(action='DESELECT')
    mesh_object.select_set(state=True)
    context.view_layer.objects.active = mesh_object

    mesh_object.rotation_euler.x = math.radians(90)
    mesh_object.rotation_euler.z = math.radians(180)
    mesh_object.scale.x = -1.0
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')

    return {'FINISHED'}

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty, BoolProperty, EnumProperty
from bpy.types import Operator, PropertyGroup


class LosaMesh(Operator, ImportHelper):
    """Import Lost Saga Mesh (.msh). Supports importing multiple files at once"""
    bl_idname = "io3d.mesh_import" 
    bl_label = "Import Lost Saga Mesh (.msh)"

    filename_ext = ".msh"

    filter_glob: StringProperty(
        default="*.msh",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    default_skin_color: EnumProperty(
        name="Default Skin Color",
        description="If mesh contains skin, this color will be used for that skin",
        items=(
            ('VANILLA', 'Vanilla', ''),
            ('PEACH', 'Peach', ''),
            ('APRICOT', 'Apricot', ''),
            ('CHOCOLATE', 'Chocolate', ''),
            ('PALE', 'Pale', ''),
            ('FROZEN', 'Frozen', ''),
            ('GREEN', 'Green', ''),
            ('UNDEAD', 'Undead', ''),
            ('GREY', 'Grey', ''),
        ),
        default='VANILLA'
    )

    generate_outline: BoolProperty(
        name="Generate Outline",
        description="Whether to generate outline to model or not",
        default=False
    )

    use_rim_light: BoolProperty(
        name="Use Rim Light Instead",
        description="If checked, rim light will be used for outline instead of solidify modifier",
        default=False
    )

    surpress_color: BoolProperty(
        name="Surpress Color",
        description="If checked, outline will not use pre-determined color on material files, and instead defaults to black",
        default=False
    )

    separate_material: BoolProperty(
        name="Separate Material",
        description="If checked, each mesh will generate its own outline material, otherwise they share the same material data",
        default=False
    )

    merge_faces: BoolProperty(
        name="Merge Faces",
        description="If checked, blender will attempt marge the mesh by distance, which will make outline more clean (may cause UV issues on some models)",
        default=False
    )
    
    files: CollectionProperty(type=PropertyGroup)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "default_skin_color")

        col = layout.column()
        col.prop(self, "merge_faces")
        col = layout.column()
        col.enabled = (bool(context.scene.io3d_resource_path.path))
        col.prop(self, "generate_outline")
        col = layout.column()
        col.prop(self, "use_rim_light")
        col.enabled = (bool(self.generate_outline))
        col = layout.column()
        col.prop(self, "surpress_color")
        col.enabled = (bool(self.generate_outline))
        col = layout.column()
        col.prop(self, "separate_material")
        col.enabled = (bool(self.surpress_color))
    
    def execute(self, context):
        path = pathlib.Path(self.filepath)
        folder = path.parent
        for file in self.files:
            filepath = str(folder.joinpath(file.name))
            import_mesh(context, filepath, context.scene.io3d_resource_path.path, self.default_skin_color, self.generate_outline, self.use_rim_light, self.surpress_color, self.separate_material, self.merge_faces)

        if len(self.files) > 1:
            self.report({'INFO'}, f'Successfully imported {len(self.files)} meshes')
        else:
            self.report({'INFO'}, f'Imported "{file.name}"')

        return {'FINISHED'}

class LosaCol(Operator, ImportHelper):
    """Import Lost Saga Collision Mesh (.cms). Supports importing multiple files at once"""
    bl_idname = "io3d.collision_mesh_import"
    bl_label = "Import Lost Saga Collision Mesh (.cms)"

    filename_ext = ".cms"

    filter_glob: StringProperty(
        default="*.cms",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: CollectionProperty(type=PropertyGroup)

    def execute(self, context):
        path = pathlib.Path(self.filepath)
        folder = path.parent
        for file in self.files:
            filepath = str(folder.joinpath(file.name))
            import_collision(context, filepath)
            
        if len(self.files) > 1:
            self.report({'INFO'}, f'Successfully imported {len(self.files)} collision meshes')
        else:
            self.report({'INFO'}, f'Imported "{file.name}"')

        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(LosaMesh.bl_idname, text="Lost Saga Mesh (.msh)", icon='OUTLINER_OB_MESH')
    self.layout.operator(LosaCol.bl_idname, text="Lost Saga Collision Mesh (.cms)", icon='CUBE')

def register():
    bpy.utils.register_class(LosaMesh)
    bpy.utils.register_class(LosaCol)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(LosaMesh)
    bpy.utils.unregister_class(LosaCol)