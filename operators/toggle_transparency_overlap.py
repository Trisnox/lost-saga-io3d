from bpy.types import Operator
import bpy


def toggle_overlap(context: bpy.types.Context):
    scene = context.scene
    transparency_overlap = scene.io3d_msh_props.transparency_overlap = not scene.io3d_msh_props.transparency_overlap
    for material in bpy.data.materials:
        if material.blend_method == 'BLEND':
            material.use_transparency_overlap = transparency_overlap

    return {'FINISHED'}


class TransparencyOverlap(Operator):
    """Toggle Transparency Overlap for all applicable material"""
    bl_idname = "io3d.toggle_transparency_overlap"
    bl_label = "Toggle Transparency Overlap for all applicable material"

    def execute(self, context):
        return toggle_overlap(context)


def register():
    bpy.utils.register_class(TransparencyOverlap)

def unregister():
    bpy.utils.unregister_class(TransparencyOverlap)
