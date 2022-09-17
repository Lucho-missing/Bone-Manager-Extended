import bpy

from .blmfuncs import prefs, check_used_layer, check_selected_layer


class BLM_PT_panel(bpy.types.Panel):
    bl_category = "Bone Layers"
    bl_label = "Layer Management"
    bl_idname = "BLM_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None):
            return True
        for ob in context.selected_objects:  # Check for armature in all objects (Add support for Weight Painting)
            if ob.type == 'ARMATURE':
                return True

    def draw(self, context):
        layout = self.layout


class BLM_PT_panel_options(bpy.types.Panel):
    bl_idname = "BLM_PT_panel_options"
    bl_label = "Display Options"
    # bl_parent_id = "BLM_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_ui_units_x = 7

    if bpy.app.version >= (2, 90, 0):
        bl_options = {'INSTANCED'}

    def draw(self, context):

        layout = self.layout
        layout.label(text="Visible Toggles\Tools")

        row = layout.row(align=True)
        col= row.column(align=True)
        col.prop(prefs(), "BLM_LayerIndex", text="", icon='LINENUMBERS_ON')
        col= row.column(align=True)
        col.prop(prefs(), "BLM_ShowProtected", text="", icon='LINKED')
        col= row.column(align=True)
        if context.mode == 'OBJECT':
            col.enabled = False
        col.prop(prefs(), "BLM_SelectAll", text="", icon='RESTRICT_SELECT_OFF')
        col= row.column(align=True)
        if context.mode == 'OBJECT':
            col.enabled = False
        col.prop(prefs(), "BLM_MoveTo", text="", icon='DOT')
        col= row.column(align=True)
        if context.mode != 'POSE':
            col.enabled = False
        col.prop(prefs(), "BLM_CreateGroup", text="", icon='GROUP_BONE')
        col= row.column(align=True)
        if context.mode == 'OBJECT':
            col.enabled = False
        col.prop(prefs(), "BLM_LockLayer", text="", icon='LOCKED')
        col= row.column(align=True)
        col.prop(prefs(), "BLM_ShowLayerSort", text="", icon='FILE_REFRESH')

        row = layout.row(align=True)
        layout.separator()
        row = layout.row()
        row.label(text="Layer Filters")
        row = layout.row()
        row.prop(prefs(), "BLM_LayerVisibility", text="Hide Empty")
        row = layout.row()
        row.prop(prefs(), "BLM_ShowNamed", text="Hide Nameless")
        layout.separator()
        row = layout.row()
        row.label(text="Rig UI")
        row = layout.row()
        row.prop(prefs(), "BLM_ShowRigUI", text="Show RigUI Setup")
        


class BLM_PT_panel_layer_tools(bpy.types.Panel):
    bl_idname = "BLM_PT_panel_debug"
    bl_label = "Layer Tools"
    bl_parent_id = "BLM_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout


        row = layout.row()

        row.operator("bone_layer_man.get_rigify_layers",
                     emboss=True, text="Get Rigify Layers")

        row.operator("bone_layer_man.copy_layers_names",
                     emboss=True, text="Copy Layer Names")

        row = layout.row()
        row.operator("bone_layer_man.exportlayers",
                     emboss=True, text="Export Layers")

        row.operator("bone_layer_man.importlayers",
                     emboss=True, text="Import Layers")


