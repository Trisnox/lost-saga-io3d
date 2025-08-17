bl_info = {
	"name": "Lost Saga IO3D Mesh",
	"author": "Trisnox",
	"version": (1, 5, 3),
	"blender": (4, 1, 0),
	"location": "View3D > Sidebar > IO3D",
	"description": "Tools to import/export various Lost Saga formats",
	"category": "Import-Export",
}

import bpy

from . import addon_updater_ops

from .properties import animation_data, animation_panel_props, skl_msh_panel_props, msh_panel_props

from .core.skl.import_ import importer as skl_importer
from .core.msh.import_ import importer as msh_importer
from .core.ani.import_ import importer as ani_importer
from .core.ani.export import exporter as ani_exporter
from .core.msh.export import exporter as msh_exporter

from .operators import import_nodes, generate_material, to_opaque, to_transparent, toggle_outline, toggle_shadeless, toggle_transparency_overlap, toggle_backface_culling, split_mesh, get_bounding, apply_animation, attach_armature, flip_pose, form_armature, frame_remapping, mirror_bone, remove_animation_entry, rename_bones, reset_rest_state, apply_delta, retarget_animation, scene_setup, swap_constraints

from .panels import animation_panel, skl_msh_panel, msh_panel, material_panel, updater_panel

m_bl_info = bl_info

classes = [
	animation_data,
	animation_panel_props,
	skl_msh_panel_props,
	msh_panel_props,
	skl_importer,
	msh_importer,
	ani_importer,
	ani_exporter,
	msh_exporter,
	import_nodes,
	generate_material,
	to_opaque,
	to_transparent,
	toggle_shadeless,
	toggle_transparency_overlap,
	toggle_backface_culling,
	toggle_outline,
	split_mesh,
	get_bounding,
	apply_animation,
	attach_armature,
	flip_pose,
	form_armature,
	frame_remapping,
	mirror_bone,
	remove_animation_entry,
	rename_bones,
	reset_rest_state,
	apply_delta,
	retarget_animation,
	scene_setup,
	swap_constraints,
	skl_msh_panel,
	msh_panel,
	material_panel,
	animation_panel,
	updater_panel
]

@addon_updater_ops.make_annotations
class io3dPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__
	bl_options = {"DEFAULT_CLOSED"}
	auto_check_update = bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=False)

	updater_interval_months = bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0)

	updater_interval_days = bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=7,
		min=0,
		max=31)

	updater_interval_hours = bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23)

	updater_interval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59)

	def draw(self, context):
		layout = self.layout

		# Works best if a column, or even just self.layout.
		mainrow = layout.row()
		col = mainrow.column()

		# Updater draw function, could also pass in col as third arg.
		addon_updater_ops.update_settings_ui(self, context)

def register():
	addon_updater_ops.register(m_bl_info)
	addon_updater_ops.make_annotations(io3dPreferences)
	bpy.utils.register_class(io3dPreferences)
	
	for cls in classes:
		cls.register()
	
def unregister():
	addon_updater_ops.unregister()
	bpy.utils.unregister_class(io3dPreferences)
	
	for cls in reversed(classes):
		cls.unregister()