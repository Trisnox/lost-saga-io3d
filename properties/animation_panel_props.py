import bpy

from bpy.props import IntProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup


class ANIMATION_PANEL_PROPERTIES(PropertyGroup):
    use_current_fps: BoolProperty(
        name='Use Scene FPS',
        description='When enabled, imported animation will use scene fps instead of the usual 60',
        default=True,
    )

    override_fps: IntProperty(
        name='fps',
        description='fps to calculate frames for iTime variable',
        default=60,
    )

    insert_at: EnumProperty(
        name='Frame insert: ',
        description='Property to define where the animation should be inserted',
        items=(
            ('CURRENT', 'Current frame', 'Insert at current frame'),
            ('FIRST', 'First frame', 'Insert at first frame'),
            ('SET', 'Set frame', 'Insert at user defined frame'),
        ),
        default='CURRENT',
    )

    frame_set: IntProperty(
        name='frame',
        description='Frame offset to insert animation',
        default=0
    )


def register():
    bpy.utils.register_class(ANIMATION_PANEL_PROPERTIES)
    bpy.types.Scene.io3d_anim_props = PointerProperty(type=ANIMATION_PANEL_PROPERTIES)

def unregister():
    del bpy.types.Scene.io3d_anim_props
    bpy.utils.unregister_class(ANIMATION_PANEL_PROPERTIES)
