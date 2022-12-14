import bpy

from bpy.props import IntProperty
from rna_prop_ui import rna_idprop_ui_create

# BLEND3.0 COMPAT also works >= 2.8.0
def insert_rna_default(arm, idx, value):
    rna_idprop_ui_create(arm, 
                        f"rigui_id_{idx}", 
                        default = value,
                        min=-1, 
                        max=31, 
                        soft_min=-1, 
                        soft_max=31, 
                        description='', 
                        overridable=False)


class SETUIID_OT_riguiid(bpy.types.Operator):
    # Assign and store a layer index for this layer as ID prop
    bl_idname = "bone_layer_man.rigui_set_id"
    bl_label = "Assign RigUI Row"
    bl_description = "Assign a row index for the RigUI."
    bl_options = {'REGISTER', 'UNDO'}

    layer_idx: IntProperty(
        name="Layer Index",
        description="Index of the layer to be named",
        default=-1, min=-1, max=31,
        options = {'HIDDEN'})

    rigui_id: IntProperty(
        name="RigUI Layer",
        description="Index of the RigUI layer",
        default=-1, min=-1, max=31, soft_min=-1, soft_max=31,
        options = {'HIDDEN'})

    @classmethod
    def poll(self, context):
        arm = getattr(context.active_object, 'data', None)
        not_link = (getattr(arm, 'library', None) is None)
        return not_link

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        arm = context.active_object.data

        insert_rna_default(arm, self.layer_idx, self.rigui_id)

        return {'FINISHED'}


class SETUIID_OT_riguiid2(bpy.types.Operator):
    # Assign and store a layer index for this layer as ID prop
    bl_idname = "bone_layer_man.rigui_set_id2"
    bl_label = "Assign RigUI Row"
    bl_description = "Assign a row index for the RigUI.\nShift + Click to assign to the previous index"
    bl_options = {'REGISTER', 'UNDO'}

    layer_idx: IntProperty(
        name="Layer Index",
        description="Index of the layer to be named",
        default=-1, min=-1, max=31,
        options = {'HIDDEN'})
    
    rigui_id: IntProperty(
        name="RigUI Layer",
        description="Index of the RigUI layer",
        default=-1, min=-1, max=31, soft_min=-1, soft_max=31,
        options = {'HIDDEN'})
    
    rigui_idcount: IntProperty(
        name="RigUI Count",
        description="RigUI layer Counter",
        default=-1, min=-1, max=31, soft_min=-1, soft_max=31,
        options = {'HIDDEN'})

    @classmethod
    def poll(self, context):
        arm = getattr(context.active_object, 'data', None)
        not_link = (getattr(arm, 'library', None) is None)
        return not_link

    def invoke(self, context, event):
        arm = context.active_object.data
        count = arm.get('rigui_idcount', self.rigui_idcount)

        if not event.shift:
            count += 1
            arm['rigui_idcount'] = count

        return self.execute(context)

    def execute(self, context):
        arm = context.active_object.data
        count = arm.get('rigui_idcount', self.rigui_idcount)
        insert_rna_default(arm, self.layer_idx, count)

        return {'FINISHED'}


class SETUIID_OT_riguiid3(bpy.types.Operator):
    # Assign and store a layer index for this layer as ID prop
    bl_idname = "bone_layer_man.rigui_set_id3"
    bl_label = "Assign RigUI Row"
    bl_description = (
        "Assign a row index for the RigUI.\n"
        "Shift + Click to assign to the previous index.\n"
        "Ctrl + Click to assign one value higher than the previous index"
        )
    bl_options = {'REGISTER', 'UNDO'}

    layer_idx: IntProperty(
        name="Layer Index",
        description="Index of the layer to be named",
        default=-1, min=-1, max=31,
        options = {'HIDDEN'})

    rigui_id: IntProperty(
        name="RigUI Layer",
        description="Index of the RigUI layer",
        default=-1, min=-1, max=31, soft_min=-1, soft_max=31)

    rigui_idcount: IntProperty(
        name="RigUI Count",
        description="RigUI layer Counter",
        default=-1, min=-1, max=31, soft_min=-1, soft_max=31,
        options = {'HIDDEN'})

    @classmethod
    def poll(self, context):
        arm = getattr(context.active_object, 'data', None)
        not_link = (getattr(arm, 'library', None) is None)
        return not_link

    def invoke(self, context, event):
        arm = context.active_object.data
        count = arm.get('rigui_idcount', self.rigui_idcount)

        if event.ctrl:
            # Increment rigui_id
            count += 1
            arm['rigui_idcount'] = count
        elif event.shift:
            # Use same rigui_id
            pass
        else:
            arm['rigui_idcount'] = self.rigui_id

        return self.execute(context)

    def execute(self, context):
        arm = context.active_object.data
        count = arm.get('rigui_idcount', self.rigui_idcount)
        insert_rna_default(arm, self.layer_idx, count)

        return {'FINISHED'}
