import bpy


class SKL_MSH_PANEL(bpy.types.Panel):
    bl_category = 'IO3D'
    bl_idname = 'OBJECT_PT_io3d_skl_msh_panel'
    bl_label = 'SKL/MSH'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column()
        row = col.row()
        row.operator('io3d.skeleton_import', text='Import Skeleton', icon='OUTLINER_OB_ARMATURE')
        row.operator('io3d.mesh_import', text='Import Mesh', icon='OUTLINER_OB_MESH')

        # row = layout.split(factor=0.5)
        # box = row.box()
        # box.scale_y = 0.5
        # box.label(text='', icon='BLANK1')
        # row = row.row()
        # row.operator('io3d.mesh_import', text='Export Mesh', icon='OUTLINER_OB_MESH')
        
        col = layout.column()
        col.label(text='Resource folder:', icon='FILE_FOLDER')
        col.prop(scene.io3d_resource_path, 'path')
        
        row = layout.row()
        row.label(text='Utility:', icon='OPTIONS')
        col = layout.column()
        col.operator('io3d.armature_attach', text='Attach Armature', icon='ARMATURE_DATA')
        col.operator('io3d.rename_bones', text='Rename bones', icon='HELP')

def register():
    bpy.utils.register_class(SKL_MSH_PANEL)

def unregister():
    bpy.utils.unregister_class(SKL_MSH_PANEL)
