import bpy
import mathutils
import numpy as np


def apply_animation(context: bpy.types.Context, fps: int, frame_offset: int, frame_range: str, frame_start: int, frame_end: int, apply_rest: bool):
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
    is_retarget = keyframe_data.is_retarget
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

        rest_position = [bone['Position Rest X'], bone['Position Rest Y'], bone['Position Rest Z']]
        rest_rotation = [bone['Quaternion Rest W'], bone['Quaternion Rest X'], bone['Quaternion Rest Y'], bone['Quaternion Rest Z']]

        keyframes = []
        new_data = []
        for frame, location, rotation in data:
            frame = int(round((frame*fps) / 1000)) + frame_offset
            if frame_range == 'PARTIAL':
                if not frame_start <= frame - frame_offset <= frame_end:
                    continue
            if is_retarget and apply_rest:
                rest_quaternion = mathutils.Quaternion(rest_rotation)
                w, x, y, z = rotation
                rotation = mathutils.Quaternion((w, -x, -y, z))
                rotation = rest_quaternion @ rotation
                new_data.append((frame, mathutils.Vector(rest_position), rotation))
            keyframes.append(frame)
        data = new_data if new_data else data

        # oops
        # if it were a list, I could insert a rest keyframe at 0th frame if there are no keyframe at 0 frame
        # if not data[0][0] == 0:
        #     data.insert

        bone.rotation_mode = 'QUATERNION'
        bone_fcurves_location = []
        bone_fcurves_rotation = []

        if mode == 'EMPTY':
            action = bpy.data.actions.get(bone.name, None)
            if not action:
                action = bpy.data.actions.new(name=bone.name)

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

        keyframe_count = len(keyframes)
        for index, fcurve in enumerate(bone_fcurves_location):
            current_keyframe_count = len(fcurve.keyframe_points)

            # rotation_list = [rotation for _, _, rotation in data]
            if not current_keyframe_count == 0:
                coords = np.zeros((keyframe_count + current_keyframe_count) * 2, dtype=np.float64)
                current_coords = np.zeros(current_keyframe_count * 2, dtype=np.float64)
                fcurve.keyframe_points.foreach_get('co', current_coords)
                if frame_offset < fcurve.keyframe_points[0].co[0]:
                    # This actually harder than I thought
                    # Appending after last keyframe is easy, but I can't say the same with in between/previous keyframes
                    raise RuntimeError('Cannot insert in between keyframes')
                    # fcurve.keyframe_points.clear()
                    # fcurve.keyframe_points.add(current_keyframe_count)
                    # current_keyframe_count = 0
                    # keyframes = keyframes + current_coords[::2].tolist()
                    # rotation_list.append([(rotation, rotation, rotation, rotation) for rotation in current_coords[1::2]])
                else:
                    coords[:current_keyframe_count * 2] = current_coords
            else:
                coords = np.zeros(keyframe_count * 2, dtype=np.float64)

            fcurve.keyframe_points.add(keyframe_count)
            coords[current_keyframe_count * 2::2] = keyframes
            coords[current_keyframe_count * 2 + 1::2] = [location[index] for _, location, _ in data]
            # coords[(current_keyframe_count * 2) + 1::2] = [rotation[index] for rotation in rotation_list]
            fcurve.keyframe_points.foreach_set('co', coords)
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'

        for index, fcurve in enumerate(bone_fcurves_rotation):
            current_keyframe_count = len(fcurve.keyframe_points)

            if not current_keyframe_count == 0:
                coords = np.zeros((keyframe_count + current_keyframe_count) * 2, dtype=np.float64)
                current_coords = np.zeros(current_keyframe_count * 2, dtype=np.float64)
                fcurve.keyframe_points.foreach_get('co', current_coords)

                coords[:current_keyframe_count * 2] = current_coords
            else:
                coords = np.zeros(keyframe_count * 2, dtype=np.float64)

            fcurve.keyframe_points.add(keyframe_count)
            coords[current_keyframe_count * 2::2] = keyframes
            coords[current_keyframe_count * 2 + 1::2] = [rotation[index] for _, _, rotation in data]
            fcurve.keyframe_points.foreach_set('co', coords)
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'

    if bone_missing:
        def draw(self, context):
            self.layout.label(text='One or more bone are not found, please check console for more info')

        context.window_manager.popup_menu(draw, title='WARNING | MISSING BONE', icon='WARNING_LARGE')

    if armature_warning:
        def draw(self, context):
            self.layout.label(text='You are attempting to apply animation into armature. It is not recommended due to offset issues.')

        context.window_manager.popup_menu(draw, title='INFO', icon='INFO')

    
    if keyframe_count == 0:
        def draw(self, context):
            self.layout.label(text='No keyframe within range')

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
        scene = context.scene
        anim_prop = scene.io3d_anim_props
        if anim_prop.use_current_fps:
            fps = scene.render.fps if scene.render.frame_map_old == scene.render.frame_map_new else scene.render.frame_map_old
        else:
            fps = anim_prop.override_fps
        if anim_prop.insert_at == 'CURRENT':
            frame_offset = context.scene.frame_current 
        elif anim_prop.insert_at == 'FIRST':
            frame_offset = 1
        else:
            frame_offset = anim_prop.frame_set

        return apply_animation(context, fps, frame_offset, anim_prop.frame_range, anim_prop.frame_start, anim_prop.frame_end, anim_prop.apply_rest_rotation)

def register():
    bpy.utils.register_class(ApplyAnimation)

def unregister():
    bpy.utils.unregister_class(ApplyAnimation)
