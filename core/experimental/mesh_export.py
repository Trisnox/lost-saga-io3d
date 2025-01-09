import bpy
import bmesh
import struct
import math
import mathutils
from mathutils import Vector, Matrix

def convert_to_y_up_left_handed(vector):
    # Z-up to Y-up: (X, Y, Z) -> (X, Z, -Y)
    # Right to left handed: Mirror X
    return mathutils.Vector((-vector.x, vector.z, -vector.y))

def convert_normal_to_y_up_left_handed(normal):
    # Same transformation as positions, but don't mirror X for normals
    return mathutils.Vector((normal.x, normal.z, -normal.y))

def calculate_bounding_box(obj):
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    
    converted_corners = [convert_to_y_up_left_handed(corner) for corner in bbox_corners]
    
    bbox_min = Vector(map(min, zip(*converted_corners)))
    bbox_max = Vector(map(max, zip(*converted_corners)))
    
    center = (bbox_max + bbox_min) / 2
    radius = max((bbox_max - center).length, (bbox_min - center).length)
    
    return bbox_min, bbox_max, radius

def export_mesh(context: bpy.context, filepath: str):
    main_mesh = context.view_layer.objects.active
    bpy.ops.object.select_all(action='DESELECT')
    main_mesh.select_set(True)
    context.view_layer.objects.active = main_mesh
    
    # Alternative solution would be main_mesh.copy(), and then link the copy
    bpy.ops.object.duplicate()
    mesh_object = context.view_layer.objects.active
    mesh_object.rotation_euler.z = math.radians(180)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    mesh_object.modifiers.new(name='Triangulate_' + mesh_object.name, type='TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier='Triangulate_' + mesh_object.name)
    
    mesh_data = mesh_object.data
    
    bm = bmesh.new()
    bm.from_mesh(mesh_data)
    bm.edges.ensure_lookup_table()
    
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            angle = math.degrees(edge.calc_face_angle())
            if angle > 30: # angle threshold
                edge.seam = True
    
    bmesh.ops.split_edges(bm, edges=[e for e in bm.edges if e.seam])

    bm.to_mesh(mesh_data)
    bm.free()
    
    vertex_mask = 313 # position, normal, uv, weights
    
    has_positions = True
    has_normals = mesh_data.has_custom_normals or mesh_data.use_auto_smooth
    has_uvs = len(mesh_data.uv_layers) > 0
    has_weights = len(mesh_object.vertex_groups) > 0
    has_vertex_colors = False
    
    #if has_positions:
    #    vertex_mask |= IOFVF_POSITION
    #if has_normals:
    #    vertex_mask |= IOFVF_NORMAL
    #if has_uvs:
    #    vertex_mask |= IOFVF_UV0
    #if has_weights:
    #    vertex_mask |= IOFVF_WEIGHTS
    #if has_vertex_colors:
    #    vertex_mask |= IOFVF_COLOR0
    
    bbox_min, bbox_max, bound_radius = calculate_bounding_box(mesh_object)
    
    with open(filepath, 'wb') as f:
        f.write(struct.pack('<I', 4739917))  # Signature
        f.write(struct.pack('<I', 2000))  # Version
        f.write(struct.pack('<I', 1)) # mesh_type
        f.write(struct.pack('<L', vertex_mask))
        
        f.write(struct.pack('<3f', *bbox_min))
        f.write(struct.pack('<3f', *bbox_max))
        f.write(struct.pack('<f', bound_radius))
        
        f.write(struct.pack('<I', 1)) # Submesh count
        
        vertex_count = len(mesh_data.vertices)
        face_count = len(mesh_data.polygons)
        
        f.write(struct.pack('<I', 0))  # min_index
        f.write(struct.pack('<I', vertex_count))  # vertex_count
        f.write(struct.pack('<I', 0))  # index_start
        f.write(struct.pack('<I', face_count))  # face_count
        
        f.write(struct.pack('<I', vertex_count))
        
        if has_positions:
            for vertex in mesh_data.vertices:
                game_pos = convert_to_y_up_left_handed(vertex.co)
                f.write(struct.pack('<3f', *game_pos))

        if has_normals:
            for x in mesh_data.vertex_normals:
                normal = x.vector
                game_normal = convert_normal_to_y_up_left_handed(normal)
                f.write(struct.pack('<3f', *game_normal))

        if has_uvs:
            uv_layer = mesh_data.uv_layers[0].data
            vertex_uvs = {}
            
            for poly in mesh_data.polygons:
                for vert_idx, loop_idx in zip(poly.vertices, poly.loop_indices):
                    vertex_uvs[vert_idx] = uv_layer[loop_idx].uv
            
            for vertex_idx in range(vertex_count):
                if vertex_idx in vertex_uvs:
                    uv = vertex_uvs[vertex_idx]
                    f.write(struct.pack('<2f', uv.x, 1.0 - uv.y))
                else:
                    f.write(struct.pack('<2f', 0.0, 0.0))
                    
        if has_weights:
            biped_list = [group.name for group in mesh_object.vertex_groups]
            f.write(struct.pack('<I', len(biped_list)))
            
            for name in biped_list:
                name_bytes = name.encode('utf-8')
                f.write(struct.pack('<I', len(name_bytes)))
                f.write(name_bytes)

            for vertex in mesh_data.vertices:
                weights = []
                indices = []
                
                for group in vertex.groups:
                    weights.append(group.weight)
                    indices.append(group.group)
                    if len(weights) >= 4:
                        break
                
                while len(weights) < 4:
                    weights.append(0.0)
                    indices.append(0)
                
                f.write(struct.pack('<4f', *weights))
                f.write(struct.pack('<4f', *[float(i) for i in indices]))
        
        # # Write vertex colors
        #if has_vertex_colors:
        #    color_layer = mesh_data.vertex_colors[0].data
        #    for poly in mesh_data.polygons:
        #        for loop_idx in poly.loop_indices:
        #            color = color_layer[loop_idx].color
        #            r = int(color[0] * 255)
        #            g = int(color[1] * 255)
        #            b = int(color[2] * 255)
        #            a = int(color[3] * 255) if len(color) > 3 else 255
        #            color_uint = (a << 24) | (b << 16) | (g << 8) | r
        #            f.write(struct.pack('<L', color_uint))

        f.write(struct.pack('<I', len(mesh_data.polygons)))
        for poly in mesh_data.polygons:
            indices = list(poly.vertices)[::-1]
            for vertex_idx in indices:
                f.write(struct.pack('<H', vertex_idx))
    
    bpy.data.objects.remove(mesh_object)
    return {'FINISHED'}


from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


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

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        return export_mesh(context, self.filepath)


def menu_func_export(self, context):
    self.layout.operator(MeshExport.bl_idname, text="Lost Saga Mesh (.msh)")

def register():
    bpy.utils.register_class(MeshExport)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(MeshExport)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()