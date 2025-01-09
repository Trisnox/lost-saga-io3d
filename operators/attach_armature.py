import bpy

def attach_armature(context: bpy.context):
    selected = context.selected_objects

    meshes = [_ for _ in selected if _.type == 'MESH']
    armature = [_ for _ in selected if _.type == 'ARMATURE']
    
    if not armature:
        raise RuntimeError('No armature is selected')
    
    if not meshes:
        raise RuntimeError('No mesh is selected')
    
    armature = armature[0]

    for mesh in meshes:
        modifier = mesh.modifiers.new(name='Armature', type='ARMATURE')
        modifier.object = armature
        
    return {'FINISHED'}


from bpy.types import Operator


class ArmatureAttach(Operator):
    """Attach meshes into selected armature"""
    bl_idname = "io3d.armature_attach" 
    bl_label = "Attach objects into armature"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type in ('MESH', 'ARMATURE')

    def execute(self, context):
        return attach_armature(context)

def register():
    bpy.utils.register_class(ArmatureAttach)

def unregister():
    bpy.utils.unregister_class(ArmatureAttach)
