import bpy

from ..addon_updater_ops import update_settings_ui

class IO3D_UPDATER_PANEL(bpy.types.Panel):
	"""Panel to check/download updates from repository"""
	bl_label = "Updater"
	bl_idname = "OBJECT_PT_io3d_updater_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_context = "objectmode"
	bl_category = "IO3D"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		update_settings_ui(self, context)

def register():
	bpy.utils.register_class(IO3D_UPDATER_PANEL)

def unregister():
	bpy.utils.unregister_class(IO3D_UPDATER_PANEL)