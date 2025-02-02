import bpy
import json
import mathutils
import struct

from ..compressor import comp_small_three, comp_8_bytes


def export_anim(context: bpy.types.Context, filepath: str, anim_ver: str, frame_range: str, frame_start: int, frame_end: int):
    scene = context.scene
    active_object = context.active_object
    mode = active_object.type
    is_use_stretching = False

    if mode == 'ARMATURE':
        try:
            bpy.ops.object.mode_set(mode='POSE')
        except:
            pass
        
        bones_iter = active_object.pose.bones
    else:
        while True:
            res = bpy.ops.object.select_grouped(extend=True, type='PARENT')
            if res == {'CANCELLED'}:
                break

        root = context.object
        bones_iter = [root] + [_ for _ in root.children_recursive]

    bones = {}
    for bone in bones_iter:
        if bone.name.startswith('origin_correction'):
            continue
        key = bone.name.rsplit('.', 1)[0]
        bones[key] = bone

    if anim_ver == 'DEFAULT':
        anim_ver = 4000
    elif anim_ver == 'VER4':
        anim_ver = 4001
    else:
        anim_ver = 4002

    if scene.render.fps == 100:
        if scene.render.frame_map_old == scene.render.frame_map_new:
            fps = 100
            old_fps = 100
        else:
            is_use_stretching = True
            fps = 100
            old_fps = scene.render.frame_map_old
    else:
        fps = scene.render.fps
        old_fps = None

    anim_data = {}
    anim_data['tracks'] = {}
    latest_keyframe = 0
    interpolation_check = {}

    if mode == 'ARMATURE':
        action = active_object.animation_data.action

    for bone_name, bone in bones.items():
        if mode == 'EMPTY':
            action = bone.animation_data.action

        anim_data['tracks'][bone_name] = {}
        anim_data['tracks'][bone_name]['frames'] = {}
        anim_data['tracks'][bone_name]['keyframe_count'] = 0

        data_path_location = 'location' if mode == 'EMPTY' else f'pose.bones["{bone.name}"].location'
        data_path_rotation = 'rotation_quaternion' if mode == 'EMPTY' else f'pose.bones["{bone.name}"].rotation_quaternion'

        bone_fcurves_location = []
        bone_fcurves_rotation = []

        for fcurve in action.fcurves:
            if fcurve.data_path == data_path_location:
                bone_fcurves_location.append(fcurve)
            elif fcurve.data_path == data_path_rotation:
                bone_fcurves_rotation.append(fcurve)

        for fcurve in bone_fcurves_location:
            keyframes = fcurve.keyframe_points

            if not anim_data['tracks'][bone_name]['frames'].get('location'):
                anim_data['tracks'][bone_name]['frames']['location'] = {}

            for keyframe in keyframes:
                frame, location = keyframe.co
                if frame == 0.0:
                    continue
                
                if frame_range == 'PARTIAL':
                    if not frame_start <= frame <= frame_end:
                        continue

                    frame = float(frame - (frame_start-1))
                else:
                    frame -= 1.0

                if not anim_data['tracks'][bone_name]['frames']['location'].get(frame):
                    anim_data['tracks'][bone_name]['frames']['location'][frame] = []

                anim_data['tracks'][bone_name]['frames']['location'][frame].append(location)

        for fcurve in bone_fcurves_rotation:
            fcurve: bpy.types.FCurve
            keyframes = fcurve.keyframe_points

            if not anim_data['tracks'][bone_name]['frames'].get('rotation'):
                anim_data['tracks'][bone_name]['frames']['rotation'] = {}

            for keyframe in keyframes:
                frame, rotation = keyframe.co
                if frame == 0.0:
                    continue
                
                if frame_range == 'PARTIAL':
                    if not frame_start <= frame <= frame_end:
                        continue
            
                    frame = float(frame - (frame_start-1)) - 1.0
                else:
                    frame -= 1.0

                if latest_keyframe < int(frame):
                    latest_keyframe = int(frame)

                if not anim_data['tracks'][bone_name]['frames']['rotation'].get(frame):
                    anim_data['tracks'][bone_name]['frames']['rotation'][frame] = []

                anim_data['tracks'][bone_name]['frames']['rotation'][frame].append(rotation)

        loc_frames = anim_data['tracks'][bone_name]['frames']['location'].keys()
        rot_frames = anim_data['tracks'][bone_name]['frames']['rotation'].keys()

        for frame in loc_frames - rot_frames:
            interpolation_check[frame] = 'rot'

        for frame in rot_frames - loc_frames:
            interpolation_check[frame] = 'loc'

        # This interpolation check is to fix keyframes that only have keyframe for either loc/rot
        # By looking from the files, it appears that location and rotation always come in pairs
        # So in order to fix it, the script will seek to certain keyframe to check the loc/rot based off the interpolation
        # Oh, also, because of this, I had no idea how to improve it with fcurves.foreach_get()
        if interpolation_check:
            for frame, ref in interpolation_check.items():
                if frame_range == 'PARTIAL':
                    frame = float(frame + (frame_start-1))

                if is_use_stretching and fps != old_fps:
                    frame = int(frame + 1.0)
                    frame = (frame/old_fps) * 1000
                    frame = round((frame / 1000) * fps)

                scene.frame_set(int(frame))
                if ref == 'loc':
                    anim_data['tracks'][bone_name]['frames']['location'][frame] = [_ for _ in bone.location]
                else:
                    anim_data['tracks'][bone_name]['frames']['rotation'][frame] = [_ for _ in bone.rotation_quaternion]
            
            check = interpolation_check.values()
            if 'loc' in check:
                anim_data['tracks'][bone_name]['frames']['location'] = dict(sorted(anim_data['tracks'][bone_name]['frames']['location'].items()))
            if 'rot' in check:
                anim_data['tracks'][bone_name]['frames']['rotation'] = dict(sorted(anim_data['tracks'][bone_name]['frames']['rotation'].items()))

            interpolation_check = {}

        current_keyframe_count = anim_data['tracks'][bone_name]['keyframe_count']
        keyframe_count = len(anim_data['tracks'][bone_name]['frames']['rotation'])
        if current_keyframe_count < keyframe_count:
            anim_data['tracks'][bone_name]['keyframe_count'] = keyframe_count

    anim_data['latest_keyframe'] = latest_keyframe

    fps = old_fps if is_use_stretching else fps

    with open(filepath, 'wb') as ani:
        ani.write(b'ANI\0') # signature

        if anim_ver == 'VER4':
            version = 4001
        elif anim_ver == 'VER8':
            version = 4002
        else:
            version = 4000
        ani.write(struct.pack('<I', version)) # version

        # Events, not yet implemented
        ani.write(struct.pack('<I', 0)) # event_count
        # ani.write(struct.pack('<I', len(events))) # event_count

        # for time, event_type, event_name in events:
        #     ani.write(struct.pack('<I', len(event_type)))
        #     ani.write(event_type.encode('utf-8'))
        #     ani.write(struct.pack('<I', len(event_name)))
        #     ani.write(event_name.encode('utf-8'))
        #     ani.write(struct.pack('<I', time))

        total_time = int((anim_data['latest_keyframe'] / fps) * 1000)
        ani.write(struct.pack('<I', total_time)) # total_time
        ani.write(struct.pack('<I', len(anim_data['tracks']))) # total_track

        for bone_name, keyframe_data in anim_data['tracks'].items():
            keyframe_count = keyframe_data['keyframe_count']
            keyframe_data = keyframe_data['frames']

            ani.write(struct.pack('<I', len(bone_name))) # biped_bone_name_length
            ani.write(bone_name.encode('utf-8')) # biped_bone_bane
            ani.write(struct.pack('<f', 1.0)) # weight
            ani.write(struct.pack('<I', keyframe_count)) # keyframe_count

            for (frame, location), (_, rotation) in zip(keyframe_data['location'].items(), keyframe_data['rotation'].items()):
                rotation = mathutils.Quaternion(rotation)
                frame = int(frame)
                time = int(round((frame/fps) * 1000))
                if anim_ver == 'VER4':
                    packed_rotation = comp_small_three(rotation)
                    ani.write(struct.pack('<L', packed_rotation)) # qRot
                elif anim_ver == 'VER8':
                    high, low = comp_8_bytes(rotation)
                    ani.write(struct.pack('<L', high)) # qRot
                    ani.write(struct.pack('<L', low)) # qRot
                else:
                    w, x, y, z = rotation
                    ani.write(struct.pack('<4f', *[x, y, z, w])) # qRot
                ani.write(struct.pack('<3f', *location)) # vTrans
                ani.write(struct.pack('<I', time)) # iTime
    
    return {'FINISHED'}

