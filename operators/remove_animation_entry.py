import bpy


def remove_entry(context: bpy.types.Context):
    anim_data = context.scene.io3d_animation_data
    anim_name = anim_data.entry[anim_data.active_entry_index].name
    anim_data.remove(anim_data.active_entry_index)
        
    return anim_name


from bpy.types import Operator


class RemoveEntry(Operator):
    """Remove an animation entry from property"""
    bl_idname = "io3d.remove_entry" 
    bl_label = "Remove animation entry"

    def execute(self, context):
        result = remove_entry(context)
        self.report({'INFO'}, f'Removed "{result}"')

        return {'FINISHED'}

def register():
    bpy.utils.register_class(RemoveEntry)

def unregister():
    bpy.utils.unregister_class(RemoveEntry)
