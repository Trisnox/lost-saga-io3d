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
        default=100,
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

    frame_range: EnumProperty(
        name="Frame Range",
        description="Frame range to import animation",
        items=(
            ("ALL", "All", "Import animation on all range"),
            ("PARTIAL", "Partial", "Import animation within frame range"),
        ),
        default="ALL",
    )

    frame_start: IntProperty(
        name="Frame Start",
        description="Frame start",
        min=1,
        default=1,
    )

    frame_end: IntProperty(
        name="Frame End",
        description="Frame end",
        min=1,
        default=100,
    )

    apply_rest_rotation: BoolProperty(
        name='Apply Rest Rotation',
        description='When enabled, rest rotation will be applied to animation that sourced from retarget',
        default=True,
    )

    mirror_target: EnumProperty(
        name='Mirror Target',
        description='Choose target to mirror to/from',
        items=(
            ('MIRROR', 'Mirror opposite bones', 'Mirror pose from currently selected bones to the opposing bones'),
            ('COPY', 'Copy opposite bones', 'Copy pose from opposing bones to the currently selected bones'),
        ),
        default='MIRROR',
    )

    location: BoolProperty(
        name='Location',
        description='When enabled, Reset Rest and Mirror Pose will also set object\'s location',
        default=True
    )

    rotation: BoolProperty(
        name='Rotation',
        description='When enabled, Reset Rest and Mirror Pose will also set object\'s rotation',
        default=True
    )


def register():
    bpy.utils.register_class(ANIMATION_PANEL_PROPERTIES)
    bpy.types.Scene.io3d_anim_props = PointerProperty(type=ANIMATION_PANEL_PROPERTIES)

def unregister():
    del bpy.types.Scene.io3d_anim_props
    bpy.utils.unregister_class(ANIMATION_PANEL_PROPERTIES)
