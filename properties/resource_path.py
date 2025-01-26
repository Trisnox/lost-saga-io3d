import bpy
from bpy.props import StringProperty, PointerProperty
from bpy.types import PropertyGroup


class ResourceFolderProperty(PropertyGroup):
    path: StringProperty(
        name="",
        description="Resource Folder Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')


def register():
    bpy.utils.register_class(ResourceFolderProperty)
    bpy.types.Scene.io3d_resource_path = PointerProperty(type=ResourceFolderProperty)

def unregister():
    del bpy.types.Scene.io3d_resource_path
    bpy.utils.unregister_class(ResourceFolderProperty)
