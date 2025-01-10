import bpy
import bmesh
import math
import mathutils
import pathlib
import struct

from ..classes.seeker import Seeker
from ..ani.compressor import decomp_small_three, decomp_8_bytes

def is_animation_file(bytes):
    return bytes == b'ANI\0'

def version_check(version: int):
    return version in (4000, 4001, 4002)

def import_animation(context: bpy.context, filepath: str, fps: int = 60, frame_offset: int = 0):
    ANIMATION_VER_DEFAULT = 4000
    ANIMATION_VER_COMP4 = 4001
    ANIMATION_VER_COMP8 = 4002
    
    while True:
        res = bpy.ops.object.select_grouped(extend=True, type='PARENT')
        if res == {'CANCELLED'}:
            break
        
    root = context.object
    if not any(root.name.startswith(bone_name) for bone_name in ('Bip01', 'origin_empty')):
        raise RuntimeError('Object is not Lost Saga skeleton')
    
    empties_objects = [root] + [_ for _ in root.children_recursive]
    
    bones = {}
    for empty in empties_objects:
        key = empty.name.rsplit('.', 1)[0]
        bones[key] = empty
    
    with open(filepath, 'rb') as f:
        ani = f.read()

    s = Seeker()
    signature =  ani[:s.i]
    if not is_animation_file(signature):
        raise RuntimeError('Not .ani file')

    version = struct.unpack('<I', ani[s.o:s.i])[0]
    if not version_check(version):
        raise RuntimeError('Unknown Version')
    
    event_count = struct.unpack('<I', ani[s.o:s.i])[0]
    animation_event = []

    for _ in range(event_count):
        event_type_length = struct.unpack('<I', ani[s.o:s.i])[0]
        event_type = ani[s.o:s.char(event_type_length)]
        event_name_length = struct.unpack('<I', ani[s.o:s.i])[0]
        event_name = ani[s.o:s.char(event_name_length)]
        event_time = struct.unpack('<f', ani[s.o:s.f])[0]
        animation_event.append((event_time, event_type, event_name))

    total_time = struct.unpack('<I', ani[s.o:s.i])[0]
    total_track = struct.unpack('<I', ani[s.o:s.i])[0]
    keyframe_data = {}
    for _ in range(total_track):
        biped_name_length = struct.unpack('<I', ani[s.o:s.i])[0]
        biped_name = ani[s.o:s.char(biped_name_length)].decode('utf-8')
        weight = struct.unpack('<f', ani[s.o:s.f])[0] # always 0 from what it seemed
        keyframe_count = struct.unpack('<I', ani[s.o:s.i])[0]
        
        keyframe_data[biped_name] = []

        if version == ANIMATION_VER_COMP4:
            for _ in range(keyframe_count):
                packed_rotation = struct.unpack('<L', ani[s.o:s.L])[0]
                qRot = decomp_small_three(packed_rotation)
                vTrans = struct.unpack('<3f', ani[s.o:s.vpos])
                vTrans = mathutils.Vector(vTrans)
                iTime = struct.unpack('<I', ani[s.o:s.i])[0]
                frame = int(iTime*fps/1000)
                keyframe_data[biped_name].append((frame, vTrans, qRot))
        elif version == ANIMATION_VER_COMP8:
            for _ in range(keyframe_count):
                dwHigh = struct.unpack('<L', ani[s.o:s.L])[0]
                dwLow = struct.unpack('<L', ani[s.o:s.L])[0]
                vTrans = struct.unpack('<3f', ani[s.o:s.vpos])
                vTrans = mathutils.Vector(vTrans)
                qRot = decomp_8_bytes(dwHigh, dwLow)
                qRot = mathutils.Quaternion(qRot)
                iTime = struct.unpack('<I', ani[s.o:s.i])[0]
                frame = int(iTime*fps/1000)
                keyframe_data[biped_name].append((frame, vTrans, qRot))
        else:
            for _ in range(keyframe_count):
                qRot = struct.unpack('<4f', ani[s.o:s.qrot])
                qRot = mathutils.Quaternion((qRot[3], qRot[0], qRot[1], qRot[2]))
                vTrans = struct.unpack('<3f', ani[s.o:s.vpos])
                vTrans = mathutils.Vector(vTrans)
                iTime = struct.unpack('<I', ani[s.o:s.i])[0]
                frame = int(iTime*fps/1000)
                keyframe_data[biped_name].append((frame, vTrans, qRot))
        
    error = False
    not_found = []
    for biped_name, data in keyframe_data.items():
        if biped_name in not_found:
            continue
        
        bpy.ops.object.select_all(action='DESELECT')
        
        try:
            bone = bones[biped_name]
        except KeyError:
            error = True
            not_found.append(biped_name)
            print(f'Warning, bone {biped_name} is not found')
            break
        
        bone.select_set(True)
        context.view_layer.objects.active = bone
        bone.rotation_mode = 'QUATERNION'
        bone_fcurves_location = []
        bone_fcurves_rotation = []
        
        action = bpy.data.actions.get(bone.name, None)
        if not action:
            action = bpy.data.actions.new(name=bone.name)
            bone.animation_data_create()
            
        bone.animation_data.action = action
            
        if not action.fcurves:
            bone_fcurves_location = [action.fcurves.new(data_path = 'location', index = i, action_group = bone.name) for i in range(3)]
            bone_fcurves_rotation = [action.fcurves.new(data_path = 'rotation_quaternion', index = i, action_group = bone.name) for i in range(4)]
        else:
            bone_fcurves_location = [action.fcurves[i] for i in range(3)]
            bone_fcurves_rotation = [action.fcurves[i] for i in range(3, 7)]
        
        for index, fcurve in enumerate(bone_fcurves_location):
            fcurve.keyframe_points.add(len(data) + frame_offset)
            
            # There is a high certainty that ver8 animation cause this out of index error
            for frame, location, rotation in data:
                if frame >= len(data):
                    continue
                    
                keyframe = fcurve.keyframe_points[frame + frame_offset]
                keyframe.co = frame + frame_offset, location[index]
                keyframe.interpolation = 'LINEAR'
                
            fcurve.update()
        
        for index, fcurve in enumerate(bone_fcurves_rotation):
            fcurve.keyframe_points.add(len(data) + frame_offset)
            
            for frame, location, rotation in data:
                if frame >= len(data):
                    continue
                    
                keyframe = fcurve.keyframe_points[frame + frame_offset]
                keyframe.co = frame + frame_offset, rotation[index]
                keyframe.interpolation = 'LINEAR'
                
            fcurve.update()
            

    if not bones.get('origin_empty', None):
        origin_empty = bpy.data.objects.new('origin_empty', None)
        origin_empty.empty_display_type = 'PLAIN_AXES'
        bpy.context.scene.collection.objects.link(origin_empty)

        bpy.ops.object.select_all(action='DESELECT')
        origin_empty.select_set(True)
        root.select_set(True)
        bpy.context.view_layer.objects.active = origin_empty
        bpy.ops.object.parent_set()

        origin_empty.rotation_euler.x = math.radians(90)
        origin_empty.rotation_euler.z = math.radians(180)
        origin_empty.scale.x = -1
    
    def draw(self, context):
        self.layout.label(text='One or more bone are not found, please check console for more info')
    
    if error:
        context.window_manager.popup_menu(draw, title='WARNING | MISSING BONE', icon='WARNING_LARGE')

    return {'FINISHED'}

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup


# frame_offset is yet to be implemented
class LosaAnim(Operator, ImportHelper):
    """Import Lost Saga Animation (.ani). WARNING, experimental"""
    bl_idname = "io3d.animation_import" 
    bl_label = "Import Lost Saga Animation (.ani)"

    filename_ext = ".ani"

    filter_glob: StringProperty(
        default="*.ani",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    files: CollectionProperty(type=bpy.types.PropertyGroup)
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'EMPTY'
    
    def execute(self, context):
        import_animation(context, self.filepath)
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(LosaAnim.bl_idname, text="Lost Saga Animation (.ani)", icon='ANIM')

def register():
    bpy.utils.register_class(LosaAnim)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(LosaAnim)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)