import bpy
from bpy.props import StringProperty, BoolProperty, PointerProperty
from bpy.types import PropertyGroup


class ResourceFolderProperty(PropertyGroup):
    path: StringProperty(
        name="",
        description="Resource Folder Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

class SKL_MSH_PANEL_PROPERTIES(PropertyGroup):
    time_stretching: BoolProperty(
        name='Time Stretching',
        description='When enabled, time stretching will be used based off current ' \
            'scene fps. Only use if you want to animate on your current fps as opposed ' \
            'to 100 fps, or when you already have animation on your object.',
        default=False,
    )

def register():
    bpy.utils.register_class(ResourceFolderProperty)
    bpy.utils.register_class(SKL_MSH_PANEL_PROPERTIES)
    bpy.types.Scene.io3d_resource_path = PointerProperty(type=ResourceFolderProperty)
    bpy.types.Scene.io3d_skl_msh_props = PointerProperty(type=SKL_MSH_PANEL_PROPERTIES)

def unregister():
    del bpy.types.Scene.io3d_skl_msh_props
    del bpy.types.Scene.io3d_resource_path
    bpy.utils.unregister_class(ResourceFolderProperty)
    bpy.utils.unregister_class(SKL_MSH_PANEL_PROPERTIES)
