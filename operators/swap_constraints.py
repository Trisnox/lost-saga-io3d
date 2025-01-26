import bpy
import mathutils


def swap_constraints(context: bpy.types.Context):
    active_object = context.active_object
    armature_collection = None
    collections_iter = active_object.users_collection if active_object.type == 'ARMATURE' else bpy.data.collections

    for col in collections_iter:
        if 'empties' in col.children:
            armature_collection = col
            break
    
    if not armature_collection:
        def draw(self, context):
            self.layout.label(text='Cannot find empties collection.')

        context.window_manager.popup_menu(draw, title='ERROR | MISSING ITEM', icon='WARNING_LARGE')
        raise RuntimeError('Cannot find empties collection.')
    
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass

    # I could've just did armature_collection.get('empties'/'retarget_armature'), but that won't work against duplicate items,
    # since duplicate items have suffixes on them
    empties_collection = [item for item in armature_collection.children if item.name.startswith('empties')][0]
    armature_object = [item for item in armature_collection.objects if item.name.startswith('retarget_armature')][0]

    empties_collection.hide_viewport = False
    armature_object.hide_viewport = False

    for empty in empties_collection.objects:
        const = empty.constraints.get('Retarget')
        if not const:
            empty_consts = empty.constraints.new('COPY_TRANSFORMS')
            empty_consts.name = 'Retarget'
            empty_consts.target = empty['Bone Reference']
            empty_consts.subtarget = empty['Bone Reference Subtarget']
            empty_consts.target_space = 'LOCAL'
            empty_consts.owner_space = 'LOCAL'

            empty.location = mathutils.Vector()
            empty.rotation_quaternion = mathutils.Quaternion()
        else:
            empty.constraints.remove(const)
            empty.location = mathutils.Vector((empty['Position Rest X'], empty['Position Rest Y'], empty['Position Rest Z']))
            empty.rotation_quaternion = mathutils.Quaternion((empty['Quaternion Rest W'], empty['Quaternion Rest X'], empty['Quaternion Rest Y'], empty['Quaternion Rest Z']))
    
    empty_state = const

    bpy.ops.object.select_all(action='DESELECT')
    armature_object.select_set(True)
    context.view_layer.objects.active = armature_object

    bpy.ops.object.mode_set(mode='POSE')
    for pose_bone in armature_object.pose.bones:
        const = pose_bone.constraints.get('Retarget')
        if not const:
            pose_bone.location = mathutils.Vector()
            pose_bone.rotation_quaternion = mathutils.Quaternion()

            pose_const = pose_bone.constraints.new('COPY_TRANSFORMS')
            pose_const.name = 'Retarget'
            pose_const.target = pose_bone['Bone Reference']
            pose_const.target_space = 'LOCAL'
            pose_const.owner_space = 'LOCAL'
        else:
            pose_bone.constraints.remove(const)
            pose_bone.location = mathutils.Vector((pose_bone['Position Rest X'], pose_bone['Position Rest Y'], pose_bone['Position Rest Z']))
            pose_bone.rotation_quaternion = mathutils.Quaternion((pose_bone['Quaternion Rest W'], pose_bone['Quaternion Rest X'], pose_bone['Quaternion Rest Y'], pose_bone['Quaternion Rest Z']))

    bpy.ops.object.mode_set(mode='OBJECT')

    if empty_state:
        armature_object.hide_viewport = True
    else:
        empties_collection.hide_viewport = True
        armature_object.select_set(True)
        context.view_layer.objects.active = armature_object

    return {'FINISHED'}


from bpy.types import Operator


class SwapConstraints(Operator):
    """Swap advanced armature from empty to armature or vice versa"""
    bl_idname = "io3d.swap_constraints"
    bl_label = "Swap armature display"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type in ('EMPTY', 'ARMATURE')

    def execute(self, context):
        return swap_constraints(context)


def register():
    bpy.utils.register_class(SwapConstraints)


def unregister():
    bpy.utils.unregister_class(SwapConstraints)
