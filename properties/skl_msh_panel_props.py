import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup


class ResourceFolderProperty(PropertyGroup):
    path: StringProperty(
        name="",
        description="Resource Folder Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
        )

class SKL_MSH_PANEL_PROPERTIES(PropertyGroup):
    time_stretching: BoolProperty(
        name='Time Stretching',
        description='When enabled, time stretching will be used based off current ' \
            'scene fps. Only use if you want to animate on your current fps as opposed ' \
            'to 100 fps, or when you already have animation on your object.',
        default=False,
    )

class MeshTypes(PropertyGroup):
    mesh_type: EnumProperty(
        name='Mesh Type: ',
        description='Property to define the type of mesh',
        items=(
            ('STATIC', 'Static', 'Static meshes, does not contain weights. For map background, use lightmap instead.'),
            ('ANIMATION', 'Animation', 'Meshes with weights. Used in conjuction with armature'),
            ('LIGHTMAP', 'Lightmap', 'Meshes with multiple UVmap, does not contain normals. Used for background meshes'),
        ),
        default='STATIC',
    )

def register():
    bpy.utils.register_class(ResourceFolderProperty)
    bpy.utils.register_class(SKL_MSH_PANEL_PROPERTIES)
    bpy.utils.register_class(MeshTypes)
    bpy.types.Scene.io3d_resource_path = PointerProperty(type=ResourceFolderProperty)
    bpy.types.Scene.io3d_skl_msh_props = PointerProperty(type=SKL_MSH_PANEL_PROPERTIES)
    bpy.types.Scene.io3d_mesh_types = PointerProperty(type=MeshTypes)

def unregister():
    del bpy.types.Scene.io3d_skl_msh_props
    del bpy.types.Scene.io3d_resource_path
    del bpy.types.Scene.io3d_mesh_types
    bpy.utils.unregister_class(ResourceFolderProperty)
    bpy.utils.unregister_class(SKL_MSH_PANEL_PROPERTIES)
    bpy.utils.unregister_class(MeshTypes)
