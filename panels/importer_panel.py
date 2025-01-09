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

class IMPORTER_PANEL(bpy.types.Panel):
    bl_category = 'IO3D'
    bl_idname = 'OBJECT_PT_io3d_importer_panel'
    bl_label = 'SKL/MSH Import'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        #col = layout.column()
        row = layout.row()
        row.operator('io3d.skeleton_import', text='Import Skeleton', text_ctxt='test', icon='OUTLINER_OB_ARMATURE')
        row.operator('io3d.mesh_import', text='Import Mesh', icon='OUTLINER_OB_MESH')
        
        col = layout.column()
        col.label(text='Resource folder:', icon='FILE_FOLDER')
        col.prop(scene.resource_path, 'path')
        
        row = layout.row()
        row.label(text='Utility:', icon='OPTIONS')
        col = layout.column()
        col.operator('io3d.armature_attach', text='Attach Armature', icon='ARMATURE_DATA')
        col.operator('io3d.rename_bones', text='Rename bones', icon='HELP')

def register():
    bpy.utils.register_class(IMPORTER_PANEL)
    bpy.utils.register_class(ResourceFolderProperty)
    
    bpy.types.Scene.resource_path = PointerProperty(type=ResourceFolderProperty)

def unregister():
    bpy.utils.unregister_class(IMPORTER_PANEL)
    bpy.utils.unregister_class(ResourceFolderProperty)
    
    del bpy.types.Scene.resource_path