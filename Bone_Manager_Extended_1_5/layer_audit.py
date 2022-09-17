import bpy

from bpy.props import BoolProperty
from .blmfuncs import prefs, check_used_layer


class BLM_OT_layeraudit(bpy.types.Operator):
    # Toggle All Selected Bones Deform Property
    bl_idname = "bone_layer_man.layeraudit"
    bl_label = "Clean Layers"
    bl_description = "Reset Empty Layer Names and Non RigUI Layers"
    bl_options = {'REGISTER', 'UNDO'}

    clean_layers: bpy.props.BoolProperty(
        name="Reset Empty Layer Names",
        description="Revert unnamed layers to show 'Assign Name'",
        default=True)

    clean_ui_layers: bpy.props.BoolProperty(
        name="Reset Invalid RigUI Layer Numbers",
        description="Revert invalid RigUI layers to show 'Add RigUI Layer'",
        default=True)

    clean_unused_layers: bpy.props.BoolProperty(
        name="Reset Unused Layers",
        description="Revert unused layers to default state",
        default=True)

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None):
            return True
        for ob in context.selected_objects:
            if ob.type == 'ARMATURE':
                return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        row = layout.row()
        row.prop(self, "clean_layers", expand=True)
        row = layout.row()
        row.prop(self, "clean_ui_layers", expand=True)
        row = layout.row()
        row.prop(self, "clean_unused_layers", expand=True)

    def execute(self, context):
        obj = context.active_object
        objects = (
            # List of selected rigs, starting with the active object (if it's a rig)
            *[o for o in {obj} if o and o.type == 'ARMATURE'],
            *[o for o in context.selected_objects
              if (o != obj and o.type == 'ARMATURE')],
        )

        for ac_ob in objects:
            arm = ac_ob.data

            for i in range(len(arm.layers)):
                # layer id property
                name_id_prop = f"layer_name_{i}"
                rigui_id_prop = f"rigui_id_{i}"
                reset_rigui = arm.get(rigui_id_prop, None)
                reset_layername = arm.get(name_id_prop, None)
                is_use = check_used_layer(arm, i, context)

                if reset_rigui is not None and reset_rigui == -1 and self.clean_ui_layers:
                    del arm[rigui_id_prop]

                if reset_layername is not None and reset_layername.strip() == "" and self.clean_layers:
                    del arm[name_id_prop]

                if self.clean_unused_layers:
                    if not is_use and arm.get(name_id_prop, None) is not None:
                        del arm[name_id_prop]

                    if not is_use and arm.get(rigui_id_prop, None) is not None:
                        del arm[rigui_id_prop]
                    
                    #reset count
                    count = 0
                    for k, v in arm.items():    
                        if k.startswith("rigui_id_"):
                            if count < v:
                                count=v

                    arm['rigui_idcount'] = count

        #redraw to update panel
        for region in context.area.regions:
            if region.type == "UI":
                region.tag_redraw()

        return {'FINISHED'}
