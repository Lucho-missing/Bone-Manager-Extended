import bpy

from .blmfuncs import prefs, check_used_layer, check_selected_layer
import re


def get_icon(arm, layer_idx, used, default):
    # Check whether the given layer is used and visible
    if arm.layers[layer_idx] and used:
        return 'LAYER_ACTIVE'

    elif used:
        return'LAYER_USED'

    else:
        return default


class BLM_OT_bonelayers(bpy.types.Operator):
    bl_idname = "bonelayers.popup"
    bl_label = "Move to Layer"
    bl_options = {'REGISTER'}
    bl_property = "filter"

    show_all: bpy.props.BoolProperty(
        name="Show Unused Layers",
        description="Show Unused Layers",
        default=False)

    filter: bpy.props.StringProperty(
        description="Filter",
        default="",
        options={'TEXTEDIT_UPDATE'})

    def __init__(self):
        self.filter = ''

    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw_dots(self, context, arm, row, range):
        for i in range:
            is_use = check_used_layer(arm, i, context)
            if is_use:
                is_use += check_selected_layer(arm, i, context)
            merge_op = row.operator("bone_layer_man.blmergeselected",
                                    text="",
                                    icon=('BLANK1',
                                          'LAYER_USED',
                                          'LAYER_ACTIVE')[is_use],
                                    depress=arm.layers[i],
                                    )

            merge_op.layer_idx = i

    def draw(self, context):

        mode = prefs().BLM_PopupMode

        layout = self.layout
        layout.label(text="Move to Layer")

        obj = context.active_object

        objects = (
            # List of selected rigs, starting with the active object (if it's a rig)
            *[o for o in {obj} if o and o.type == 'ARMATURE'],
            *[o for o in context.selected_objects
              if (o != obj and o.type == 'ARMATURE')],
        )

        for (i_ob, ac_ob) in enumerate(objects):

            arm = ac_ob.data

            if mode in {'dots', 'both'}:
                row_ = layout.row(align=True)
                split = row_.split(factor=0.5)
                col = split.column(align=True)

                row = col.row(align=True)
                BLM_OT_bonelayers.draw_dots(self, context, arm, row, range(0, 8))
                row = col.row(align=True)
                BLM_OT_bonelayers.draw_dots(self, context, arm, row, range(16, 24))

                col = split.column(align=True)

                row = col.row(align=True)
                BLM_OT_bonelayers.draw_dots(self, context, arm, row, range(8, 16))
                row = col.row(align=True)
                BLM_OT_bonelayers.draw_dots(self, context, arm, row, range(24, 32))

            if mode in {'list', 'both'}:

                row_ = layout.row(align=True)
                row_.prop(self, 'filter', text="", icon='VIEWZOOM')

                row_ = layout.row(align=True)
                row_.emboss = 'PULLDOWN_MENU'
                if self.show_all:
                    text = 'Hide Unused Layers'

                else:
                    text = 'Show Unused Layers'

                row_.prop(self, 'show_all', text=text)
                row_ = layout.row(align=True)
                col = row_.column(align=True)
                col.scale_y = .8

                for i in range(len(arm.layers)):

                    is_use = check_used_layer(arm, i, context)

                    name_id_prop = f"layer_name_{i}"

                    if is_use:
                        is_use += check_selected_layer(arm, i, context)
                        # layer id property

                        if name_id_prop in arm:
                            text = f'{arm[name_id_prop]}'

                        else:
                            text = f'[UNNAMED]'

                    elif not is_use and name_id_prop in arm:
                        text = f'{arm[name_id_prop]}'

                    else:
                        text = f'[EMPTY]'

                    if self.filter != '' and not re.search(self.filter, text, re.IGNORECASE):
                        continue

                    if is_use or self.show_all:
                        split = col.split(factor=0.07, align=True)
                        split.label(text=f"{i}")
                        split = split.row(align=True)
                        row = split.split(factor=0.9, align=True)

                        if text == '':
                            row.prop(arm, f'["{name_id_prop}"]', text="",)

                        else:
                            row.label(text=text)

                        if text in {'[EMPTY]', '[UNNAMED]'}:
                            row = split.split(factor=.35, align=True)
                            do_name_operator = row.operator("bone_layer_man.layout_do_name", text='', icon='ADD', emboss=False)
                            do_name_operator.layer_idx = i
                            do_name_operator.layer_name = ''

                        else:
                            row = split.split(factor=0.5, align=True)

                        row.alignment = 'LEFT'
                        merge_op = row.operator("bone_layer_man.blmergeselected",
                                                emboss=False,
                                                text="",
                                                icon=('RADIOBUT_OFF',
                                                      'LAYER_USED',
                                                      'LAYER_ACTIVE')[is_use],
                                                )

                        merge_op.layer_idx = i
                        row.prop(arm, "layers", index=i, emboss=False,
                                 icon=('HIDE_ON', 'HIDE_OFF')[arm.layers[i]],
                                 toggle=True,
                                 text=""
                                 )

                    if 0 < i < 31 and (i + 1) % 8 == 0 and self.show_all and self.filter == '':
                        row = col.row()
                        row.separator(factor=2.5)