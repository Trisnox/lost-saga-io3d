import bpy
import math
import mathutils


def retarget_animation(context: bpy.types.Context):
    armature_object = context.active_object
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass

    # bpy.ops.object.select_all(action='DESELECT')
    # armature_object.select_set(True)
    # context.view_layer.objects.active = armature_object
    # armature_object.rotation_euler.x = math.radians(-90)
    # armature_object.rotation_euler.y = math.radians(180)
    # armature_object.scale.x = -1
    # bpy.ops.object.transform_apply(rotation=True, scale=True)

    bpy.ops.object.mode_set(mode='POSE')

    anim_data = armature_object.animation_data
    if not anim_data:
        raise RuntimeError('Armature does not have animation data')
    
    action = anim_data.action
    if not anim_data:
        raise RuntimeError('Armature does not have action data')

    bones = armature_object.pose.bones
    if not 'Bip01' in bones:
        raise RuntimeError('Cannot detect Lost Saga Skeleton. Try rename bones first')
    
    keyframe_data = {}
    total_keyframe = 0
    latest_keyframe = 0
    for bone in bones:
        bone_name = bone.name

        keyframe_data[bone_name] = []

        data_path_rotation = f'pose.bones["{bone_name}"].rotation_quaternion'

        bone_fcurves_rotation = []

        for fcurve in action.fcurves:
            if fcurve.data_path == data_path_rotation:
                bone_fcurves_rotation.append(fcurve)

        # It is expected that the frames and rotation comes in pairs
        # If not, then the user needs to bake their animation first
        frames = []
        rotation_quaternion = []
        for index, fcurve in enumerate(bone_fcurves_rotation):
            tmp_quaternion = []
            keyframes = fcurve.keyframe_points

            total_keyframe = len(keyframes) if total_keyframe < len(keyframes) else total_keyframe

            for keyframe in keyframes:
                frame, rotation = keyframe.co
                latest_keyframe = frame if latest_keyframe < frame else frame
                tmp_quaternion.append(rotation)
                if index == 3:
                    frames.append(frame)

            rotation_quaternion.append(tmp_quaternion)
        
        rotation_quaternion = list(zip(*rotation_quaternion))

        if len(frames) != len(rotation_quaternion):
            raise RuntimeError('Length of frames and Quaternion rotation is uneven. Try baking the animation first')
        
        for frame, rotation in zip(frames, rotation_quaternion):
            frame -= 1.0
            frame = int(round((frame / context.scene.render.fps) * 1000))
            keyframe_data[bone_name].append((frame, mathutils.Vector(), rotation))
    
    total_time = int(round((total_keyframe / context.scene.render.fps) * 1000))
    animation = {armature_object.name + '_retarget': keyframe_data, 'frames': total_keyframe, 'total_time': total_time, 'is_retarget': True}
    context.scene.io3d_animation_data.append(animation)

    # bpy.ops.object.mode_set(mode='OBJECT')
    # bpy.ops.object.select_all(action='DESELECT')
    # armature_object.select_set(True)
    # context.view_layer.objects.active = armature_object
    # armature_object.rotation_euler.x = math.radians(-90)
    # armature_object.rotation_euler.y = math.radians(180)
    # armature_object.scale.x = -1
    # bpy.ops.object.transform_apply(rotation=True, scale=True)


    return {'FINISHED'}


from bpy.types import Operator


class RetargetAnim(Operator):
    """Retarget animation from lite skeleton. Animation will be stored inside panel"""
    bl_idname = "io3d.anim_retarget" 
    bl_label = "Retarget animation"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'ARMATURE'

    def execute(self, context):
        return retarget_animation(context)

def register():
    bpy.utils.register_class(RetargetAnim)

def unregister():
    bpy.utils.unregister_class(RetargetAnim)
