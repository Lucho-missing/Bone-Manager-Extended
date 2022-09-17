import bpy
import re


class BLNAMES_OT_get_rigify_layers(bpy.types.Operator):
    bl_idname = "bone_layer_man.get_rigify_layers"
    bl_label = "Get Rigify Metarig names"
    bl_description = "Populate Layers with Rigify Metarig layer names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return getattr(bpy.context.object.data, 'rigify_layers', None)

    def execute(self, context):
        rigify_layers = bpy.context.object.data.rigify_layers

        for i, layer in enumerate(rigify_layers):
            if layer.name != "":
                bpy.ops.bone_layer_man.layout_do_name(layer_idx=i, layer_name=layer.name)

        return {'FINISHED'}


class BLNAMES_OT_get_copy_layers_names(bpy.types.Operator):
    bl_idname = "bone_layer_man.copy_layers_names"
    bl_label = "Copy layer names"
    bl_description = "Copy layer names from selected to active"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        active = context.active_object
        # polling for only 2 armatures with 1 active
        armatures = [ob for ob in context.selected_objects if ob.type =='ARMATURE' and ob != active]
        return active.type == 'ARMATURE' and len(armatures) == 1

    def execute(self, context):

        active = context.active_object
        selected = [ob for ob in context.selected_objects if ob.type =='ARMATURE' and ob != active]
        
        for arm in selected:
            if arm != active:
                layers = [layer for layer in arm.data.keys() if layer.startswith('layer_name_')]
                for layer in layers:
                    bpy.ops.bone_layer_man.layout_do_name(layer_idx=int(re.sub('\D', '', f'{layer}')), layer_name=arm.data[layer])

        return {'FINISHED'}
