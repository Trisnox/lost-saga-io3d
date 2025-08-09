import bpy
import bmesh


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def split_mesh(context: bpy.types.Context, threshold: int):
    original_objects = context.selected_objects
    bpy.ops.object.duplicate()
    new_objects = []

    for object in context.selected_objects:
        mesh_data = object.data
        mesh_name = object.name[:-4]
        object.name = mesh_name + '_chunk_1'

        new_objects.append(object)
        
        if len(mesh_data.polygons) <= threshold:
            def draw(self, context):
                self.layout.label(text=f'{mesh_name} is already have less face than threshold')
            
            bpy.data.objects.remove(object)
            context.window_manager.popup_menu(draw, title='INFO | INSUFFICIENT POLYGONS', icon='INFO')
            return {'FINISHED'}
        
        face_indices = list(range(len(mesh_data.polygons)))
        face_chunks = list(chunks(face_indices, threshold))

        for index, poly_chunk in reversed(list(enumerate(face_chunks[1:], 2))):
            bpy.ops.object.select_all(action='DESELECT')
            object.select_set(True)
            context.view_layer.objects.active = object

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(type='FACE')

            bm = bmesh.from_edit_mesh(mesh_data)
            bm.faces.ensure_lookup_table()
            bm.select_mode = {'FACE'}
            bm.select_flush_mode()

            for face_idx in poly_chunk:
                if face_idx < len(bm.faces):
                    bm.faces[face_idx].select = True

            # bmesh.update_edit_mesh(mesh_data)
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode='OBJECT')

            separated_mesh = context.view_layer.objects.selected[-1]
            separated_mesh.name = mesh_name + '_chunk_' + str(index)
            new_objects.append(separated_mesh)
            bm.free()


    for object in original_objects:
        object.hide_set(True)

    for object in new_objects:
        object.select_set(True)

    return {'FINISHED'}


from bpy.types import Operator


class SplitMesh(Operator):
    """Split mesh based off threshold. Useful to avoid hitting vert/face limit. Non destructive."""
    bl_idname = "io3d.split_mesh"
    bl_label = "Split mesh based off threshold."

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'MESH'

    def execute(self, context):
        threshold = context.scene.io3d_msh_props.split_threshold
        return split_mesh(context, threshold)


def register():
    bpy.utils.register_class(SplitMesh)


def unregister():
    bpy.utils.unregister_class(SplitMesh)