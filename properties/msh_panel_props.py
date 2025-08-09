import bpy
from bpy.props import BoolProperty, PointerProperty, IntProperty
from bpy.types import PropertyGroup

class MSH_PANEL_PROPERTIES(PropertyGroup):
    transparency_overlap: BoolProperty(
        name='Toggle Transparency Overlap',
        description='When turned on, it allows all material to overlap ' \
                    'transparency with one another, which may cause ' \
                    'transparency sorting problems, otherwise it will ' \
                    'not show any overlapping transparency.',
        default=False,
    )

    backface_culling: BoolProperty(
        name='Toggle Backface Culling',
        description='When turned on, mesh will not render its backface. ' \
                    'Commonly used in games to optimize rendering ',
        default=False,
    )

    outline_active: BoolProperty(
        name='Toggle Outline',
        description='Toggle outline, only works if outline was generated using modifier',
        default=True,
    )

    surpress_split: BoolProperty(
        name="Don't split faces",
        description='When enabled, mesh will not have their faces split. Assumes manual split as it may cause UV distortion.',
        default=False,
    )

    split_threshold: IntProperty(
        name='Face Threshold',
        description='Maximum face each mesh will have.',
        default=10000,
        min=0,
        max=100000,
    )

def register():
    bpy.utils.register_class(MSH_PANEL_PROPERTIES)
    bpy.types.Scene.io3d_msh_props = PointerProperty(type=MSH_PANEL_PROPERTIES)

def unregister():
    del bpy.types.Scene.io3d_msh_props
    bpy.utils.unregister_class(MSH_PANEL_PROPERTIES)
