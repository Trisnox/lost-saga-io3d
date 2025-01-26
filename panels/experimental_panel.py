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

def register():
    bpy.utils.register_class(EXPERIMENTAL_PANEL)

def unregister():
    bpy.utils.unregister_class(EXPERIMENTAL_PANEL)