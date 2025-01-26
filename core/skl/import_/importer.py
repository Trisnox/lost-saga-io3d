import bpy
import math
import mathutils
import pathlib
import struct

from ...classes.seeker import Seeker
from ....operators.form_armature import ArmatureForm

def is_skeleton_file(bytes):
    encrypted_skeleton_token = 0x105C5B63
    decrypted_check = encrypted_skeleton_token - 0x10101010
    return bytes == decrypted_check


def import_skeleton(context: bpy.types.Context, filepath: str, mode: str, armature_mode: str):
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

    basename = pathlib.Path(filepath).stem

    if mode == 'LITE':
        armature_data = bpy.data.armatures.new(basename)
        armature_object = bpy.data.objects.new(basename, armature_data)
        armature_object.show_in_front = True
        
        context.scene.collection.objects.link(armature_object)
        
        armature_object.select_set(state=True)
        context.view_layer.objects.active = armature_object

        bpy.ops.object.mode_set(mode='EDIT')

        bones = {}
    elif mode == 'ADVANCED':
        armature_collection = bpy.data.collections.new(basename + '_armature')
        context.scene.collection.children.link(armature_collection)
        empties_collection = bpy.data.collections.new('empties')
        armature_collection.children.link(empties_collection)
        
    
    version = struct.unpack('<I', skl[s.o:s.i])[0]
    biped_count = struct.unpack('<I', skl[s.o:s.i])[0]
    bone_data = {}
    bone_parenting = {}
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
        # LocalTMvPos = mathutils.Vector((LocalTMvPos[0], LocalTMvPos[2], LocalTMvPos[1]))
        LocalTMvPos = mathutils.Vector(LocalTMvPos)

        LocalTMqRot = struct.unpack('<4f', skl[s.o:s.qrot])
        # LocalTMqRot = mathutils.Quaternion((LocalTMqRot[3], -LocalTMqRot[0], -LocalTMqRot[2], -LocalTMqRot[1]))
        x, y, z, w = LocalTMqRot
        LocalTMqRot = mathutils.Quaternion((w, x, y, z))

        # Unused
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
        
        if mode == 'LITE':
            edit_bone = armature_data.edit_bones.new(biped_bone_name)
            edit_bone.matrix = converted_matrix
            bones[biped_bone_name] = edit_bone
        elif mode == 'ADVANCED':
            empty = bpy.data.objects.new(biped_bone_name, None)
            empty.empty_display_type = 'PLAIN_AXES'
            empties_collection.objects.link(empty)
            
            empty['Position Rest X'] = LocalTMvPos.x
            empty['Position Rest Y'] = LocalTMvPos.y
            empty['Position Rest Z'] = LocalTMvPos.z
            empty['Quaternion Rest W'] = LocalTMqRot.w
            empty['Quaternion Rest X'] = LocalTMqRot.x
            empty['Quaternion Rest Y'] = LocalTMqRot.y
            empty['Quaternion Rest Z'] = LocalTMqRot.z

            if biped_bone_name == 'Bip01':
                origin_empty = bpy.data.objects.new('origin_correction', None)
                origin_empty.empty_display_type = 'PLAIN_AXES'
                empties_collection.objects.link(origin_empty)
                bone_data['origin_correction'] = (origin_empty, mathutils.Vector(), mathutils.Quaternion())
                
                rot_x = mathutils.Quaternion((1, 0, 0), math.radians(-90))
                rot_y = mathutils.Quaternion((0, 1, 0), math.radians(180))
                origin_rotation = rot_y @ rot_x

                origin_empty['Position Rest X'] = 0.0
                origin_empty['Position Rest Y'] = 0.0
                origin_empty['Position Rest Z'] = 0.0
                origin_empty['Quaternion Rest W'] = origin_rotation.w
                origin_empty['Quaternion Rest X'] = origin_rotation.x
                origin_empty['Quaternion Rest Y'] = origin_rotation.y
                origin_empty['Quaternion Rest Z'] = origin_rotation.z

                bpy.ops.object.select_all(action='DESELECT')
                empty.select_set(True)
                origin_empty.select_set(True)
                context.view_layer.objects.active = origin_empty
                bpy.ops.object.parent_set(keep_transform=True)

                # Actually not needed
                # bone_parenting['origin_correction'] = biped_bone_name
            
            # To ensure bone order inside dictionary
            bone_data[biped_bone_name] = (empty, LocalTMvPos, LocalTMqRot)

        if parent_name and not parent_name == 'NoParent': # NoParent indicates root
            if mode == 'LITE':
                edit_bone.parent = bones[parent_name]
                edit_bone.head = bones[parent_name].tail
            elif mode == 'ADVANCED':
                parent_empty = [item for item in empties_collection.objects if item.name.startswith(parent_name)][0]
                bpy.ops.object.select_all(action='DESELECT')
                empty.select_set(True)
                parent_empty.select_set(True)
                context.view_layer.objects.active = parent_empty
                bpy.ops.object.parent_set(keep_transform=True)

        if mode == 'LITE':
            if edit_bone.head == edit_bone.tail: # blender removes bones if the head and tail have the exact same position
                edit_bone.tail.y += 0.1

        child_count = struct.unpack('<I', skl[s.o:s.i])[0]
        for _ in range(1, child_count+1):
            child_length = struct.unpack('<I', skl[s.o:s.i])[0]
            child_bone_name = None
            if child_length:
                child_bone_name = skl[s.o:s.char(child_length)].decode('utf-8')
                res = bone_parenting.get(biped_bone_name)
                if res:
                    continue

                bone_parenting[biped_bone_name] = child_bone_name
    
    if mode == 'ADVANCED':
        armature_hide = True if armature_mode == 'EMPTY' else False
        empty_hide = not armature_hide

        bone_length = {}
        for parent_name, child_name in bone_parenting.items():
            child_bone_length = bone_data[child_name][1]
            bone_length[parent_name] = (child_bone_length.x if child_bone_length.x >= 1.0 else 1.0, 1.0, 1.0)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0.1, 0.0, 0.0))
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
        shape = context.view_layer.objects.active
        shape.name = 'armature_base_shape'
        shape.hide_render = True
        shape.hide_viewport = True

        for collection in shape.users_collection:
            collection.objects.unlink(shape)

        for bone, position, rotation in bone_data.values():
            bone.location = position
        
        bpy.ops.object.select_all(action='DESELECT')
        root = next(iter(bone_data.values()))[0]
        root.select_set(True)
        context.view_layer.objects.active = root

        retarget_armature = ArmatureForm.generate_with_return(context)
        for collection in retarget_armature.users_collection:
            collection.objects.unlink(retarget_armature)
        armature_collection.objects.link(retarget_armature)
        armature_collection.objects.link(shape)

        for bone, position, rotation in bone_data.values():
            bone.rotation_mode = 'QUATERNION'
            bone.rotation_quaternion = rotation

        retarget_armature.select_set(True)
        context.view_layer.objects.active = retarget_armature
        bpy.ops.object.mode_set(mode='POSE')

        # Alright, small problem here
        # Turns out, pose bone does need to define location, attempting to define location would've just make the armature appear 2x as big
        # Why did I apply the location? because the empties rely on it, so I just scale the object by half to make it appear like normal
        # If it wasn't for animation exporting, I wouldn't have done it
        # With that being said, please do not apply loc/rot/scale for any armature object, they will fuck up the exporter
        for pose_bone in retarget_armature.pose.bones:
            empty, position, rotation = bone_data[pose_bone.name]

            shape_length = bone_length.get(pose_bone.name, (1.0, 1.0, 1.0))
            pose_bone.custom_shape = shape
            pose_bone.custom_shape_scale_xyz = shape_length

            # Blender keeps nagging about depedency cycles despite being muted
            # Solution is to store the object data inside property, and then remove/add the constraints when swapped
            if armature_hide:
                pose_bone.location = mathutils.Vector()
                pose_bone.rotation_quaternion = mathutils.Quaternion()

                pose_const = pose_bone.constraints.new('COPY_TRANSFORMS')
                pose_const.name = 'Retarget'
                pose_const.target = empty
                pose_const.target_space = 'LOCAL'
                pose_const.owner_space = 'LOCAL'

            if empty_hide:
                empty.location = mathutils.Vector()
                empty.rotation_quaternion = mathutils.Quaternion()

                empty_consts = empty.constraints.new('COPY_TRANSFORMS')
                empty_consts.name = 'Retarget'
                empty_consts.target = retarget_armature
                empty_consts.subtarget = pose_bone.name
                empty_consts.target_space = 'LOCAL'
                empty_consts.owner_space = 'LOCAL'

                pose_bone.location = position
                pose_bone.rotation_quaternion = rotation

            pose_bone['Position Rest X'] = empty['Position Rest X']
            pose_bone['Position Rest Y'] = empty['Position Rest Y']
            pose_bone['Position Rest Z'] = empty['Position Rest Z']
            pose_bone['Quaternion Rest W'] = empty['Quaternion Rest W']
            pose_bone['Quaternion Rest X'] = empty['Quaternion Rest X']
            pose_bone['Quaternion Rest Y'] = empty['Quaternion Rest Y']
            pose_bone['Quaternion Rest Z'] = empty['Quaternion Rest Z']
            
            pose_bone['Bone Reference'] = empty
            pose_bone['Bone Reference Subtarget'] = None
            empty['Bone Reference'] = retarget_armature
            empty['Bone Reference Subtarget'] = pose_bone.name
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        root = bone_data['Bip01'][0]
        root.select_set(True)
        context.view_layer.objects.active = root
        mesh_armature = ArmatureForm.generate_with_return(context, True)
        mesh_armature.name = 'mesh_armature'
        context.scene.collection.objects.unlink(mesh_armature)
        armature_collection.objects.link(mesh_armature)
        mesh_armature['Rotation Correction'] = True

        if not empty_hide:
            origin, _, _ = bone_data['origin_correction']
            rot_x = mathutils.Quaternion((1, 0, 0), math.radians(-90))
            rot_y = mathutils.Quaternion((0, 1, 0), math.radians(180))
            origin.rotation_quaternion = rot_y @ rot_x
            origin.scale.x = -1

        bpy.ops.object.mode_set(mode='POSE')
        for pose_bone in mesh_armature.pose.bones:
            empty = bone_data[pose_bone.name][0]
            const = pose_bone.constraints.new('COPY_TRANSFORMS')
            const.target = empty
        bpy.ops.object.mode_set(mode='OBJECT')

        if not armature_hide:
            mesh_armature.select_set(False)
            retarget_armature.select_set(True)
            context.view_layer.objects.active = retarget_armature

            bpy.ops.object.mode_set(mode='POSE')
            pose_bone = retarget_armature.pose.bones.get('origin_correction')
            rot_x = mathutils.Quaternion((1, 0, 0), math.radians(-90))
            rot_y = mathutils.Quaternion((0, 1, 0), math.radians(180))
            pose_bone.rotation_quaternion = rot_y @ rot_x
            pose_bone.scale.x = -1
            bpy.ops.object.mode_set(mode='OBJECT')

        retarget_armature.scale = mathutils.Vector((0.5, 0.5, 0.5))
        retarget_armature.hide_viewport = armature_hide
        empties_collection.hide_viewport = empty_hide
        mesh_armature.hide_viewport = True
    
    linked_skeleton_length = struct.unpack('<I', skl[s.o:s.i])[0]
    if linked_skeleton_length:
        linked_skeleton_name = skl[s.o:s.char(linked_skeleton_length)]
        
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass
    
    return {'FINISHED'}

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, EnumProperty
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
        description="Skeleton importer mode to choose from.",
        items=(
            ("LITE", "Lite", "Import skeleton by using x-axis bone rotation. Not intended for animation (import/export)"),
            ("ADVANCED", "Advanced", "Import skeleton by using y-axis bone rotation. Intended for animation (import/export)"),
        ),
        default="LITE",
    )
    
    armature_mode: EnumProperty(
        name="Display",
        description="Choose whichever display the armature will be used on. Either choice will not affect the importer/exporter",
        items=(
            ("EMPTY", "Empty", "Display skeleton as empty, plain axes"),
            ("ARMATURE", "Armature", "Display skeleton as armature. Not recommended for importing animation"),
        ),
        default="EMPTY"
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mode")

        col = layout.column()
        col.enabled = (self.mode == 'ADVANCED')
        col.prop(self, "armature_mode")

    def execute(self, context):
        return import_skeleton(context, self.filepath, self.mode, self.armature_mode)

def menu_func_import(self, context):
    self.layout.operator(LosaSkeleton.bl_idname, text="Lost Saga Skeleton (.skl)", icon='OUTLINER_OB_ARMATURE')

def register():
    bpy.utils.register_class(LosaSkeleton)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(LosaSkeleton)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)