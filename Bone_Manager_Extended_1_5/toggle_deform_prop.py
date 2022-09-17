import bpy

from bpy.props import BoolProperty
from .blmfuncs import prefs


class BLDEF_OT_deformproptoggle(bpy.types.Operator):
    # Toggle All Selected Bones Deform Property
    bl_idname = "bone_layer_man.deformtoggle"
    bl_label = "Toggle deform prop"
    bl_description = "Toggle 'Deform' property of all selected bones"

    @classmethod
    def poll(self, context):
        if context.mode == 'OBJECT':
            return False
        for ob in context.selected_objects:  # Check for armature in all objects (Add support for Weight Painting)
            if ob.type == 'ARMATURE':
                return True
        # return getattr(context.active_object, 'type', False) == 'ARMATURE'

    def execute(self, context):
        ac_ob = context.active_object
        arm = ac_ob.data

        if context.mode in ('POSE', 'PAINT_WEIGHT'):
            path_iter = 'selected_pose_bones'
            path_item = "bone.use_deform"
        
        else:
            path_iter = 'selected_bones'
            path_item = "use_deform"

        bpy.ops.wm.context_collection_boolean_set(data_path_iter=path_iter, data_path_item=path_item, type='TOGGLE')

        return {'FINISHED'}
