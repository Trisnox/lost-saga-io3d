import bpy
import bmesh
import math
import pathlib
import struct

from ...classes.seeker import Seeker
from ...classes.mesh import MeshData, BlendWeight
    
def is_mesh_file(bytes):
    return bytes == 4739917

def import_mesh(context: bpy.types.Context, filepath: str, resource_folder: str = None):
    IOFVF_POSITION	= 1<<0
    IOFVF_POSITION2	= 1<<1
    IOFVF_POSITIONW = 1<<2
    IOFVF_WEIGHTS	= 1<<3
    IOFVF_INDICES	= 1<<4
    IOFVF_NORMAL	= 1<<5
    IOFVF_COLOR0	= 1<<6
    IOFVF_COLOR1	= 1<<7
    IOFVF_UV0		= 1<<8
    IOFVF_UV1		= 1<<9
    IOFVF_UV2		= 1<<10
    IOFVF_UV3		= 1<<11
    IOFVF_TANGENT	= 1<<12
    IOFVF_BINORMAL	= 1<<13
    IOFVF_END       = 1<<14
    
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
    mesh_type = struct.unpack('<I', msh[s.o:s.i])[0] # It uses its own enum, likely 4 bytes
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
    if vertex_mask & IOFVF_POSITION:
        position = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
        
    if vertex_mask & IOFVF_NORMAL:
        normal = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
        
    if vertex_mask & IOFVF_TANGENT:
        tangent_list = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
        
    if vertex_mask & IOFVF_BINORMAL:
        normal_list = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
        
    if vertex_mask & IOFVF_COLOR0:
        vertex_color = [struct.unpack('<L', msh[s.o:s.L])[0] for _ in range(vertices)]
        
    if vertex_mask & IOFVF_UV0:
        texture_uv = [struct.unpack('<2f', msh[s.o:s.v2]) for _ in range(vertices)]
        
    if vertex_mask & IOFVF_UV1:
        light_texture_uv = [struct.unpack('<2f', msh[s.o:s.v2]) for _ in range(vertices)]
    
    biped_list = []
    weights = []
    if vertex_mask & IOFVF_WEIGHTS:
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
    
    # Not implemented
    billboard_center = []
    if vertex_mask & IOFVF_POSITION2:
        billboard_center = [struct.unpack('<3f', msh[s.o:s.vpos]) for _ in range(vertices)]
    
    # Faces was constructed using WORD, which is equivalent to unsigned short
    face_count = struct.unpack('<I', msh[s.o:s.i])[0]
    faces = [struct.unpack('<H', msh[s.o:s.H])[0] for _ in range(face_count*3)]
    
    # Not implemented
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
        normal = [(n[0], -n[2], n[1]) for n in normal]
        mesh_data.normals_split_custom_set_from_vertices(normal)

    if texture_uv:
        mesh_data.uv_layers.new(name="UVMap")
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
    
    mesh_object.rotation_euler.x = math.radians(90)
    mesh_object.rotation_euler.z = math.radians(180)
    mesh_object.scale.x = -1.0
    bpy.ops.object.transform_apply(location = False, rotation = True, scale = True)
    
    def split_mesh():
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
            
            bpy.ops.object.make_links_data(type='MATERIAL')
            separated_mesh = context.view_layer.objects.selected[-1]
            separated_mesh.name = mesh_name + '_' + str(index)
            ebm.free()

    if not resource_folder:
        if len(submesh) >= 2:
            split_mesh()
        return {'FINISHED'}
    
    def create_material():
        material = bpy.data.materials.new(name=mesh_name)
        material.use_nodes = True
        mesh_object.data.materials.append(material)
            
        texture = bpy.data.images.load(str(texture_path))
        texture_slot = material.node_tree.nodes.new('ShaderNodeTexImage')
        texture_slot.location = (-300.0, 300.0)
        texture_slot.image = texture
        
        principled = material.node_tree.nodes['Principled BSDF']
        links = material.node_tree.links
        links.new(texture_slot.outputs['Color'], principled.inputs['Base Color'])
    
    texture_path = pathlib.Path(resource_folder)
    texture_path = texture_path.joinpath('texture') if not str(texture_path).endswith('texture') else texture_path
    texture_path = texture_path.joinpath(mesh_name + '.dds')
    # Alternative solution: link material data
    if texture_path.exists():
        if 'body' in mesh_name:
            material = bpy.data.materials.get(mesh_name)
            if material:
                mesh_object.data.materials.append(material)
            else:
                create_material()
        else:
            create_material()
    # Hand usually uses their body texture, so we'll use their body texture if there are any
    #
    elif 'hand' in mesh_name:
        mesh_name = mesh_name.replace('hand', 'body')
        material = bpy.data.materials.get(mesh_name)
        if material:
            mesh_object.data.materials.append(material)
        else:
            create_material()
    
    if len(submesh) >= 2:
        split_mesh()
    
    return {'FINISHED'}

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
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
    
    files: CollectionProperty(type=bpy.types.PropertyGroup)
    
    def execute(self, context):
        path = pathlib.Path(self.filepath)
        folder = path.parent
        for file in self.files:
            filepath = str(folder.joinpath(file.name))
            import_mesh(context, filepath, context.scene.io3d_resource_path.path)
            
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(LosaMesh.bl_idname, text="Lost Saga Mesh (.msh)", icon='OUTLINER_OB_MESH')

def register():
    bpy.utils.register_class(LosaMesh)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(LosaMesh)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)