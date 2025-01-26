import bpy
import mathutils


def reset_rest(context: bpy.types.Context):
    bones = context.selected_pose_bones if context.object.type == 'ARMATURE' else [_ for _ in context.selected_objects if _.type == 'EMPTY']

    for bone in bones:
        location = mathutils.Vector((bone['Position Rest X'], bone['Position Rest Y'], bone['Position Rest Z']))
        rotation = mathutils.Quaternion((bone['Quaternion Rest W'], bone['Quaternion Rest X'], bone['Quaternion Rest Y'], bone['Quaternion Rest Z']))
        bone.location = location
        bone.rotation_quaternion = rotation

    return {'FINISHED'}


from bpy.types import Operator


class ResetRest(Operator):
    """Reset bone position/rotation into its rest position"""
    bl_idname = "io3d.reset_rest"
    bl_label = "Reset bone to rest position/rotation"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if not object:
            return False
        
        if object.type == 'ARMATURE':
            return context.selected_pose_bones
        else:
            return object.type == 'EMPTY'

    def execute(self, context):
        return reset_rest(context)


def register():
    bpy.utils.register_class(ResetRest)


def unregister():
    bpy.utils.unregister_class(ResetRest)
