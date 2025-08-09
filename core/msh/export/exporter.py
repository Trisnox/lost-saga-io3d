import bpy
import bpy
import bmesh
import struct
import math
import mathutils

from collections import defaultdict
from ....core.classes.mesh import TOON_SHADER_INDEX, BlendWeight, VertexComponent


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
                texture_node = material.node_tree.nodes['Diffuse Texture']
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
    
    return filepath


def export_mesh(context: bpy.types.Context, filepath: str, surpress_split: bool, preview_split: bool, mesh_type: str, use_normals: bool, use_uv: bool, use_uv1: bool, use_weights: bool):
    mesh_type = int(mesh_type)

    original_objects = context.selected_objects
    bpy.ops.object.duplicate()

    meshes = sorted(context.selected_objects, key=lambda x: x.name)
    for object in meshes:
        if not preview_split:
            object.rotation_euler.x = math.radians(90)
            object.rotation_euler.z = math.radians(180)
            object.scale.x = -1
        object.modifiers.new(name='Triangulate_' + object.name, type='TRIANGULATE')
        bpy.ops.object.modifier_apply(modifier='Triangulate_' + object.name, use_selected_objects=True)

        mesh_data = object.data
        bm = bmesh.new()
        bm.from_mesh(mesh_data)
        bm.verts.ensure_lookup_table()
        bmesh.ops.split_edges(bm, edges=[e for e in bm.edges if e.seam])
        bm.to_mesh(mesh_data)
        bm.free()

        if not surpress_split:
            for index in range(2 if object.data.materials.get('Shader Type', '') == 'LightMap' else 1):
                mesh_data = object.data
                bm = bmesh.new()
                bm.from_mesh(mesh_data)
                bm.verts.ensure_lookup_table()

                uv_layer = bm.loops.layers.uv[index]

                vertex_uvs = defaultdict(list)

                for face in bm.faces:
                    for loop in face.loops:
                        vertex_index = loop.vert.index
                        uv_coord = (loop[uv_layer].uv[0], loop[uv_layer].uv[1])
                        vertex_uvs[vertex_index].append((uv_coord, face.index, loop))

                seam_edges = set()
                vertices_with_seams = []
                tolerance = 1e-6

                for vertex_index, uv_data in vertex_uvs.items():
                    if len(uv_data) > 1:
                        first_uv = uv_data[0][0]
                        has_different_uvs = False

                        for uv_coord, face_index, loop in uv_data[1:]:
                            uv_diff_x = abs(uv_coord[0] - first_uv[0])
                            uv_diff_y = abs(uv_coord[1] - first_uv[1])

                            if uv_diff_x > tolerance or uv_diff_y > tolerance:
                                has_different_uvs = True
                                break

                        if has_different_uvs:
                            vertices_with_seams.append(vertex_index)

                            vertex = bm.verts[vertex_index]
                            for edge in vertex.link_edges:
                                if len(edge.link_faces) == 2:
                                    face1, face2 = edge.link_faces

                                    uv1 = None
                                    uv2 = None

                                    for loop in face1.loops:
                                        if loop.vert.index == vertex_index:
                                            uv1 = (loop[uv_layer].uv[0],
                                                loop[uv_layer].uv[1])
                                            break

                                    for loop in face2.loops:
                                        if loop.vert.index == vertex_index:
                                            uv2 = (loop[uv_layer].uv[0],
                                                loop[uv_layer].uv[1])
                                            break

                                    if uv1 and uv2:
                                        uv_diff_x = abs(uv1[0] - uv2[0])
                                        uv_diff_y = abs(uv1[1] - uv2[1])

                                        if uv_diff_x > tolerance or uv_diff_y > tolerance:
                                            edge.seam = True
                                            seam_edges.add(edge.index)

                bmesh.ops.split_edges(bm, edges=[e for e in bm.edges if e.seam])
                bm.to_mesh(mesh_data)
                bm.free()
    
    if not preview_split:
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        try:
            bpy.ops.object.mode_set(mode='EDIT')
        except:
            pass
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.mode_set(mode='OBJECT')

    # if normalize_weights and mesh_type == 1:
    #     try:
    #         bpy.ops.object.mode_set(mode='EDIT')
    #     except:
    #         pass
    #     bpy.ops.mesh.select_all(action='SELECT')
    #     bpy.ops.object.vertex_group_normalize_all(group_select_mode='BONE_DEFORM')
    #     bpy.ops.object.mode_set(mode='OBJECT')
        

    if preview_split:
        main_uv = []
        lightmap_uv = []
        for mesh in meshes:
            mesh_data = mesh.data
            uv_layer = mesh_data.uv_layers[0].data
            vertex_uvs = {}

            for poly in mesh_data.polygons:
                for vert_idx, loop_idx in zip(poly.vertices, poly.loop_indices):
                    vertex_uvs[vert_idx] = uv_layer[loop_idx].uv

            for vertex_idx in range(len(mesh_data.vertices)):
                if vertex_idx in vertex_uvs:
                    uv = vertex_uvs[vertex_idx]
                    main_uv.append(uv)

        try:
            mesh_data = mesh.data
            secondary_uv = mesh_data.uv_layers[1].data
        except IndexError:
            secondary_uv = None
        
        if secondary_uv:
            for mesh in meshes:
                mesh_data = mesh.data
                uv_layer = mesh_data.uv_layers[1].data
                vertex_uvs = {}

                for poly in mesh_data.polygons:
                    for vert_idx, loop_idx in zip(poly.vertices, poly.loop_indices):
                        vertex_uvs[vert_idx] = uv_layer[loop_idx].uv

                for vertex_idx in range(len(mesh_data.vertices)):
                    if vertex_idx in vertex_uvs:
                        uv = vertex_uvs[vertex_idx]
                        lightmap_uv.append(uv)
                        
        if main_uv:
            uv_layer = mesh_data.uv_layers[0].data
            
            for face in mesh_data.polygons:
                for loop_idx in face.loop_indices:
                    vertex_index = mesh_data.loops[loop_idx].vertex_index
                    uv = main_uv[vertex_index]
                    uv_layer[loop_idx].uv = (uv[0], uv[1])

        if lightmap_uv:
            uv_layer = mesh_data.uv_layers[1].data
            
            for face in mesh_data.polygons:
                for loop_idx in face.loop_indices:
                    vertex_index = mesh_data.loops[loop_idx].vertex_index
                    uv = lightmap_uv[vertex_index]
                    uv_layer[loop_idx].uv = (uv[0], uv[1])

        return {'FINISHED'}

    vcomp = VertexComponent()
    vertex_mask = vcomp.IOFVF_POSITION
    if mesh_type == 0:
        if use_normals:
            vertex_mask |= vcomp.IOFVF_NORMAL
        if use_uv:
            vertex_mask |= vcomp.IOFVF_UV0
    elif mesh_type == 1:
        if use_normals:
            vertex_mask |= vcomp.IOFVF_NORMAL
        if use_uv:
            vertex_mask |= vcomp.IOFVF_UV0
        if use_weights:
            vertex_mask |= vcomp.IOFVF_WEIGHTS
            vertex_mask |= vcomp.IOFVF_INDICES
    elif mesh_type == 2:
        if use_uv:
            vertex_mask |= vcomp.IOFVF_UV0
        if use_uv1:
            vertex_mask |= vcomp.IOFVF_UV1
    
    corners = []
    for object in meshes:
        corners.extend([object.matrix_world @ mathutils.Vector(corner) for corner in object.bound_box])
    
    bbox_min = mathutils.Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    bbox_max = mathutils.Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    bound_radius = (bbox_max - bbox_min).length / 2
    
    vertices = []
    normals = []
    polygons = []
    submesh = []
    vertex_offset = 0

    for mesh in meshes:
        mesh_data = mesh.data
        count = [
            vertex_offset,  # min_index
            len(mesh_data.vertices),  # vertex_count
            len(polygons) * 3,  # index_start
            len(mesh_data.polygons)  # face_count
        ]
        submesh.append(count)

        vertices.extend(mesh_data.vertices)

        if vertex_mask & vcomp.IOFVF_NORMAL:
            normals.extend(mesh_data.vertex_normals)

        for poly in mesh_data.polygons:
            class AdjustedPoly:
                def __init__(self, original_poly, offset):
                    self.vertices = [v + offset for v in original_poly.vertices]
                    
            polygons.append(AdjustedPoly(poly, vertex_offset))

        vertex_offset += len(mesh_data.vertices)

    with open(filepath, 'wb') as f:
        f.write(struct.pack('<I', 4739917))  # Signature
        f.write(struct.pack('<I', 2000))  # Version
        f.write(struct.pack('<I', mesh_type)) # mesh_type
        f.write(struct.pack('<L', vertex_mask))
        
        f.write(struct.pack('<3f', *bbox_min))
        f.write(struct.pack('<3f', *bbox_max))
        f.write(struct.pack('<f', bound_radius))
        
        f.write(struct.pack('<I', len(submesh))) # Submesh count
        
        # submesh
        for min_index, vertex_count, index_start, face_count in submesh:
            f.write(struct.pack('<I', min_index))
            f.write(struct.pack('<I', vertex_count))
            f.write(struct.pack('<I', index_start))
            f.write(struct.pack('<I', face_count))
        
        f.write(struct.pack('<I', len(vertices))) # vertex count
        
        # Check is not needed for this one... why would you?
        for vert in vertices:
            f.write(struct.pack('<3f', *vert.co))

        if vertex_mask & vcomp.IOFVF_NORMAL:
            for normal in normals:
                f.write(struct.pack('<3f', *normal.vector))

        if vertex_mask & vcomp.IOFVF_UV1:
            for mesh in meshes:
                mesh_data = mesh.data
                uv_layer = mesh_data.uv_layers[1].data
                vertex_uvs = {}

                for poly in mesh_data.polygons:
                    for vert_idx, loop_idx in zip(poly.vertices, poly.loop_indices):
                        vertex_uvs[vert_idx] = uv_layer[loop_idx].uv

                for vertex_idx in range(len(mesh_data.vertices)):
                    if vertex_idx in vertex_uvs:
                        uv = vertex_uvs[vertex_idx]
                        f.write(struct.pack('<2f', uv.x, 1.0 - uv.y))
                    else:
                        f.write(struct.pack('<2f', 0.0, 0.0))

        if vertex_mask & vcomp.IOFVF_UV0:
            for mesh in meshes:
                mesh_data = mesh.data
                uv_layer = mesh_data.uv_layers[0].data
                vertex_uvs = {}

                for poly in mesh_data.polygons:
                    for vert_idx, loop_idx in zip(poly.vertices, poly.loop_indices):
                        vertex_uvs[vert_idx] = uv_layer[loop_idx].uv

                for vertex_idx in range(len(mesh_data.vertices)):
                    if vertex_idx in vertex_uvs:
                        uv = vertex_uvs[vertex_idx]
                        f.write(struct.pack('<2f', uv.x, 1.0 - uv.y))
                    else:
                        f.write(struct.pack('<2f', 0.0, 0.0))
            
        
        if vertex_mask & vcomp.IOFVF_WEIGHTS:
            biped_list = []
            for mesh in meshes:
                for group in mesh.vertex_groups:
                    if group.name not in biped_list:
                        biped_list.append(group.name)

            f.write(struct.pack('<I', len(biped_list)))
            
            for name in biped_list:
                name_bytes = name.encode('utf-8')
                f.write(struct.pack('<I', len(name_bytes)))
                f.write(name_bytes)

            weight_groups = []
            for vertex in vertices:
                blend_group = []
                previous_indices = 0.0
                previous_weight = 0.0
                
                for group in vertex.groups:
                    if not group.group < len(biped_list):
                        continue
                    if group.weight > 0.0:
                        continue

                    blend_group.append((group.weight, float(group.group)))

                    if not previous_indices:
                        previous_indices = float(group.group)
                    if previous_weight >= group.weight and previous_indices:
                        previous_indices = float(group.group)
                    previous_weight = group.weight

                while len(blend_group) < 4:
                    blend_group.append((0.0, previous_indices))
                
                blend_group.sort(key=lambda x: x[0], reverse=True)
                blend_group = blend_group[:4]

                total_weight = sum(weight for weight, _ in blend_group)
                if total_weight > 0.0:
                    blend_group = [(weight / total_weight, indices) for weight, indices in blend_group]

                weight_groups.append(BlendWeight(*list(zip(*blend_group))))
            
            for blend in weight_groups:
                weights, indices = blend.group
                f.write(struct.pack('<4f', *weights))
                f.write(struct.pack('<4f', *indices))
        
        # if vertex_mask & vcomp.IOFVF_COLOR0:
        #    for mesh in meshes:
        #     color_layer = mesh.data.vertex_colors[0].data
        #     for poly in mesh.data.polygons:
        #         for loop_idx in poly.loop_indices:
        #             color = color_layer[loop_idx].color
        #             r = int(color[0] * 255)
        #             g = int(color[1] * 255)
        #             b = int(color[2] * 255)
        #             a = int(color[3] * 255) if len(color) > 3 else 255
        #             color_uint = (a << 24) | (b << 16) | (g << 8) | r
        #             f.write(struct.pack('<L', color_uint))

        f.write(struct.pack('<I', len(polygons))) # face count
        for poly in polygons:
            indices = list(poly.vertices)
            for vertex_idx in indices:
                f.write(struct.pack('<H', vertex_idx))
    
    for mesh in meshes:
        bpy.data.objects.remove(mesh)
    
    for object in original_objects:
        object.select_set(True)
    context.view_layer.objects.active = original_objects[0]

    return filepath


