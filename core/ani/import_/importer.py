import bpy
import mathutils
import pathlib
import struct

from ...classes.seeker import Seeker
from ..compressor import decomp_small_three, decomp_8_bytes


def is_animation_file(bytes):
    return bytes == b'ANI\0'

def version_check(version: int):
    return version in (4000, 4001, 4002)

def import_animation(context: bpy.types.Context, filepath: str):
    ANIMATION_VER_DEFAULT = 4000
    ANIMATION_VER_COMP4 = 4001
    ANIMATION_VER_COMP8 = 4002

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
    total_frames = 0
    highest_time = 0
    for _ in range(total_track):
        biped_name_length = struct.unpack('<I', ani[s.o:s.i])[0]
        biped_name = ani[s.o:s.char(biped_name_length)].decode('utf-8')
        weight = struct.unpack('<f', ani[s.o:s.f])[0] # always 1 from what it seemed
        keyframe_count = struct.unpack('<I', ani[s.o:s.i])[0]
        total_frames = keyframe_count if total_frames < keyframe_count else total_frames
        
        keyframe_data[biped_name] = []

        # Why not convert the quaternion instead of using rotating the empty origin?
        # Because I did, and it's too much hassle
        # Importing the skeleton is already stressful enough
        # Here's the thing, if I were to fix the animation, it'd be hassle since the axes needs
        # to be converted. Instead of having to convert each one back to back, I'd figured I'll
        # just make an universal solution, that is by parenting the root into the origin, which
        # makes it very easy to fix the axes differences.
        if version == ANIMATION_VER_COMP4:
            for _ in range(keyframe_count):
                packed_rotation = struct.unpack('<L', ani[s.o:s.L])[0]
                qRot = decomp_small_three(packed_rotation)
                qRot = mathutils.Quaternion(qRot)

                vTrans = struct.unpack('<3f', ani[s.o:s.vpos])
                vTrans = mathutils.Vector(vTrans)

                iTime = struct.unpack('<I', ani[s.o:s.i])[0]
                keyframe_data[biped_name].append((iTime, vTrans, qRot))

                highest_time = iTime if highest_time < iTime else highest_time
        elif version == ANIMATION_VER_COMP8:
            for _ in range(keyframe_count):
                dwHigh = struct.unpack('<L', ani[s.o:s.L])[0]
                dwLow = struct.unpack('<L', ani[s.o:s.L])[0]
                qRot = decomp_8_bytes(dwHigh, dwLow)
                qRot = mathutils.Quaternion(qRot)

                vTrans = struct.unpack('<3f', ani[s.o:s.vpos])
                vTrans = mathutils.Vector(vTrans)

                iTime = struct.unpack('<I', ani[s.o:s.i])[0]
                keyframe_data[biped_name].append((iTime, vTrans, qRot))

                highest_time = iTime if highest_time < iTime else highest_time
        else:
            for _ in range(keyframe_count):
                qRot = struct.unpack('<4f', ani[s.o:s.qrot])
                qRot = mathutils.Quaternion((qRot[3], qRot[0], qRot[1], qRot[2]))

                vTrans = struct.unpack('<3f', ani[s.o:s.vpos])
                vTrans = mathutils.Vector(vTrans)

                iTime = struct.unpack('<I', ani[s.o:s.i])[0]
                keyframe_data[biped_name].append((iTime, vTrans, qRot))

                highest_time = iTime if highest_time < iTime else highest_time
        
    basename = pathlib.Path(filepath).stem
    animation = {basename: keyframe_data, 'frames': total_frames, 'total_time': highest_time}
    context.scene.io3d_animation_data.append(animation)

    return {'FINISHED'}

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator


class LosaAnim(Operator, ImportHelper):
    """Import Lost Saga Animation (.ani). Supports importing multiple files at once"""
    bl_idname = "io3d.animation_import" 
    bl_label = "Import Lost Saga Animation (.ani)"

    filename_ext = ".ani"

    filter_glob: StringProperty(
        default="*.ani",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    files: CollectionProperty(type=bpy.types.PropertyGroup)
    
    def execute(self, context):
        path = pathlib.Path(self.filepath)
        folder = path.parent
        for file in self.files:
            filepath = str(folder.joinpath(file.name))
            import_animation(context, filepath)

        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(LosaAnim.bl_idname, text="Lost Saga Animation (.ani)", icon='ANIM')

def register():
    bpy.utils.register_class(LosaAnim)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(LosaAnim)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)