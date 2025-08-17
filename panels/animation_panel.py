import bpy

class ANIMATION_UL_entries(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        scene = context.scene
        fps = scene.render.fps if scene.io3d_anim_props.use_current_fps else scene.io3d_anim_props.override_fps
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", text="", icon='ARMATURE_DATA' if not item.is_retarget else 'DRIVER', emboss=False, expand=True)
            row = row.row()
            row.alignment = 'RIGHT'
            row.label(text = str(int(round((item.total_time * fps) / 1000)) + 1))

class ANIMATION_PANEL(bpy.types.Panel):
    bl_category = 'IO3D'
    bl_idname = 'OBJECT_PT_io3d_animation_panel'
    bl_label = 'ANI'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        anim_data = context.scene.io3d_animation_data
        anim_props = context.scene.io3d_anim_props

        row = layout.row()
        row.label(text='Utility:', icon='OPTIONS')
        col = layout.column()
        col.operator('io3d.flip_pose', text='Flip pose', icon='GROUP_BONE')
        col = layout.column()
        col.operator('io3d.mirror_pose', text='Mirror pose', icon='MOD_MIRROR')
        col = layout.column()
        col.operator('io3d.reset_rest', text='Reset rest state', icon='ARMATURE_DATA')
        col = layout.column()
        col.prop(anim_props, 'mirror_target')
        row = layout.row()
        row.prop(anim_props, 'location')
        row.prop(anim_props, 'rotation')
        col = layout.column()
        col.operator('io3d.swap_constraints', text='Swap armature display', icon='MOD_ARMATURE')
        col.operator('io3d.frame_remap', text='Remap frames', icon='MOD_TIME')

        row = layout.row()
        row.label(text='Animation:', icon='POSE_HLT')
        col = layout.column()
        col.operator('io3d.anim_export', text='Export Animation', icon='ANIM')
        col = layout.column()
        col.operator('io3d.apply_delta', text='Apply Delta Transformations', icon='DRIVER')

        col = layout.column()
        col.label(text='In order to use animation, import')
        col.label(text='skeleton using advanced mode')

        row = layout.row()
        row.label(text='')

        box = layout.box()
        box = box.row(align=True)
        box.label(text='Animation Name', icon='BLANK1')

        box = box.row()
        box.alignment = 'CENTER'
        box.label(text=' | ')

        box = box.row()
        box.alignment = 'RIGHT'
        box.label(text='Frames')

        col = layout.column()
        col.template_list("ANIMATION_UL_entries", "", anim_data, "entry", anim_data, "active_entry_index")

        row = layout.row(align=True)
        row.operator('io3d.animation_import', text='Import Animation', icon='ANIM')
        row.operator('io3d.remove_entry', text='Delete', icon='REMOVE')
        row.operator('io3d.entry_export', text='Export', icon='FILE_LARGE')
        
        row = layout.row()
        row.prop(anim_props, 'apply_rest_rotation')
        row = layout.row()
        row.prop(anim_props, 'use_current_fps')
        row = row.row()
        row.enabled = not anim_props.use_current_fps
        row.prop(anim_props, 'override_fps')

        row = layout.row()
        row.prop(anim_props, 'frame_range')
        row = layout.row()
        row.enabled = anim_props.frame_range == 'PARTIAL'
        row.prop(anim_props, 'frame_start')
        row.prop(anim_props, 'frame_end')

        row = layout.row()
        row.prop(anim_props, 'insert_at')
        row = row.row()
        row.enabled = (anim_props.insert_at == 'SET')
        row.prop(anim_props, 'frame_set')

        col = layout.column()
        col.operator('io3d.apply_animation', text='Apply Animation', icon='ARMATURE_DATA')

def register():
    bpy.utils.register_class(ANIMATION_UL_entries)
    bpy.utils.register_class(ANIMATION_PANEL)

def unregister():
    bpy.utils.unregister_class(ANIMATION_PANEL)
    bpy.utils.unregister_class(ANIMATION_UL_entries)