def export_collision(context: bpy.types.Context, filepath: str):
    original_object = context.active_object
    bpy.ops.object.select_all(action='DESELECT')
    original_object.select_set(state=True)
    context.view_layer.objects.active = original_object

    bpy.ops.object.duplicate()
    object = context.active_object

    object.rotation_euler.x = math.radians(90)
    object.rotation_euler.z = math.radians(180)
    object.scale.x = -1
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # even though collision did not contain normals, this will help to not make the mesh collision inside out
    try:
        bpy.ops.object.mode_set(mode='EDIT')
    except:
        pass
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')

    object.modifiers.new(name='Triangulate_' + object.name, type='TRIANGULATE')
    bpy.ops.object.modifier_apply(
        modifier='Triangulate_' + object.name, use_selected_objects=True)

    mesh_data = object.data

    vertices = mesh_data.vertices
    faces = mesh_data.polygons

    with open(filepath, 'wb') as f:
        f.write(struct.pack('<I', 5459267))  # signature, CMS\0
        f.write(struct.pack('<I', 5000))  # version

        f.write(struct.pack('<I', len(vertices)))  # vertex_count
        for vert in vertices:
            f.write(struct.pack('<3f', *vert.co))  # vertices

        f.write(struct.pack('<I', len(faces)))  # face_count
        for poly in faces:
            indices = list(poly.vertices)
            for vertex_idx in indices:
                f.write(struct.pack('<H', vertex_idx))  # faces

    bpy.data.objects.remove(object)

    original_object.select_set(True)
    context.view_layer.objects.active = original_object

    return filepath


