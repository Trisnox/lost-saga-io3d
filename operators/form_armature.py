# https://github.com/artellblender/empties_to_bones

import bpy
import math
import mathutils

def matrix_converter(matrix):
    vpos = matrix.col[1]
    vposMatrix = vpos_to_matrix(vpos)
    roll_matrix = vposMatrix.inverted() @ matrix
    roll = math.atan2(roll_matrix[0][2], roll_matrix[2][2])
    vpos = mathutils.Vector((vpos[0] * 10, vpos[1] * 10, vpos[2] * 10))
    return vpos, roll

def vpos_to_matrix(vpos):
    vector_target = mathutils.Vector((0.0, 0.1, 0.0))
    vpos = vpos.normalized()
    axis = vector_target.cross(vpos)
    if axis.dot(axis) > 0.0000000001:
        axis.normalize()
        theta = vector_target.angle(vpos)
        bMatrix = mathutils.Matrix.Rotation(theta, 3, axis)
    else:
        up_or_down = 1 if vector_target.dot(vpos) > 0 else -1
        bMatrix = mathutils.Matrix.Scale(up_or_down, 3)
        bMatrix[2][2] = 1.0
        
    rMatrix = mathutils.Matrix.Rotation(0, 3, vpos)
    return rMatrix @ bMatrix

def form_armature(context: bpy.types.Context, is_static_call: bool = False, skip_check: bool = False, is_delta: bool = False):
    while True and not skip_check:
        res = bpy.ops.object.select_grouped(extend=True, type='PARENT')
        if res == {'CANCELLED'}:
            break
        
    root = context.object
    if not any(root.name.startswith(bone_name) for bone_name in ('Bip01', 'origin_correction')):
        raise RuntimeError('Object is not Lost Saga skeleton')
    
    empties = [root] + [_ for _ in root.children_recursive]

    if is_delta:
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = root

        for empty in empties:
            empty.select_set(True)
        
        bpy.ops.object.transforms_to_deltas(mode='ALL')

    armature_data = bpy.data.armatures.new('retarget_armature')
    armature_object = bpy.data.objects.new('retarget_armature', armature_data)
    armature_object.show_in_front = True

    context.scene.collection.objects.link(armature_object)
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass

    armature_object.select_set(state=True)
    context.view_layer.objects.active = armature_object

    bpy.ops.object.mode_set(mode='EDIT')

    bones = {}
    for empty in empties:
        bone_name = empty.name.rsplit('.', 1)[0]
        vpos, roll = matrix_converter(empty.matrix_world.to_3x3())
        edit_bone = armature_data.edit_bones.new(bone_name)
        
        edit_bone.head = empty.matrix_world.to_translation()
        edit_bone.tail = edit_bone.head + (vpos)
        edit_bone.roll = roll
        
        bones[bone_name] = edit_bone
        if empty.parent:
            # This problem only occur for mesh armature, since the origin correction needs to be skipped
            # so that it will deform correctly for meshes
            try:
                edit_bone.parent = bones[empty.parent.name.rsplit('.', 1)[0]]
            except KeyError:
                pass

    
    if is_static_call:
        return armature_object
    
    bpy.ops.object.mode_set(mode='POSE')
    for bone, empty in zip(armature_object.pose.bones, empties):
        const = bone.constraints.new('COPY_TRANSFORMS')
        const.target = empty

    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {'FINISHED'}

from bpy.types import Operator


class ArmatureForm(Operator):
    """Form/retarget an armature from empties object"""
    bl_idname = "io3d.retarget" 
    bl_label = "Form/retarget armature from empty object"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'EMPTY'
    
    def execute(self, context):
        return form_armature(context)
    
    @staticmethod
    def generate_with_return(context, skip_check: bool = False, is_delta: bool = False):
        """Used for SKL importing, returns the object of generated armature"""
        return form_armature(context, True, skip_check, is_delta)


def register():
    bpy.utils.register_class(ArmatureForm)

def unregister():
    bpy.utils.unregister_class(ArmatureForm)