class BLM_PT_panel_layers(bpy.types.Panel):
    # Creates a subpanel in the scene context of the properties editor
    bl_idname = "BLM_PT_panel_layers"
    bl_label = ""
    bl_parent_id = "BLM_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        if context.active_pose_bone and context.mode in ('POSE', 'PAINT_WEIGHT'):
            is_deform = context.active_pose_bone.bone.use_deform
        else:
            is_deform = getattr(context.active_bone, 'use_deform', False)

        row = layout.row(align=True)
        row.scale_y = .9

        # row.label(text="Tom's Toggles:", translate=False) # Tom's a good guy ;)
        bsplit = row.split(factor = 0.8)
        split = bsplit.split(factor = 0.5)
        split.operator("bone_layer_man.deformtoggle", emboss=True,
                     text=f"Deform",
                     icon=('CHECKBOX_DEHLT', 'CHECKBOX_HLT')[is_deform])

        split.operator("bone_layer_man.deformerisolate",
                     emboss=True, text="Deformer Filter")

        bsplit.operator("bone_layer_man.layeraudit",
                     emboss=True, text="", icon = 'TRASH')

        bsplit.popover(
                panel="BLM_PT_panel_options",
                text="",
                icon='FILTER',
            )
        
        obj = context.active_object
        objects = (
            # List of selected rigs, starting with the active object (if it's a rig)
            *[o for o in {obj} if o and o.type == 'ARMATURE'],
            *[o for o in context.selected_objects
              if (o != obj and o.type == 'ARMATURE')],
        )
        grid = layout.column(align=True)

        row = grid.row()
        row.label(text = "   Main Layers", icon ='BONE_DATA')
        for (i_ob, ac_ob) in enumerate(objects):
            arm = ac_ob.data

            grid.context_pointer_set('active_object', ac_ob)
            col = grid.column(align=True)
            if len(objects) > 1:
                if i_ob:  # Don't use separator on the first rig
                    col.separator()
                col.label(text=ac_ob.name, icon='ARMATURE_DATA')

            for i in range(len(arm.layers)):
                if i == 16:
                    row = col.row()
                    row.label(text = "   Tweak Layers" , icon ='BONE_DATA') 
                # layer id property
                name_id_prop = f"layer_name_{i}"
                rigui_id_prop = f"rigui_id_{i}"

                # conditionals needed for interface drawing
                # layer is used
                is_use = check_used_layer(arm, i, context)

                # layer is named RigUIid given
                layer_name = None
                rigui_id = None

                try:
                    layer_name = arm[name_id_prop]
                except KeyError:
                    do_name_operator = "bone_layer_man.layout_do_name"
                try:
                    rigui_id = arm[rigui_id_prop]
                except KeyError:
                    do_id_operator = "bone_layer_man.rigui_set_id"

                # Add layer line
                if ((is_use or not prefs().BLM_LayerVisibility) and
                        (layer_name or not prefs().BLM_ShowNamed)):
                    # Group every GroupBy layers
                    if i % prefs().BLM_GroupBy == 0:
                        col.separator()

                    # Fill entries

                    # visibility, show layer index as text and set split if queried
                    
                    # if visible
                    if prefs().BLM_LayerIndex:
                        #active button count
                        active_buttons = 0
                        if context.mode == 'POSE':
                            bool_list = [prefs().BLM_ShowProtected,
                                        prefs().BLM_SelectAll,
                                        prefs().BLM_MoveTo,
                                        prefs().BLM_LockLayer,
                                        prefs().BLM_CreateGroup,
                                        prefs().BLM_ShowLayerSort,
                                        ]
                        
                        elif context.mode not in {'POSE', 'OBJECT'}:
                            bool_list = [prefs().BLM_ShowProtected,
                                        prefs().BLM_SelectAll,
                                        prefs().BLM_MoveTo,
                                        prefs().BLM_LockLayer,
                                        prefs().BLM_ShowLayerSort,
                                        ]
                        
                        else:
                            bool_list = [prefs().BLM_ShowProtected,
                                        prefs().BLM_ShowLayerSort,
                                        ]
                        
                        active_buttons = sum(bool_list)
                        

                        area = bpy.context.area
                        ui_scale = context.preferences.system.ui_scale
                        for reg in area.regions:
                            if reg.type == 'UI':
                                region_width_raw = reg.width

                        # basically madness
                        region_width = region_width_raw - 75                   
                        region_width_factor = round(region_width / 440, 3)
                        but_buffer = (active_buttons * 0.01) + (prefs().BLM_ShowRigUI * 0.05) # .01 for icon only + .05 for rigui button
                        row_scale_raw = round(0.15 * (1/region_width_factor), 3) # .15 seems to work best
                        row_scale = round(max(min(0.3 + but_buffer, row_scale_raw + but_buffer), 0.26 + but_buffer), 3)
    
                        row = col.row()
                        subrow = row.row()
                        subrow.scale_x = row_scale
                        subrow.label(text = f"{i}")
                        row = row.row(align=True)

                        row.prop(arm, "layers", index=i, emboss=True,
                                   icon=('HIDE_ON', 'HIDE_OFF')[arm.layers[i]],
                                   toggle=True,
                                   text="")

                        # name if any, else naming operator
                        if layer_name is not None:
                            row.prop(arm, f'["{name_id_prop}"]', text="")
                        else:
                            name_op = row.operator(do_name_operator)
                            name_op.layer_idx = i
                            name_op.layer_name = f"Layer {i}"
                    # else if not visible
                    else:
                        row = col.row(align=True)
                        row.prop(arm, "layers", index=i, emboss=True,
                                 icon=('HIDE_ON', 'HIDE_OFF')[arm.layers[i]],
                                 toggle=True,
                                 text="")

                        # name if any, else naming operator
                        if layer_name is not None:
                            row.prop(arm, f'["{name_id_prop}"]', text="")
                        else:
                            name_op = row.operator(do_name_operator)
                            name_op.layer_idx = i
                            name_op.layer_name = f"Layer {i}"

                    # RigUI Setup fields

                    if prefs().BLM_ShowRigUI:

                        if rigui_id is None:
                            id_mode = prefs().BLM_AddRUIMode

                            if id_mode == 'new':
                                #  Use sequential number
                                id_op = row.operator("bone_layer_man.rigui_set_id2")
                            else:
                                #  Use layer number
                                if id_mode == 'default':
                                    id_op = row.operator('bone_layer_man.rigui_set_id')
                                if id_mode == 'mix':
                                    id_op = row.operator('bone_layer_man.rigui_set_id3')
                                id_op.rigui_id = i
                            id_op.layer_idx = i
                        else:
                            if rigui_id in range(0, 32):
                                row.prop(arm, f'["{rigui_id_prop}"]', index=i, text="UI Row ")
                            else:
                                row.prop(arm, f'["{rigui_id_prop}"]', index=i, text="Non UI")

                    # assume layer was never locked if has no lock property
                    lock = arm.get(f"layer_lock_{i}", False)
             
                    # protected layer
                    if prefs().BLM_ShowProtected:
                        row.prop(arm, "layers_protected", index=i, emboss=True,
                                 icon=('UNLINKED', 'LINKED')[arm.layers_protected[i]],
                                 toggle=True, text="")

                    # Select, Lock, Group and Merge are optional
                    if context.mode != 'OBJECT':
                        # bones select
                        if prefs().BLM_SelectAll:
                            sel_op = row.operator("bone_layer_man.selectboneslayer",
                                                icon='RESTRICT_SELECT_OFF',
                                                text="", emboss=True)
                            sel_op.layer_idx = i

                           
                        if prefs().BLM_MoveTo:
                            if is_use:
                                is_use += check_selected_layer(arm, i, context)

                            merge_op = row.operator("bone_layer_man.blmergeselected",
                                                    text="", emboss=True,
                                                    icon=('RADIOBUT_OFF',
                                                        'LAYER_USED',
                                                        'LAYER_ACTIVE')[is_use])
                            merge_op.layer_idx = i

                        # groups operator **only in pose mode
                        if context.mode == 'POSE' and prefs().BLM_CreateGroup:
                            grp_op = row.operator("bone_layer_man.bonelayergroup",
                                                  text="",
                                                  emboss=True, icon='GROUP_BONE')
                            grp_op.layer_idx = i

                        # lock operator
                        if prefs().BLM_LockLayer:
                            lock_op = row.operator("bone_layer_man.bonelockselected",
                                                text="", emboss=True,
                                                icon=('UNLOCKED', 'LOCKED')[lock])

                            lock_op.layer_idx = i
                            lock_op.lock = not lock

                    def is_lock(idx):
                        # check if layer is locked (or hidden)
                        layer_lock = f"layer_lock_{idx}"
                        lock = arm.get(layer_lock, False)

                        if idx not in range(32):
                            return True
                        at_end = idx in [0, 31]

                        if not lock and not at_end:
                            is_use = check_used_layer(arm, idx, context)
                            layer_name = arm.get(f"layer_name_{idx}")

                            if not ((is_use or not prefs().BLM_LayerVisibility) and
                                    (layer_name or not prefs().BLM_ShowNamed)):
                                lock = True  # skip hidden layers
                        return lock

                    # Show Sorting functions without "ExtraOptions" enabled
                    if prefs().BLM_ShowLayerSort:

                        # Swap layers button
                        swap = row.row(align=True)
                        swap.enabled = not lock
                        swap.active = True
                        toggle_layer_1 = arm.get('BLM_TEMP_FIRST_LAYER')
                        highlight = bool(toggle_layer_1 == i)

                        if highlight:
                            icon = 'FILE_REFRESH'
                        elif toggle_layer_1:
                            icon = 'LOOP_FORWARDS'
                        else:
                            icon = 'ARROW_LEFTRIGHT'
                        op = swap.operator("bone_layer_man.bonelayerswap", depress=highlight, text="", icon=icon)
                        op.layer_idx = i

                        # Directional layer swapping
                        # swap = swap.column(align=True)
                        # swap.active = bool(toggle_layer_1 is None)

                        # target_up = (i - 1)
                        # target_down = (i + 1)

                        # while is_lock(target_up) and target_up in range(32):
                        #     target_up -= 1
                        # while is_lock(target_down) and target_down in range(32):
                        #     target_down += 1

                        # if target_up <= 0:
                        #     icon_up = 'TRIA_UP_BAR'
                        # else:
                        #     icon_up = 'TRIA_UP'

                        # if target_down >= 31:
                        #     icon_down = 'TRIA_DOWN_BAR'
                        # else:
                        #     icon_down = 'TRIA_DOWN'

                        # Disabled sorting method
                        # do_up = not is_lock(target_up)
                        # do_down = not is_lock(target_down)

                        do_up = False
                        do_down = False

                        if (do_up and do_down):
                            swap.scale_y = 0.5

                        if do_up:
                            up = swap.row()
                            op = up.operator("bone_layer_man.bonelayerswap", text="", icon=icon_up)
                            op.layer_idx = i
                            op.target_idx = target_up

                        if do_down:
                            down = swap.row()
                            op = down.operator("bone_layer_man.bonelayerswap", text="", icon=icon_down)
                            op.layer_idx = i
                            op.target_idx = target_down

