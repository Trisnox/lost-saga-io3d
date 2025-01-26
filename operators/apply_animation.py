import bpy


def apply_animation(context: bpy.types.Context, fps: int, frame_offset: int):
    if context.active_object.type == 'ARMATURE':
        mode = 'ARMATURE'
        try:
            bpy.ops.object.mode_set(mode='POSE')
        except:
            pass

        armature_object = context.active_object
        bones_iter = armature_object.pose.bones
    else:
        mode = 'EMPTY'
        while True:
            res = bpy.ops.object.select_grouped(extend=True, type='PARENT')
            if res == {'CANCELLED'}:
                break

        root = context.object
        bones_iter = [root] + [_ for _ in root.children_recursive]

    # Very poor check, but oh well...
    if not bones_iter[0].get('Quaternion Rest W'):
        raise RuntimeError('Object is not Advanced Lost Saga Skeleton')

    bones = {}
    for bone in bones_iter:
        key = bone.name.rsplit('.', 1)[0]
        bones[key] = bone

    # Bad idea, non-humanoid bones, such as effects, may have different names
    # if not 'Bip01' in bones:
    #     raise RuntimeError('Object is not Lost Saga Skeleton')

    bone_missing = False
    not_found = []
    armature_warning = False

    if mode == 'ARMATURE':
        action = bpy.data.actions.get(armature_object.name, None)
        if not action:
            action = bpy.data.actions.new(name=armature_object.name)
            armature_warning = True

        if not armature_object.animation_data:
            armature_object.animation_data_create()

        armature_object.animation_data.action = action

    anim_data = context.scene.io3d_animation_data
    keyframe_data = anim_data.entry[anim_data.active_entry_index]
    # frames = keyframe_data.frames
    frames = int(keyframe_data.total_time/fps*1000) # ver8 fix
    for biped_name, data in keyframe_data:
        if biped_name in not_found:
            continue

        if mode == 'EMPTY':
            bpy.ops.object.select_all(action='DESELECT')

        try:
            bone = bones[biped_name]
        except KeyError:
            bone_missing = True
            not_found.append(biped_name)
            print(f'Warning, bone {biped_name} is not found')
            continue

        if mode == 'EMPTY':
            bone.select_set(True)
            context.view_layer.objects.active = bone

        bone.rotation_mode = 'QUATERNION'
        bone_fcurves_location = []
        bone_fcurves_rotation = []

        if mode == 'EMPTY':
            action = bpy.data.actions.get(bone.name, None)
            if not action:
                action = bpy.data.actions.new(name=bone.name)
                is_action_new = True

            if not bone.animation_data:
                bone.animation_data_create()

            bone.animation_data.action = action

        data_path_location = 'location' if mode == 'EMPTY' else f'pose.bones["{bone.name}"].location'
        data_path_rotation = 'rotation_quaternion' if mode == 'EMPTY' else f'pose.bones["{bone.name}"].rotation_quaternion'

        bone_fcurves_location = []
        bone_fcurves_rotation = []

        for fcurve in action.fcurves:
            if fcurve.data_path == data_path_location:
                bone_fcurves_location.append(fcurve)
            elif fcurve.data_path == data_path_rotation:
                bone_fcurves_rotation.append(fcurve)
        if not bone_fcurves_location:
            bone_fcurves_location = [action.fcurves.new(data_path=data_path_location, index=i, action_group=bone.name) for i in range(3)]
        if not bone_fcurves_rotation:
            bone_fcurves_rotation = [action.fcurves.new(data_path=data_path_rotation, index=i, action_group=bone.name) for i in range(4)]

        # There is a high certainty that ver8 animation cause out of index error
        # Instead of allocating keyframe points based off the length of the keyframe data,
        # it will allocate using the last entry keyframe instead
        for index, fcurve in enumerate(bone_fcurves_location):
            fcurve.keyframe_points.add(frames + frame_offset)

            for frame, location, rotation in data:
                frame = int(frame*fps/1000) + frame_offset

                keyframe = fcurve.keyframe_points[frame]
                keyframe.co = frame, location[index]
                keyframe.interpolation = 'LINEAR'

            fcurve.update()

        for index, fcurve in enumerate(bone_fcurves_rotation):
            fcurve.keyframe_points.add(frames + frame_offset)

            for frame, location, rotation in data:
                frame = int(frame*fps/1000) + frame_offset

                keyframe = fcurve.keyframe_points[frame]
                keyframe.co = frame, rotation[index]
                keyframe.interpolation = 'LINEAR'

            fcurve.update()

        # Alright
        # Since the initial pos/rot is not the same as rest position, I had to make it so that it uses rest pos/rot for the frame 0 only
        # Blender will just insert frame regardless at 0th frame, and the values would be 0, which may mess up some animation
        rest_position = [bone['Position Rest X'], bone['Position Rest Y'], bone['Position Rest Z']]
        rest_rotation = [bone['Quaternion Rest W'], bone['Quaternion Rest X'], bone['Quaternion Rest Y'], bone['Quaternion Rest Z']]

        for index, fcurve in enumerate(bone_fcurves_location):
            fcurve.keyframe_points.add(0)
            keyframe = fcurve.keyframe_points[0]
            keyframe.co = 0, rest_position[index]
            keyframe.interpolation = 'LINEAR'

        fcurve.update()

        for index, fcurve in enumerate(bone_fcurves_rotation):
            keyframe = fcurve.keyframe_points[0]
            keyframe.co = 0, rest_rotation[index]
            keyframe.interpolation = 'LINEAR'

        fcurve.update()

    if bone_missing:
        def draw(self, context):
            self.layout.label(text='One or more bone are not found, please check console for more info')

        context.window_manager.popup_menu(draw, title='WARNING | MISSING BONE', icon='WARNING_LARGE')

    if armature_warning:
        def draw(self, context):
            self.layout.label(text='You are attempting to apply animation into armature. It is not recommended due to offset issues.')

        context.window_manager.popup_menu(draw, title='INFO', icon='INFO')

    return {'FINISHED'}


from bpy.types import Operator


class ApplyAnimation(Operator):
    """Apply animation into empties/armature"""
    bl_idname = "io3d.apply_animation" 
    bl_label = "Apply animation into empties/armature"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type in ('EMPTY', 'ARMATURE')

    def execute(self, context):
        anim_prop = context.scene.io3d_anim_props
        fps = context.scene.render.fps if anim_prop.use_current_fps else anim_prop.override_fps
        if anim_prop.insert_at == 'CURRENT':
            frame_offset = context.scene.frame_current 
        elif anim_prop.insert_at == 'FIRST':
            frame_offset = 0
        else:
            frame_offset = anim_prop.frame_set

        return apply_animation(context, fps, frame_offset)

def register():
    bpy.utils.register_class(ApplyAnimation)

def unregister():
    bpy.utils.unregister_class(ApplyAnimation)