def export_entry(context: bpy.types.Context, filepath: str):
    anim_data_props = context.scene.io3d_animation_data
    try:
        anim_data = anim_data_props.entry[anim_data_props.active_entry_index]
    except IndexError:
        def draw(self, context):
            self.layout.label(text='No entry to export')

        context.window_manager.popup_menu(draw, title='INFO', icon='INFO')
        return {'FINISHED'}
    
    tmp_dict = {}
    for bone_name, data in anim_data:
        tmp_dict[bone_name] = []
        for frame, location, rotation in data:
            location = (location.x, location.y, location.z)
            rotation = (rotation.w, rotation.x, rotation.y, rotation.z)
            tmp_dict[bone_name].append((frame, location, rotation))

    animation = {anim_data.name: tmp_dict, 'frames': anim_data.frames,
                 'total_time': anim_data.total_time, 'is_retarget': anim_data.is_retarget}
    
    with open(filepath, 'w+') as f:
        json.dump(animation, f)

    return {'FINISHED'}

from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper


class AnimExport(Operator, ExportHelper):
    """Export Lost Saga Anim (.ani)"""
    bl_idname = "io3d.anim_export"
    bl_label = "Export Lost Saga Anim (.ani)"

    filename_ext = ".ani"

    filter_glob: StringProperty(
        default="*.ani",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    anim_ver: EnumProperty(
        name="Animation Version",
        description="Animation Version to choose from",
        items=(
            ("DEFAULT", "Default", "Version 4000. Which compress quaternion as is"),
            ("VER4", "VER4", "Version 4001. Which compress quaternion into single 32-bit integer"),
            ("VER8", "VER8", "Version 4001. Which compress quaternion into double 32-bit integer"),
        ),
        default="DEFAULT",
    )

    frame_range: EnumProperty(
        name="Frame Range",
        description="Frame range to export animation",
        items=(
            ("ALL", "All", "Export animation on all range"),
            ("PARTIAL", "Partial", "Export animation within frame range"),
        ),
        default="ALL",
    )

    frame_start: IntProperty(
        name="Frame Start",
        description="Frame start",
        default=0,
    )

    frame_end: IntProperty(
        name="Frame End",
        description="Frame end",
        default=250,
    )

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type in ('EMPTY', 'ARMATURE')

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.prop(self, "anim_ver")

        col = layout.column()
        col.prop(self, "frame_range")

        col = layout.column()
        col.enabled = (self.frame_range == 'PARTIAL')
        col.prop(self, "frame_start")
        col.prop(self, "frame_end")

    def execute(self, context):
        return export_anim(context, self.filepath, self.anim_ver, self.frame_range, self.frame_start, self.frame_end)

    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        return super().invoke(context, event)

class EntryExport(Operator, ExportHelper):
    """Export Animation Entry"""
    bl_idname = "io3d.entry_export"
    bl_label = "Export Animation Entry (.json)"

    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return export_entry(context, self.filepath)

def menu_func_export(self, context):
    self.layout.operator(AnimExport.bl_idname, text="Lost Saga Anim (.ani)", icon='ANIM')


def register():
    bpy.utils.register_class(AnimExport)
    bpy.utils.register_class(EntryExport)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(EntryExport)
    bpy.utils.unregister_class(AnimExport)
