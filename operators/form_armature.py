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

def form_armature(context: bpy.context):
    while True:
        res = bpy.ops.object.select_grouped(extend=True, type='PARENT')
        if res == {'CANCELLED'}:
            break
        
    root = context.object
    if not root.name.startswith('Bip01'):
        raise RuntimeError('Object is not Lost Saga skeleton')

    bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
    
    empties = [_ for _ in context.selected_objects if _.type == 'EMPTY']

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
            edit_bone.parent = bones[empty.parent.name]
        
    bpy.ops.object.mode_set(mode='POSE')
    for bone, empty in zip(armature_object.pose.bones, empties):
        const = bone.constraints.new('COPY_TRANSFORMS')
        const.target = empty

    bpy.ops.object.mode_set(mode='OBJECT')
    
    return {'FINISHED'}

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup


class ArmatureForm(Operator):
    """Form/retarget an armature from empties object. Experimental"""
    bl_idname = "io3d.retarget" 
    bl_label = "Form/retarget armature from empty object"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'EMPTY'
    
    def execute(self, context):
        return form_armature(context)

def register():
    bpy.utils.register_class(ArmatureForm)

def unregister():
    bpy.utils.unregister_class(ArmatureForm)