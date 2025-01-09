import bpy


class EXPERIMENTAL_PANEL(bpy.types.Panel):
    bl_category = 'IO3D'
    bl_idname = 'OBJECT_PT_io3d_experimental_panel'
    bl_label = 'EXPERIMENTAL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column()
        col.label(text='All features inside this', icon='EXPERIMENTAL')
        col.label(text='panel is still experimental')
        
        col = layout.column()
        col.label(text='Mesh', icon='OUTLINER_DATA_MESH')
        col.label(text='Note: Mesh is already processed')
        col.label(text='before exporting, no need for')
        col.label(text='triangulate/flip uv maps, etc')
        col.operator('io3d.mesh_export', text='Export Mesh', icon='OUTLINER_OB_MESH')
        
        col = layout.column()
        col.label(text='Animation:', icon='ANIM')
        col.label(text='In order to import animation,')
        col.label(text='import armature as empty, select')
        col.label(text='the empty, and then import')
        col.label(text='animaion')
        col.operator('io3d.animation_import', text='Import Animation', icon='ANIM')
        col.operator('io3d.retarget', text='Form/Retarget Armature', icon='OUTLINER_OB_ARMATURE')

def register():
    bpy.utils.register_class(EXPERIMENTAL_PANEL)

def unregister():
    bpy.utils.unregister_class(EXPERIMENTAL_PANEL)