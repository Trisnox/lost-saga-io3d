import bpy
import mathutils
import numpy as np


def is_using_newer_version():
    return bpy.app.version >= (4, 4, 0)

def apply_delta(context):
    while True:
        res = bpy.ops.object.select_grouped(extend=True, type='PARENT')
        if res == {'CANCELLED'}:
            break

    root = context.object
    bones_iter = [root] + [_ for _ in root.children_recursive]

    for bone in bones_iter:
        if bone.name == 'origin_correction':
            continue

        action = bone.animation_data.action

        if is_using_newer_version:
            fcurves = action.layers[0].strips[0].channelbag(action.slots[0]).fcurves
        else:
            fcurves = action.fcurves

        data_path_location = 'location'
        data_path_rotation = 'rotation_quaternion'

        fcurve_location = []
        fcurve_rotation = []

        for fcurve in fcurves:
            if fcurve.data_path == data_path_location:
                fcurve_location.append(fcurve)
            elif fcurve.data_path == data_path_rotation:
                fcurve_rotation.append(fcurve)

        delta_position = bone.delta_location
        delta_rotation = bone.delta_rotation_quaternion

        for index, fcurve in enumerate(fcurve_location):
            keyframe_count = len(fcurve.keyframe_points)

            coords = np.zeros(keyframe_count * 2)
            fcurve.keyframe_points.foreach_get('co', coords)
            
            coords[1::2] = [pos + delta_position[index] for pos in coords[1::2]]
            # coords[1::2] = [delta_position[index]] * keyframe_count
            
            fcurve.keyframe_points.foreach_set('co', coords)

        # Knowing bake action, I knew quaternion always come in pairs
        raw_coords = []
        quaternion_coords = []
        for index, fcurve in enumerate(fcurve_rotation):
            keyframe_count = len(fcurve.keyframe_points)

            coords = np.zeros(keyframe_count * 2)
            fcurve.keyframe_points.foreach_get('co', coords)
            raw_coords.append(coords)
            quaternion_coords.append(coords[1::2])

        quaternion_coords = [delta_rotation @ mathutils.Quaternion((w, x, y, z)) for w, x, y, z in zip(*quaternion_coords)]

        for index, fcurve in enumerate(fcurve_rotation):
            coords = raw_coords[index]
            coords[1::2] = [rot[index] for rot in quaternion_coords]
            
            fcurve.keyframe_points.foreach_set('co', coords)

        bone.delta_location = mathutils.Vector()
        bone.delta_rotation_quaternion = mathutils.Quaternion()

    return {'FINISHED'}


from bpy.types import Operator


class ApplyDelta(Operator):
    """Apply delta transformation. Intended for retarget skeleton with animation data"""
    bl_idname = "io3d.apply_delta" 
    bl_label = "Apply Delta Transformation"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        return object is not None and object.type == 'EMPTY'

    def execute(self, context):
        return apply_delta(context)

def register():
    bpy.utils.register_class(ApplyDelta)

def unregister():
    bpy.utils.unregister_class(ApplyDelta)
