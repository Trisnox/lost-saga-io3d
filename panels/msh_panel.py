import bpy


class MSH_PANEL(bpy.types.Panel):
    bl_category = 'IO3D'
    bl_idname = 'OBJECT_PT_io3d_msh_panel'
    bl_label = 'MSH'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        msh_props = scene.io3d_msh_props

        col = layout.column()
        col.label(text='Material Utility:', icon='NODE_MATERIAL')
        row = layout.row()
        row.operator('io3d.import_nodes', text='Import Losa Shader', icon='MATERIAL')
        row.operator('io3d.generate_material', text='Generate Material', icon='MATERIAL')
        col = layout.column()
        col.operator('io3d.to_opaque', text='Turn material into opaque', icon='SNAP_VOLUME')
        col.operator('io3d.to_transparent', text='Turn material into transparent', icon='MOD_WIREFRAME')
        col.operator('io3d.toggle_shadeless', text='Toggle Shadeless', icon='OUTLINER_OB_LIGHTPROBE')

        row = layout.row()
        row.label(text='Visibility:', icon='HIDE_OFF')

        # col = layout.column()
        # col.operator('io3d.toggle_transparency_overlap', text='Toggle Transparency Overlap', icon='MATERIAL')
        # row = col.row()
        # row.label(text=f'Current: {msh_props.transparency_overlap}')

        row = layout.row()

        col = layout.column()
        col.operator('io3d.toggle_backface_culling', text='Toggle Backface Culling', icon='XRAY')
        row = col.row()
        row.label(text=f'Current: {msh_props.backface_culling}')

        row = layout.row()

        col = layout.column()
        col.operator('io3d.toggle_outline', text='Toggle Outline', icon='MOD_SOLIDIFY')
        row = col.row()
        row.label(text=f'Current: {msh_props.outline_active}')
        

def register():
    bpy.utils.register_class(MSH_PANEL)


def unregister():
    bpy.utils.unregister_class(MSH_PANEL)