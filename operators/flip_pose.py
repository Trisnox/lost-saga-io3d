import bpy


def flip_pose(context: bpy.types.Context):
    active_object = context.active_object
    if active_object.type == 'ARMATURE':
        bones_iter = active_object.pose.bones
    else:
        while True:
            res = bpy.ops.object.select_grouped(extend=True, type='PARENT')
            if res == {'CANCELLED'}:
                break

        root = context.object
        bones_iter = [root] + [_ for _ in root.children_recursive]
    
    bones_rotation = {bone.name:bone.rotation_quaternion.copy() for bone in bones_iter}
    left_right_bones = []
    for bone in bones_iter:
        bone_name = bone.name
        if bone_name.startswith('origin_correction'):
            continue

        if bone_name.startswith('Bip01'):
            name = bone_name.removeprefix('Bip01').strip()
            if not name:
                continue

            if name.startswith('L '):
                mirror_bone_name = bone_name.replace(' L ', ' R ')
            elif name.startswith('R '):
                mirror_bone_name = bone_name.replace(' R ', ' L ')
            else:
                left_right_bones.append((bone, None))
                continue

            left_right_bones.append((bone, mirror_bone_name))
        else:
            if name == 'root':
                continue
            
            if name.endswith('.L'):
                mirror_bone_name = bone_name[:-1] + 'R'
            elif name.endswith('.R'):
                mirror_bone_name = bone_name[:-1] + 'L'
            else:
                left_right_bones.append((bone, None))
                continue

            left_right_bones.append((bone, mirror_bone_name))
    
    for bone_target, bone_source in left_right_bones:
        if 'Pelvis' in bone_target.name: # Flipping pelvis bone just make it rotate 180 on z-axis instead
            continue

        if bone_source:
            bone_target.rotation_quaternion = bones_rotation[bone_source]

        bone_target.rotation_quaternion.x = -bone_target.rotation_quaternion.x
        bone_target.rotation_quaternion.z = -bone_target.rotation_quaternion.z

    return {'FINISHED'}


from bpy.types import Operator


class FlipPose(Operator):
    """Flip pose on selected object. Cannot flip bones that doesn't have left/right"""
    bl_idname = "io3d.flip_pose"
    bl_label = "Flip pose"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if not object:
            return False
        
        if object.type == 'ARMATURE':
            return context.selected_pose_bones and context.mode == 'POSE'
        else:
            return object.type == 'EMPTY'

    def execute(self, context):
        return flip_pose(context)


def register():
    bpy.utils.register_class(FlipPose)

def unregister():
    bpy.utils.unregister_class(FlipPose)
