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
    if not root.name.startswith('Bip01'):
        raise RuntimeError('Object is not Lost Saga skeleton')
        
    bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
    
    empties_objects = [_ for _ in context.selected_objects if _.type == 'EMPTY']
    
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
                vTrans = mathutils.Vector((vTrans[0], vTrans[2], -vTrans[1]))
                iTime = struct.unpack('<I', ani[s.o:s.i])[0]
                frame = int(iTime*fps/1000)
                keyframe_data[biped_name].append((frame, vTrans, qRot))
        elif version == ANIMATION_VER_COMP8:
            for _ in range(keyframe_count):
                dwHigh = struct.unpack('<L', ani[s.o:s.L])[0]
                dwLow = struct.unpack('<L', ani[s.o:s.L])[0]
                vTrans = struct.unpack('<3f', ani[s.o:s.vpos])
                vTrans = mathutils.Vector((vTrans[0], vTrans[2], -vTrans[1]))
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
                vTrans = mathutils.Vector((vTrans[0], vTrans[2], -vTrans[1]))
                iTime = struct.unpack('<I', ani[s.o:s.i])[0]
                frame = int(iTime*fps/1000)
                keyframe_data[biped_name].append((frame, vTrans, qRot))
        
        error = False
        not_found = []
        for biped_name, data in keyframe_data.items():
            if biped_name in not_found:
                continue
            
            for frame_data in data:
                frame, vTrans, qRot = frame_data
            
                bpy.ops.object.select_all(action='DESELECT')
                try:
                    bone = bones[biped_name]
                    bone.select_set(True)
                    context.view_layer.objects.active = bone
                    bone.rotation_mode = 'QUATERNION'
                    bone.location = vTrans
                    bone.rotation_quaternion = qRot
                    bone.keyframe_insert(data_path="rotation_quaternion", frame=frame+frame_offset)
                except KeyError:
                    error = True
                    not_found.append(biped_name)
                    print(f'Warning, bone {biped_name} is not found')
                    break
        
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