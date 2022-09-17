import bpy

from .blmfuncs import prefs, clean_string


class BLM_PT_customproperties(bpy.types.Panel):
    # Creates a Rig Properties Panel (Pose Bone Custom Properties)
    bl_category = "Bone Layers"
    bl_label = "Rig Properties"
    bl_idname = "BLM_PT_customproperties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None):
            return True
        for ob in context.selected_objects:
            if ob.type == 'ARMATURE':
                return True

    def draw(self, context):
        layout = self.layout


class BLM_PT_customproperties_options(bpy.types.Panel):
    # Creates a Custom Properties Options Subpanel
    bl_idname = "BLM_PT_customproperties_options"
    bl_label = "Options"
    bl_parent_id = "BLM_PT_customproperties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Display", translate=False)
        row = layout.row()

        row = layout.row(align=True)
        row.prop(prefs(), "BLM_ShowPropEdit", text="Edit Mode")
        row.prop(prefs(), "BLM_ShowDeveloperUI", text="Developer Extras ")
        row = layout.row(align=True)
        row.prop(prefs(), "BLM_ShowArmatureName", text="Armature Name")
        row.prop(prefs(), "BLM_ShowBoneLabels", text="Bone Name")
        row = layout.row()
        row.scale_y = .8
        row.prop(prefs(), "BLM_CustomPropSplit", text="Property Width")

        if bpy.app.version >= (2, 92, 0):
            row = layout.row()
            row.label(text="Import/Export", translate=False)

            row = layout.row()
            row.operator("bone_layer_man.exportprops",
                        emboss=True, text="Export Custom Props")

            row.operator("bone_layer_man.importprops",
                        emboss=True, text="Import Custom Props")


class BLM_PT_customproperties_layout(bpy.types.Panel):
    # Displays a Rig Custom Properties in Subpanel
    bl_category = "Bone Layers"
    bl_label = ""
    bl_idname = "BLM_PT_customproperties_layout"
    bl_parent_id = "BLM_PT_customproperties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if context.mode == 'POSE':
            bones = context.selected_pose_bones
        else:
            obs = (
                # List of selected rigs, starting with the active object (if it's a rig)
                *[o for o in {obj} if o and o.type == 'ARMATURE'],
                *[o for o in context.selected_objects
                  if (o != obj and o.type == 'ARMATURE')],
            )
            if context.mode == 'EDIT_ARMATURE':
                bones = [
                    b
                    for o in obs
                    for b in getattr(o.pose, 'bones', [])
                    if o.data.edit_bones[f'{b.name}'].select
                ]
            else:
                bones = [
                    b
                    for o in obs
                    for b in getattr(o.pose, 'bones', [])
                    if b.bone.select
                ]

        # Store the indexes of selected objects, as a dict()
        objs = {o: i for (i, o) in enumerate(context.selected_objects)}

        showedit = prefs().BLM_ShowPropEdit
        showbone = prefs().BLM_ShowBoneLabels
        showarm = prefs().BLM_ShowArmatureName
        showrna = prefs().BLM_ShowDeveloperUI

        rna_properties = {
            prop.identifier for prop in bpy.types.PoseBone.bl_rna.properties
            if prop.is_runtime
        }

        #BLEND3.0 COMPAT
        skip_keys = rna_properties
        if bpy.app.version < (3, 0, 0):
            skip_keys = rna_properties.union({"_RNA_UI"})
        else:
            skip_keys = rna_properties.union({"constraint_active_index"})

        has_ui = False

        def assign_props(op, val, key, bone):
            if bone.id_data == obj:
                op.data_path = f'active_object.pose.bones["{bone.name}"]'
            else:
                index = objs[bone.id_data]
                op.data_path = f'selected_objects[{index}].pose.bones["{bone.name}"]'
            
            #BLEND3.0 COMPAT
            if bpy.app.version < (3, 0, 0):
                op.property = key
            else:
                op.property_name = key

            try:
                op.value = str(val)
            except:
                pass

        # Iterate through selected bones add each prop property of each bone to the panel.

        for (index, bone) in enumerate(bones):
            items = tuple((
                (k, v) for (k, v) in sorted(bone.items())
                if k not in {'_RNA_UI', 'constraint_active_index'} and ((showrna) or (k not in skip_keys))
            ))

            if (items or showedit):
                has_ui = True
                if (showarm or showbone):
                    row = layout.row(align=True)
                    row.alignment = 'LEFT'
                    if showarm:
                        row.label(text=bones[index].id_data.name, icon='ARMATURE_DATA')
                        if showbone:
                            row.label(icon='RIGHTARROW')
                    if showbone:
                        row.label(icon='BONE_DATA')
                        if showedit:
                            row.emboss = 'PULLDOWN_MENU'
                            row.prop(bone, 'name', text="")
                        else:
                            row.label(text=bone.name)

            if items:
                box = layout.box()

            for key, val in items:
                is_rna = key in rna_properties

                to_dict = getattr(val, "to_dict", None)
                to_list = getattr(val, "to_list", None)

                if to_dict:
                    val = to_dict()
                    val_draw = str(val)
                elif to_list:
                    val = to_list()
                    val_draw = str(val)
                else:
                    val_draw = val

                # explicit exception for arrays.
                show_array_ui = to_list and not is_rna and 0 < len(val) <= 4

                row = box.row(align=True)
                split = row.split(align=True, factor=prefs().BLM_CustomPropSplit)
                row = split.row(align=True)
                row.label( text= clean_string(key), translate=False)

                row = split.row(align=True)

                if show_array_ui and isinstance(val[0], (int, float)):
                    row.prop(bone, f'["{key}"]', text="")
                elif to_dict or to_list:
                    row.label(text=val_draw, translate=False)
                else:
                    if is_rna:
                        row.prop(bone, key, text="")
                    else:
                        new_b = row.operator('chui_add.user_prop', text = "", icon ='FOLDER_REDIRECT')
                        new_b.bone = bone.name
                        new_b.key = key
                        row.separator()
                        row.prop(bone, f'["{key}"]', text="", slider=True)

                if showedit:
                    if is_rna:
                        row.label(text="API Defined")
                    else:
                        split = row.split(align=True, factor=0)

                        row = split.row(align=True)
                        row.context_pointer_set('active_pose_bone', bone)
                        op = row.operator("wm.properties_edit", text="", icon='SETTINGS')
                        assign_props(op, val, key, bone)

                        row = split.row(align=False)
                        row.context_pointer_set('active_pose_bone', bone)
                        op = row.operator("wm.properties_remove", text="", icon='X')
                        assign_props(op, val, key, bone)

            if showedit:
                row = layout.row(align=True)
                row.context_pointer_set('active_pose_bone', bone)
                add = row.operator("wm.properties_add", text="Add")
                add.data_path = "active_pose_bone"

        if not bones:
            layout.label(text="No bones selected", icon='INFO')
        elif not has_ui:
            layout.label(text="No available bone properties", icon='INFO')
