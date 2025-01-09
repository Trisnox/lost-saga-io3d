import bpy

def losa_to_blender(name):
    name = name.removeprefix('Bip01').strip()
    
    if not name:
        return 'root'
    
    if name.startswith('L '):
        name = name[2:] + '.L'
    elif name.startswith('R '):
        name = name[2:] + '.R'
    
    return name

def blender_to_losa(name):
    if name == 'root':
        return 'Bip01'
    
    if name.endswith('.L'):
        name = 'L ' + name[:-2]
    elif name.endswith('.R'):
        name = 'R ' + name[:-2]
    
    return 'Bip01 ' + name

def rename_bones(context: bpy.context):
    armature = context.view_layer.objects.active
    armature_data = armature.data
    for bone in armature_data.bones:
        if bone.name.startswith('Bip01'):
            bone.name = losa_to_blender(bone.name)
        else:
            bone.name = blender_to_losa(bone.name)
        
    return {'FINISHED'}


from bpy.types import Operator


class BonesRename(Operator):
    """Rename selected armature bones/mesh vertex groups into Blender, or Lost Saga"""
    bl_idname = "io3d.rename_bones" 
    bl_label = "Rename bones/vertex group into Blender or Lost Saga"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'ARMATURE'
    
    def execute(self, context):
        return rename_bones(context)

def register():
    bpy.utils.register_class(BonesRename)

def unregister():
    bpy.utils.unregister_class(BonesRename)