import bpy
import math
import mathutils
import pathlib
import struct

from ...classes.seeker import Seeker

def is_skeleton_file(bytes):
    encrypted_skeleton_token = 0x105C5B63
    decrypted_check = encrypted_skeleton_token - 0x10101010
    return bytes == decrypted_check

# To-do legs/hands IK
def import_skeleton(context: bpy.context, filepath: str, mode: str, legs_IK: bool, hand_IK: bool):
    with open(filepath, 'rb') as f:
        skl = f.read()

    s = Seeker()
    signature = struct.unpack('<I', skl[:s.i])[0]
    if not is_skeleton_file(signature):
        raise RuntimeError('Not a skeleton file')
    
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass
    
    if mode == 'ARMATURE':
        basename = pathlib.Path(filepath).stem
        armature_data = bpy.data.armatures.new(basename)
        armature_object = bpy.data.objects.new(basename, armature_data)
        armature_object.show_in_front = True
        
        context.scene.collection.objects.link(armature_object)
        
        armature_object.select_set(state=True)
        context.view_layer.objects.active = armature_object

        bpy.ops.object.mode_set(mode='EDIT')

        bones = {}
    
    version = struct.unpack('<I', skl[s.o:s.i])[0]
    biped_count = struct.unpack('<I', skl[s.o:s.i])[0]
    bone_data = {}
    for _ in range(1, biped_count+1):
        biped_length = struct.unpack('<I', skl[s.o:s.i])[0]
        biped_bone_name = skl[s.o:s.char(biped_length)].decode('utf-8')
        
        # Brief Explanation
        # LocalTM likely indicates the bone position/rotation relative to the parent (likely using inverse?)
        # ObjectTM likely indicates the bone position/rotation relative to world origin
        # For root, both LocalTM and ObjectTM results the same
        # For eyes, the correct rotation is stored inside ObjectTM
        # For mantle, the correct rotation is stored inside ObjectTM, but y and z axis is swapped
        # (This script already swapped beforehand for axis compability (y>z), so in this case, it's
        # wxyz on blender, but xzyw on lost saga)
        #
        # Either LocalTM or ObjectTM implementation works, you can use either quaternion for bone rotation
        # But for animation, you only need to import armature as empty and using the LocalTMVPos
        LocalTMvPos = struct.unpack('<3f', skl[s.o:s.vpos])
        LocalTMvPos = mathutils.Vector((LocalTMvPos[0], LocalTMvPos[2], LocalTMvPos[1]))
        LocalTMqRot = struct.unpack('<4f', skl[s.o:s.qrot])
        LocalTMqRot = mathutils.Quaternion((LocalTMqRot[3], -LocalTMqRot[0], -LocalTMqRot[2], -LocalTMqRot[1])) # Likely xyzw order
        ObjectTMvPos = mathutils.Vector(struct.unpack('<3f', skl[s.o:s.vpos]))
        ObjectTMqRot = struct.unpack('<4f', skl[s.o:s.qrot])
        ObjectTMqRot = mathutils.Quaternion((-ObjectTMqRot[3], -ObjectTMqRot[0], ObjectTMqRot[2], ObjectTMqRot[1])) # Likely xyzw order
        kObjectTMmatrix = struct.unpack('<16f', skl[s.o:s.matrix])
        kObjectTMmatrix = mathutils.Matrix([kObjectTMmatrix[x:x+4] for x in range(0, len(kObjectTMmatrix),4)]).transposed()
        
        rot_x = mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
        rot_y = mathutils.Matrix.Rotation(math.radians(180), 4, 'Y')
        transformation = mathutils.Matrix.Scale(-1, 4, (1, 0, 0)) @ rot_x @ rot_y
        converted_matrix = transformation @ kObjectTMmatrix @ kObjectTMmatrix.transposed()
        
        parent_length = struct.unpack('<I', skl[s.o:s.i])[0]
        parent_name = None
        if parent_length:
            parent_name = skl[s.o:s.char(parent_length)].decode('utf-8')
        
        # Bone rotation corrector for empties
        # I'll be honest, this is very dirty and is a very bad practice
        # Either way, here is the rotation correction for LocalTM
        if mode == 'EMPTY':
            correction_w = ['Bip01 L Clavicle', 'Bip01 R Clavicle', 'Bip01 R Thigh']
            correction_x = ['Bip01 Spine2', 'Bip01 Head', 'Bip01 L Clavicle', 'Bip01 L Forearm', 'Bip01 L Finger01', 'Bip01 L Finger12', 'Bip01 R Clavicle', 'Bip01 R Finger02', 'Bip01 R Finger11', 'Bip01 R Finger12', 'Bip01 R Finger21', 'Bip01 R Finger22', 'Bip01 Mantle01', 'Bip01 L Toe0', 'Bip01 R Thigh', 'Bip01 R Calf', 'Bip01 R Foot', 'Bip01 R Toe0']
            correction_y = ['Bip01', 'Bip01 Spine', 'Bip01 Spine1', 'Bip01 Neck', 'Bip01 Head', 'Bip01 L Clavicle', 'Bip01 L Finger01', 'Bip01 L Finger11', 'Bip01 L Finger21', 'Bip01 R Clavicle', 'Bip01 R Finger02', 'Bip01 R Finger22', 'Bip01 Mantle03', 'Bip01 Mantle05', 'Bip01 L Calf', 'Bip01 R Thigh']
            correction_z = ['Bip01 Spine2', 'Bip01 L Clavicle', 'Bip01 L Finger12', 'Bip01 L Finger22', 'Bip01 R Clavicle', 'Bip01 R Finger11', 'Bip01 R Finger21', 'Bip01 R Finger22', 'Bip01 Mantle01', 'Bip01 R Thigh']
            if biped_bone_name in correction_w:
                LocalTMqRot.w = -LocalTMqRot.w
            if biped_bone_name in correction_x:
                LocalTMqRot.x = -LocalTMqRot.x
            if biped_bone_name in correction_y:
                LocalTMqRot.y = -LocalTMqRot.y
            if biped_bone_name in correction_z:
                LocalTMqRot.z = -LocalTMqRot.z
                
            LocalTMqRot = LocalTMqRot.to_euler()
            correction_x = ['Bip01 right_eyebrow', 'Bip01 right_eyeball', 'Bip01 right_eyetop', 'Bip01 L Finger01', 'Bip01 L Finger02']
            correction_y = ['Bip01']
            correction_z = ['Bip01 Spine2', 'Bip01 Mantle01', 'Bip01 Mantle02']
            if biped_bone_name in correction_x:
                LocalTMqRot.x = -LocalTMqRot.x
            if biped_bone_name in correction_y:
                LocalTMqRot.y = -LocalTMqRot.y
            if biped_bone_name in correction_z:
                LocalTMqRot.z = -LocalTMqRot.z
        
        if mode == 'EMPTY':
            correction_x = ['Bip01 L Clavicle', 'Bip01 R Clavicle', 'Bip01 Mantle03', 'Bip01 Mantle04']
            correction_y = ['Bip01 Head', 'Bip01 L Clavicle', 'Bip01 L Finger12', 'Bip01 R Clavicle', 'Bip01 R UpperArm', 'Bip01 R Finger01', 'Bip01 R Finger11', 'Bip01 R Finger21', 'Bip01 Mantle02', 'Bip01 Mantle03', 'Bip01 Mantle04', 'Bip01 Mantle05', 'Bip01 L Foot']
            correction_z = ['Bip01 Pelvis', 'Bip01 Spine', 'Bip01 Spine2', 'Bip01 Neck', 'Bip01 left_eyebrow', 'Bip01 left_eyetop', 'Bip01 left_eyeball', 'Bip01 right_eyebrow', 'Bip01 right_eyeball', 'Bip01 right_eyetop', 'Bip01 L UpperArm', 'Bip01 L Forearm', 'Bip01 L Finger11', 'Bip01 L Finger12', 'Bip01 R Forearm', 'Bip01 R Finger01', 'Bip01 R Finger21', 'Bip01 R Finger22', 'Bip01 L Toe0', 'Bip01 R Foot']
            if biped_bone_name in correction_x:
                LocalTMvPos.x = -LocalTMvPos.x
            if biped_bone_name in correction_y:
                LocalTMvPos.y = -LocalTMvPos.y
            if biped_bone_name in correction_z:
                LocalTMvPos.z = -LocalTMvPos.z
        
        if mode == 'ARMATURE':
            edit_bone = armature_data.edit_bones.new(biped_bone_name)
            edit_bone.matrix = converted_matrix
            bones[biped_bone_name] = edit_bone
        elif mode == 'EMPTY':
            empty = bpy.data.objects.new(biped_bone_name, None)
            empty.empty_display_type = 'PLAIN_AXES'
            context.scene.collection.objects.link(empty)
            bone_data[biped_bone_name] = (empty, LocalTMvPos, LocalTMqRot)
            
            empty['Euler Rest X'] = LocalTMqRot.x
            empty['Euler Rest Y'] = LocalTMqRot.y
            empty['Euler Rest Z'] = LocalTMqRot.z
            quaternion_rest = LocalTMqRot.to_quaternion()
            empty['Quaternion Rest W'] = quaternion_rest.w
            empty['Quaternion Rest X'] = quaternion_rest.x
            empty['Quaternion Rest Y'] = quaternion_rest.y
            empty['Quaternion Rest Z'] = quaternion_rest.z

        if parent_name and not parent_name == 'NoParent': # NoParent indicates root
            if mode == 'ARMATURE':
                edit_bone.parent = bones[parent_name]
                edit_bone.head = bones[parent_name].tail
            # Empties does not account for duplicates found in scene
            # Will be fixed as soon animation is fully implemented
            elif mode == 'EMPTY':
                parent_empty = bpy.data.objects.get(parent_name)
                bpy.ops.object.select_all(action='DESELECT')
                empty.select_set(True)
                parent_empty.select_set(True)
                context.view_layer.objects.active = parent_empty
                bpy.ops.object.parent_set(keep_transform=True)

        if mode == 'ARMATURE':
            if edit_bone.head == edit_bone.tail: # blender removes bones if the head and tail have the exact same position
                edit_bone.tail.y += 0.1

        child_count = struct.unpack('<I', skl[s.o:s.i])[0]
        for _ in range(1, child_count+1):
            child_length = struct.unpack('<I', skl[s.o:s.i])[0]
            child_bone_name = None
            if child_length:
                child_bone_name = skl[s.o:s.char(child_length)].decode('utf-8')
    
    for bone, position, rotation in bone_data.values():
        bone.location = position
        bone.rotation_euler = rotation
    
    linked_skeleton_length = struct.unpack('<I', skl[s.o:s.i])[0]
    if linked_skeleton_length:
        linked_skeleton_name = skl[s.o:s.char(linked_skeleton_length)]
        
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass
    
    return {'FINISHED'}

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class LosaSkeleton(Operator, ImportHelper):
    """Import Lost Saga Skeleton (.skl)"""
    bl_idname = "io3d.skeleton_import" 
    bl_label = "Import Lost Saga Skeleton (.skl)"

    filename_ext = ".skl"

    filter_glob: StringProperty(
        default="*.skl",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    mode: EnumProperty(
        name="Mode",
        description="Resulting object to import as",
        items=(
            ('ARMATURE', "Armature", "Import as armature object. Intended for weight painting"),
            ('EMPTY', "Empty", "Import skeleton as empty object. Intended for animation"),
        ),
        default='ARMATURE',
    )
    
    legs_IK: BoolProperty(
        name="Use IK for legs",
        description="Whether to use inverse kinematics for legs",
        default=False,
    )
    
    hands_IK: BoolProperty(
        name="Use IK for hands",
        description="Whether to use inverse kinematics for hands",
        default=False,
    )

    def execute(self, context):
        return import_skeleton(context, self.filepath, self.mode, self.legs_IK, self.hands_IK)

def menu_func_import(self, context):
    self.layout.operator(LosaSkeleton.bl_idname, text="Lost Saga Skeleton (.skl)", icon='OUTLINER_OB_ARMATURE')

def register():
    bpy.utils.register_class(LosaSkeleton)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(LosaSkeleton)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)