from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from bpy_extras.io_utils import ExportHelper


def dynamic_mesh_type(self, context):
    object = context.active_object

    base_items = [
        ('1', 'Animation', 'Mesh with weights. Contains: position, normal, weight'),
        ('0', 'Static', 'Static mesh. Contains: position, normal, UV'),
        ('2', 'Lightmap', 'Static mesh with lightmap. Contains: position, UV, lightmap UV'),
    ]

    try:
        shader_type = object.data.materials[0].get('Shader Type', 'AnimateToonShade')
    except IndexError:
        shader_type = 'AnimateToonShade'

    if shader_type == 'LightMap':
        base_items.insert(0, base_items.pop(2))
    elif shader_type == 'Static':
        base_items.insert(0, base_items.pop(1))

    return base_items


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
        result = export_material(context, self.filepath)
        self.report({'INFO'}, f'File saved "{result}"')
        self.report({'INFO'}, f'File saved "{result}"')

        return {'FINISHED'}


class MeshExport(Operator, ExportHelper):
    """Export mesh into Lost Saga Mesh (.msh). Experimental"""
    bl_idname = "io3d.mesh_export"
    bl_label = "Export mesh into Lost Saga Mesh (.msh)"

    filename_ext = ".msh"

    filter_glob: StringProperty(
        default="*.msh",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # normalize_weights: BoolProperty(
    #     name='Normalize Weights',
    #     description='When enabled, mesh will be normalized first before exporting',
    #     default=True,
    # )

    mesh_type: EnumProperty(
        name="Mesh Type",
        description="Type of mesh that will be exported into",
        items=dynamic_mesh_type,
    )

    normals: BoolProperty(
        name='Normals',
        description='Mesh normals',
        default=True,
    )

    uv: BoolProperty(
        name='UV',
        description='Mesh main UVmap',
        default=True,
    )

    uv1: BoolProperty(
        name='Lightmap UV',
        description='Mesh Lightmap UV',
        default=True,
    )

    weights: BoolProperty(
        name='Weights',
        description='Mesh vertex groups that contain weights',
        default=True,
    )

    def draw(self, context):
        msh_props = context.scene.io3d_msh_props

        layout = self.layout
        col = layout.column()
        col.prop(msh_props, 'surpress_split')

        # col = layout.column()
        # col.enabled = (bool(self.mesh_type == '1'))
        # col.prop(self, "normalize_weights")

        col.separator(type='LINE')

        col = layout.column()
        col.prop(self, "mesh_type")

        col = layout.column()
        col.enabled = (bool(self.mesh_type in ('0', '1')))
        col.prop(self, "normals")

        col = layout.column()
        col.prop(self, "uv")

        col = layout.column()
        col.enabled = (bool(self.mesh_type == '2'))
        col.prop(self, "uv1")

        col = layout.column()
        col.enabled = (bool(self.mesh_type == '1'))
        col.prop(self, "weights")

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        surpress_split = context.scene.io3d_msh_props.surpress_split
        result = export_mesh(context, self.filepath, surpress_split, False, self.mesh_type, self.normals, self.uv, self.uv1, self.weights)
        self.report({'INFO'}, f'File saved "{result}"')

        return {'FINISHED'}


class PreviewSplit(Operator):
    """Create a duplicate object that preview the UV as if they were being displayed in-game"""
    bl_idname = "io3d.preview_split"
    bl_label = "Preview UV as if they were exported to game"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        surpress_split = context.scene.io3d_msh_props.surpress_split
        return export_mesh(context, None, surpress_split, True, 0, None, None, None, None)


class CollExport(Operator, ExportHelper):
    """Export mesh into Lost Saga Collision Mesh (.cms). cms"""
    bl_idname = "io3d.collision_mesh_export"
    bl_label = "Export mesh into Lost Saga Collision Mesh (.cms)"

    filename_ext = ".cms"

    filter_glob: StringProperty(
        default="*.cms",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        result = export_collision(context, self.filepath)
        self.report({'INFO'}, f'File saved "{result}"')

        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(MatExport.bl_idname, text="Lost Saga Material (.txt)", icon='MATERIAL')
    self.layout.operator(MeshExport.bl_idname, text="Lost Saga Mesh (.msh)", icon='OUTLINER_OB_MESH')
    self.layout.operator(CollExport.bl_idname, text="Lost Saga Collision Mesh (.cms)", icon='CUBE')


def register():
    bpy.utils.register_class(MatExport)
    bpy.utils.register_class(MeshExport)
    bpy.utils.register_class(PreviewSplit)
    bpy.utils.register_class(CollExport)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(MatExport)
    bpy.utils.unregister_class(PreviewSplit)
    bpy.utils.unregister_class(MeshExport)
    bpy.utils.unregister_class(CollExport)