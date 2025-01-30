import bpy


def mirror_pose(context: bpy.types.Context):
    active_object = context.active_object
    anim_props = context.scene.io3d_anim_props
    mirror_operation = anim_props.mirror_target

    if active_object.type == 'ARMATURE':
        selected_bones = context.selected_pose_bones
        bones = context.active_object.pose.bones
    else:
        selected_bones = context.selected_objects
        while True:
            res = bpy.ops.object.select_grouped(extend=True, type='PARENT')
            if res == {'CANCELLED'}:
                break

        root = context.object
        if not any(root.name.startswith(bone_name) for bone_name in ('Bip01', 'origin_correction')):
            raise RuntimeError('Object is not Lost Saga skeleton')

        bones = [root] + [_ for _ in root.children_recursive]
    
    if not bones[0].get('Quaternion Rest W'):
        if active_object.type == 'ARMATURE':
            raise RuntimeError('Not an Advanced Lost Saga Skeleton, use X-Axis mirror instead')
        else:
            raise RuntimeError('Object is not Advanced Lost Saga Skeleton')

    bone_names = [bone.name for bone in selected_bones]
    mirrored_bone_names = []
    side_check = []
    for bone_name in bone_names:
        if bone_name.startswith('origin_correction'):
            continue
        elif bone_name.startswith('Bip01'):
            name = bone_name.removeprefix('Bip01').strip()
            if not name:
                continue

            if name.startswith('L '):
                bone_name = bone_name.replace(' L ', ' R ')
                side_check.append('L')
            elif name.startswith('R '):
                bone_name = bone_name.replace(' R ', ' L ')
                side_check.append('R')
            else:
                bone_names.remove(bone_name)
                continue

            mirrored_bone_names.append(bone_name)
        else: # assuming they're renaming the bones
            if name.endswith('.L'):
                bone_name = bone_name[:-1] + 'R'
                side_check.append('L')
            elif name.endswith('.R'):
                bone_name = bone_name[:-1] + 'L'
                side_check.append('R')
            else:
                bone_names.remove(bone_name)
                continue

            mirrored_bone_names.append(bone_name)

    if all(x in side_check for x in ('L', 'R')):
        raise RuntimeError('Cannot mirror pose due to selected bones having both left and right')

    if not mirrored_bone_names:
        def draw(self, context):
            self.layout.label(text='No bones to mirror')

        context.window_manager.popup_menu(draw, title='INFO', icon='INFO')
        return {'FINISHED'}

    if mirror_operation == 'MIRROR':
        bone_iter = zip(mirrored_bone_names, bone_names)
    else:
        bone_iter = zip(bone_names, mirrored_bone_names)

    for bone_target_name, bone_source_name in bone_iter:
        bone_target = bones.get(bone_target_name)
        bone_source = bones.get(bone_source_name)

        if anim_props.location:
            bone_target.location = bone_source.location
            bone_target.location.y = -bone_target.location.y

        if anim_props.rotation:
            bone_target.rotation_quaternion = bone_source.rotation_quaternion
            bone_target.rotation_quaternion.x = -bone_target.rotation_quaternion.x
            bone_target.rotation_quaternion.z = -bone_target.rotation_quaternion.z

    return {'FINISHED'}


from bpy.types import Operator


class MirrorPose(Operator):
    """Mirror or copy pose location/rotation from opposing bone or vice versa"""
    bl_idname = "io3d.mirror_pose"
    bl_label = "Mirror poses to/from opposing bones"

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
        return mirror_pose(context)


def register():
    bpy.utils.register_class(MirrorPose)

def unregister():
    bpy.utils.unregister_class(MirrorPose)
