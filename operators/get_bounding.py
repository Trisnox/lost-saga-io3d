import bpy
import math
import mathutils
import subprocess

def get_bounding(context: bpy.types.Context):
    original_objects = context.selected_objects
    bpy.ops.object.duplicate()

    for object in context.selected_objects:
        if not object.type == 'MESH':
            continue

        object.rotation_euler.x = math.radians(90)
        object.rotation_euler.z = math.radians(180)
        object.scale.x = -1
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        try:
            bpy.ops.object.mode_set(mode='EDIT')
        except:
            pass
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.mode_set(mode='OBJECT')

    all_corners = []
    for object in context.selected_objects:
        bbox_corners = [object.matrix_world @ mathutils.Vector(corner) for corner in object.bound_box]
        all_corners.extend(bbox_corners)
    
    min_x = min(corner.x for corner in all_corners)
    min_y = min(corner.y for corner in all_corners)
    min_z = min(corner.z for corner in all_corners)
    
    max_x = max(corner.x for corner in all_corners)
    max_y = max(corner.y for corner in all_corners)
    max_z = max(corner.z for corner in all_corners)
    
    center = mathutils.Vector(((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2))
    
    max_distance = 0
    for object in context.selected_objects:
        if not object.type == 'MESH':
            continue

        for vertex in object.data.vertices:
            world_vertex = object.matrix_world @ vertex.co
            distance = (world_vertex - center).length
            max_distance = max(max_distance, distance)

    text = f"""#AABOX
{min_x:.2f} {min_y:.2f} {min_z:.2f}
{max_x:.2f} {max_y:.2f} {max_z:.2f}
#SPHERE
{center.x:.2f} {center.y:.2f} {center.z:.2f}
{max_distance:.2f}
"""

    try:
        subprocess.run(['clip'], input=text, text=True)
    except FileNotFoundError:
        return False, text

    for object in context.selected_objects:
        bpy.data.objects.remove(object)
    
    for object in original_objects:
        object.select_set(True)

    context.view_layer.objects.active = original_objects[0]

    return True, text


from bpy.types import Operator


class GetBounding(Operator):
    """Get mesh(es) bounding box and its sphere radius"""
    bl_idname = "io3d.get_bounding"
    bl_label = "Get mesh(es) bounding and its sphere radius and copy them to clipboard."

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        status, result = get_bounding(context)

        if status == False:
            def draw(self, context):
                self.layout.label(text=f'Text cannot be copied to clipboard')

            context.window_manager.popup_menu(draw, title='ERROR | CANNOT COPY TO CLIPBOARD', icon='ERROR')
        else:
            def draw(self, context):
                self.layout.label(text=f'Text successfully copied to clipboard')

            context.window_manager.popup_menu(draw, title='INFO | COPIED TO CLIPBOARD', icon='INFO')

        self.report({'INFO'}, result)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(GetBounding)


def unregister():
    bpy.utils.unregister_class(GetBounding)
