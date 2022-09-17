import bpy



from . customprop_panel import (BLM_PT_customproperties, BLM_PT_customproperties_options,
                                BLM_PT_customproperties_layout)
from . chui_data import (CHUI_user_key, CHUI_user_key_group, CHUI_bones_snappig)
from . userprop_panel import (CHUI_PT_userproperties_select, CHUI_UL_group_prop, CHUI_OT_add_user_group, CHUI_OT_add_user_prop, CHUI_OT_remove_list, CHUI_OT_group_setting, CHUI_OT_MoveItem, CHUI_PT_userproperties_preview, CHUI_OT_update_user_prop)
from . rigui_panel import BLM_PT_rigui

from . bone_layers_panel import (BLM_PT_panel, BLM_PT_panel_options, BLM_PT_panel_layers, BLM_PT_panel_layer_tools)
from . ik_snapping_utility import (CHUI_PT_snap_config, CHUI_OT_create_snap_group, CHUI_PT_snap_preview, CHUI_OT_snap_IKtoFK, CHUI_OT_remove_limb, CHUI_OT_detect_ikfk_sys, CHUI_OT_clear_fields, CHUI_OT_snap_FKtoIK, CHUI_OT_modify_limb)

from . write_ui_script import (WRITEUI_OT_writeui, CHUI_OT_bind_scritp)
from . swap_layers import BLSWAP_OT_swaplayers
from . toggle_deform_prop import BLDEF_OT_deformproptoggle
from . toggle_deform_view import BLTGGLE_OT_toggledefs
from . make_group import BLGROUP_OT_group
from . merge_layers import BLMERGE_OT_merge
from . select_layer import SELECTLAYER_OT_selectlayer
from . lock_layer import LOCKLAYER_OT_lock
from . create_rigui_id import (SETUIID_OT_riguiid, SETUIID_OT_riguiid2, SETUIID_OT_riguiid3)
from . create_layer_id import (CREATEID_OT_name, CHUI_OP_other_rigs, CHUI_OT_link_rig, CHUI_OT_to_secondary_rig, CHUI_OP_clear_data)
from . layer_audit import BLM_OT_layeraudit
from . qconstraints_panel import (QC_MT_specials, QC_MT_popup, QC_UL_conlist,
                                  QC_PT_qcontraints, QC_PT_subqcontraints,
                                  QC_PT_ConSettings,
                                  QC_PT_bArmatureConstraint_bones, QC_PT_bSplineIKConstraint_fitting, QC_PT_bSplineIKConstraint_chain_scaling,
                                  QC_PT_bTransformConstraint_from, QC_PT_bTransformConstraint_to, QC_PT_bActionConstraint_target, QC_PT_bActionConstraint_action,
                                  )

from . constraint_operators import (QC_OT_contraint_action, QC_OT_constraint_add,
                                    QC_OT_add_target, QC_OT_remove_target, QC_OT_disable_keep_transform, QC_OT_normalize_target_weights,
                                    QC_OT_copyconstraint, QC_OT_copyall, QC_OT_copyflipx,
                                    QC_OT_constraint_clear, QC_OT_autopole)

from os.path import basename, dirname
from bpy.props import BoolProperty, EnumProperty, IntProperty, FloatProperty, StringProperty, PointerProperty, CollectionProperty
from .copy_names import BLNAMES_OT_get_rigify_layers, BLNAMES_OT_get_copy_layers_names
from .io_layers import BLM_OT_exportlayers, BLM_OT_Importlayers
from .bone_layers_popup import BLM_OT_bonelayers
import rna_keymap_ui

if bpy.app.version >= (2, 92, 0):
    from .io_customprops import BLM_OT_importprops, BLM_OT_exportprops, BLM_UL_proplist, BLM_OT_proppopup


bl_info = {
    'name': 'Bone Manager Extended',
    'description': 'Bone layer names, Rig UI creation tools and more',
    'author': 'Fin, Irmitya, Mystfit, Lucho',
    'version': (1, 5, 0),
    'blender': (3, 2, 2),
    'location': 'View3D > Properties  > Bone Layers',
    'warning': '',
    'tracker_url': '',
    'category': 'Rigging'
}


class BLMpreferences(bpy.types.AddonPreferences):
    bl_idname = __name__  # basename(dirname(__file__))

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        row.prop(self, "BLM_pref_tabs", expand=True)

        row = layout.row()

        if self.BLM_pref_tabs == "general":
            self.draw_general(row)
        elif self.BLM_pref_tabs == "keymap":
            self.draw_keymap(row)
        elif self.BLM_pref_tabs == "conpresets":
            self.draw_conpresets(row)

    def draw_general(self, row):
        layout = self.layout

        col = row.column()
        col.label(text="Layer Management Defaults:")
        col.prop(self, "BLM_LayerVisibility", text="Hide Empty Layers")
        col.prop(self, "BLM_LayerIndex", text="Show Layer Index")
        col.prop(self, "BLM_ShowNamed", text="Show Named Layers Only")
        col.prop(self, "BLM_ShowRigUI", text="Show Rig UI Setup")
        col.prop(self, "BLM_ShowLayerSort", text="Enable Layer Sorting")
        col.prop(self, "BLM_GroupBy", text="Group Layers by")

        col = row.column()
        col.label(text="Custom Properties Defaults:")
        col.prop(self, "BLM_ShowPropEdit", text="Custom Properties Edit")
        col.prop(self, "BLM_ShowBoneLabels", text="Show Bone Labels")
        col.prop(self, "BLM_ShowArmatureName", text="Show Armature Name")
        col.prop(self, "BLM_ShowDeveloperUI", text="Show RNA Properties")
        col.label(text="Slider Size:")
        col.prop(self, "BLM_CustomPropSplit", text="Set Custom Properties Split")

        col = row.column()
        col.label(text="RigUI Options:")
        col.prop(self, "BLM_AddRUIMode", expand=True)
        col.separator()
        col.label(text="Popup Mode:")
        col.prop(self, "BLM_PopupMode", expand=True)

    def draw_keymap(self, row):
        layout = self.layout
        wm = bpy.context.window_manager
        row.label(text="Addon Keymaps:")
        row = layout.row()
        col = row.column()
        AddonKeymaps.draw_keymap_items(wm, col)
    
    def draw_conpresets(self, row):
        layout = self.layout
        row.label(text="Coming soon....")

    BLM_pref_tabs: EnumProperty(
        items=[
            ('general', "General", ""),
            ('keymap', "Keymap Settings", ""),
            ('conpresets', "Constraint Presets", ""),
            ],
        # name="",
        description="",
        default='general',
        )

    BLM_AddRUIMode: EnumProperty(
        items=[
            ('default', "Default", "Click to assign layer as ID number"),
            ('new', "New", "Click to assign incremental numbers as ID"),
            ('mix', "Mix", "Click to assign layer as ID number\nCtrl / Shift Click to assign in Increments"),
            ],
        # name="",
        description="Default mode for assiging Rig UI ID",
        default='new',
        )

    BLM_PopupMode: EnumProperty(
        items=[
            ('dots', "Layer Dots", ""),
            ('list', "Layer List", ""),
            ('both', "Both", ""),
            ],
        default='both',
        description="Bone Layers Popup (M) Mode",
        )

    BLM_ActiveRUILayer: IntProperty(
        name="Active Rig UI Layer",
        description="Current UI Layer to add button to",
        min=1,
        max=32,
        default=1)
   
    BLM_ShowProtected: BoolProperty(
        name="Protected Options",
        description="Show protected layer toggle",
        default=True)
    
    BLM_SelectAll: BoolProperty(
        name="Select All",
        description="Show select all toggle",
        default=True)
    
    BLM_MoveTo: BoolProperty(
        name="Move to Layer",
        description="Show move to layer option",
        default=True)
    
    BLM_LockLayer: BoolProperty(
        name="Lock Layer",
        description="Show lock layer option",
        default=True)
    
    BLM_CreateGroup: BoolProperty(
        name="Create Group",
        description="Show create group option",
        default=True)

    BLM_GroupBy: IntProperty(
        name="Group By",
        description="How many layers per group",
        min=1,
        max=32,
        default=8)
    
    BLM_ShowLayerSort: BoolProperty(
        name="Enable Layer Sorting",
        description="Show Layer Sorting Buttons",
        default=False)

    BLM_LayerVisibility: BoolProperty(
        name="Hide Empty",
        description="Hide empty layers",
        default=False)

    BLM_LayerIndex: BoolProperty(
        name="Show Index",
        description="Show layer Index",
        default=False)

    BLM_ShowArmatureName: BoolProperty(
        name="Show Armature Name",
        description="Show Armature Name",
        default=False)

    BLM_ShowBoneLabels: BoolProperty(
        name="Show Bone Labels",
        description="Show Bone Labels",
        default=False)

    BLM_ShowDeveloperUI: BoolProperty(
        name="Show All Custom Properties",
        description="Show API-Only Defined Properties.\n"
        "These properties are defined by an addon and normally can't be edited"
        " but they are still stored inside the bone's custom properties",
        default=False)

    BLM_ShowNamed: BoolProperty(
        name="Show Named",
        description="Show named layers only",
        default=False)

    BLM_ShowPropEdit: BoolProperty(
        name="Properties Edit",
        description="Edit Bone Properties",
        default=False)

    BLM_ShowRigUI: BoolProperty(
        name="RigUI Setup",
        description="Show Rig UI Setup",
        default=False)

    BLM_ShowSwap: BoolProperty(
        name="Enable UI Layer Swapping",
        description="Enable UI Swapping",
        default=False)

    BLM_ToggleView_deform: BoolProperty(
        name="Toggle Status",
        description="Isolate Deformers",
        default=False)

    BLM_ToggleView_pose: BoolProperty(
        name="Toggle Status",
        description="Isolate pose",
        default=False)

    BLM_CustomPropSplit: FloatProperty(
        name="Custom Property Panel Splt",
        description="Set Custom Properties Name\Property Ratio\n"
        "This value is also written to UI Scripts",
        min=.2,
        max=.8,
        default=.6,
        subtype="FACTOR")


class custom_prop_data(bpy.types.PropertyGroup):

    index: IntProperty(options={'HIDDEN'})

    hide_mp : BoolProperty(name ="Compress Rig Box", default= False)

    name: StringProperty(
        name="Name",
        description="Property Name",
        default="")

    prop_import: BoolProperty(
        name="prop_Import",
        description="Import Property",
        default=True)

    proptype: StringProperty(
        name="proptype",
        description="Property Name",
        default="")

    value: StringProperty(
        name="value",
        description="Property value",
        default="")

    default: StringProperty(
        name="default",
        description="Property default",
        default="")

    min: StringProperty(
        name="min",
        description="Property min",
        default="")

    max: StringProperty(
        name="max",
        description="Property max",
        default="")

    soft_min: StringProperty(
        name="soft_min",
        description="Property soft min",
        default="")

    soft_max: StringProperty(
        name="soft_max",
        description="Property soft max",
        default="")

    overridable: BoolProperty(
        name="overridable",
        description="Library overridable",
        default=True)

    description: StringProperty(
        name="description",
        description="Property description",
        default="")

    subtype: StringProperty(
        name="subtype",
        description="Property subtype",
        default="")

    array_type: StringProperty(
        name="array_type",
        description="Property array type",
        default="")


class AddonKeymaps:
    _addon_keymaps = []
    _keymaps = {}

    @classmethod
    def new_keymap(cls, name, kmi_name, kmi_value=None, km_name='3D View',
                   space_type="VIEW_3D", region_type="WINDOW",
                   event_type=None, event_value=None,
                   ctrl=False, shift=False, alt=False, key_modifier="NONE"):

        cls._keymaps.update({name: [kmi_name, kmi_value, km_name, space_type,
                                    region_type, event_type, event_value,
                                    ctrl, shift, alt, key_modifier]
                             })

    @classmethod
    def add_hotkey(cls, kc, keymap_name):

        items = cls._keymaps.get(keymap_name)
        if not items:
            return

        kmi_name, kmi_value, km_name, space_type, region_type = items[:5]
        event_type, event_value, ctrl, shift, alt, key_modifier = items[5:]
        km = kc.keymaps.new(name=km_name, space_type=space_type,
                            region_type=region_type)

        kmi = km.keymap_items.new(kmi_name, event_type, event_value,
                                  ctrl=ctrl,
                                  shift=shift, alt=alt,
                                  key_modifier=key_modifier
                                  )
        if kmi_value:
            kmi.properties.name = kmi_value

        kmi.active = True

        cls._addon_keymaps.append((km, kmi))

    @staticmethod
    def register_keymaps():
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        # In background mode, there's no such thing has keyconfigs.user,
        # because headless mode doesn't need key combos.
        # So, to avoid error message in background mode, we need to check if
        # keyconfigs is loaded.
        if not kc:
            return

        for keymap_name in AddonKeymaps._keymaps.keys():
            AddonKeymaps.add_hotkey(kc, keymap_name)

    @classmethod
    def unregister_keymaps(cls):
        kmi_values = [item[1] for item in cls._keymaps.values() if item]
        kmi_names = [item[0] for item in cls._keymaps.values() if
                     item not in ['wm.call_menu', 'wm.call_menu_pie']]

        for km, kmi in cls._addon_keymaps:
            # remove addon keymap for menu and pie menu
            if hasattr(kmi.properties, 'name'):
                if kmi_values:
                    if kmi.properties.name in kmi_values:
                        km.keymap_items.remove(kmi)

            # remove addon_keymap for operators
            else:
                if kmi_names:
                    if kmi.idname in kmi_names:
                        km.keymap_items.remove(kmi)

        cls._addon_keymaps.clear()

    @staticmethod
    def get_hotkey_entry_item(name, kc, km, kmi_name, kmi_value, col):

        # for menus and pie_menu
        if kmi_value:
            for km_item in km.keymap_items:
                if km_item.idname == kmi_name and km_item.properties.name == kmi_value:
                    col.context_pointer_set('keymap', km)
                    rna_keymap_ui.draw_kmi([], kc, km, km_item, col, 0)
                    return

            col.label(text=f"No hotkey entry found for {name}")
            col.operator(BLM_OT_restore_hotkey.bl_idname,
                         text="Restore keymap",
                         icon='ADD').km_name = km.name

        # for operators
        else:
            if km.keymap_items.get(kmi_name):
                col.context_pointer_set('keymap', km)
                rna_keymap_ui.draw_kmi([], kc, km, km.keymap_items[kmi_name],
                                       col, 0)

            else:
                col.label(text=f"No hotkey entry found for {name}")
                col.operator(BLM_OT_restore_hotkey.bl_idname,
                             text="Restore keymap",
                             icon='ADD').km_name = km.name

    @staticmethod
    def draw_keymap_items(wm, layout):
        kc = wm.keyconfigs.user

        for name, items in AddonKeymaps._keymaps.items():
            kmi_name, kmi_value, km_name = items[:3]
            box = layout.box()
            split = box.split()
            col = split.column()
            col.label(text=name)
            col.separator()
            km = kc.keymaps[km_name]
            AddonKeymaps.get_hotkey_entry_item(name, kc, km, kmi_name, kmi_value, col)


class BLM_OT_restore_hotkey(bpy.types.Operator):
    bl_idname = "copy_world_space.restore_hotkey"
    bl_label = "Restore hotkeys"
    bl_options = {'REGISTER', 'INTERNAL'}

    km_name: bpy.props.StringProperty()

    def execute(self, context):
        context.preferences.active_section = 'KEYMAP'
        wm = context.window_manager
        kc = wm.keyconfigs.addon
        km = kc.keymaps.get(self.km_name)
        if km:
            km.restore_to_default()
            context.preferences.is_dirty = True
        context.preferences.active_section = 'ADDONS'
        return {'FINISHED'}


classes = (
    BLMpreferences,
    
    
    CHUI_user_key,
    CHUI_user_key_group,
    CREATEID_OT_name,
    SETUIID_OT_riguiid, SETUIID_OT_riguiid2, SETUIID_OT_riguiid3,
    LOCKLAYER_OT_lock,
    SELECTLAYER_OT_selectlayer,
    BLMERGE_OT_merge,
    BLGROUP_OT_group,
    BLTGGLE_OT_toggledefs,
    BLDEF_OT_deformproptoggle,
    BLSWAP_OT_swaplayers,
    WRITEUI_OT_writeui,
    BLM_PT_panel,
    BLM_PT_panel_options,
    BLM_PT_panel_layers,
    BLM_PT_panel_layer_tools,      
    BLM_PT_rigui,
    BLM_PT_customproperties,
    BLM_PT_customproperties_options,
    BLM_PT_customproperties_layout,
    BLM_OT_layeraudit,
    QC_PT_qcontraints,
    QC_PT_subqcontraints,
    QC_PT_ConSettings,
    QC_UL_conlist,
    QC_OT_contraint_action,
    QC_OT_disable_keep_transform,
    QC_OT_normalize_target_weights,
    QC_OT_add_target,
    QC_OT_remove_target,
    QC_OT_constraint_add,
    QC_MT_popup,
    QC_MT_specials,
    QC_OT_copyconstraint,
    QC_OT_copyall,
    QC_OT_copyflipx,
    QC_OT_constraint_clear,
    QC_OT_autopole,
    QC_PT_bArmatureConstraint_bones,
    QC_PT_bSplineIKConstraint_fitting,
    QC_PT_bSplineIKConstraint_chain_scaling,
    QC_PT_bTransformConstraint_from,
    QC_PT_bTransformConstraint_to,
    QC_PT_bActionConstraint_target,
    QC_PT_bActionConstraint_action,
    BLNAMES_OT_get_rigify_layers,
    BLNAMES_OT_get_copy_layers_names,
    BLM_OT_exportlayers,
    BLM_OT_Importlayers,
    custom_prop_data,
    BLM_OT_bonelayers,
    BLM_OT_restore_hotkey,
    CHUI_OP_other_rigs,
    CHUI_OT_link_rig,
    CHUI_OT_to_secondary_rig,
    CHUI_OP_clear_data,
    CHUI_OT_bind_scritp,
    CHUI_UL_group_prop,
    CHUI_PT_userproperties_select,
    CHUI_OT_add_user_group,
    CHUI_OT_add_user_prop,
    CHUI_OT_remove_list,
    CHUI_OT_group_setting,
    CHUI_OT_MoveItem,
    CHUI_PT_userproperties_preview,
    CHUI_OT_update_user_prop,
    CHUI_PT_snap_config,
    CHUI_bones_snappig,
    CHUI_OT_create_snap_group,
    CHUI_PT_snap_preview,
    CHUI_OT_snap_IKtoFK,
    CHUI_OT_remove_limb,
    CHUI_OT_detect_ikfk_sys,
    CHUI_OT_clear_fields,
    CHUI_OT_snap_FKtoIK,
    CHUI_OT_modify_limb,
    

)

if bpy.app.version >= (2, 92, 0):
    custom_prop_cls = (
        BLM_OT_exportprops,
        BLM_OT_importprops,
        BLM_UL_proplist,
        BLM_OT_proppopup,
        )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    if bpy.app.version >= (2, 92, 0):
        for cls in custom_prop_cls:
            register_class(cls)
    
    bpy.types.Armature.use_frame_range = bpy.props.BoolProperty(name = "use frame range", default = False, override = {"LIBRARY_OVERRIDABLE"})
    
    
    bpy.types.Armature.userProp_group = bpy.props.CollectionProperty(type= CHUI_user_key_group)
    bpy.types.Armature.list_snap = bpy.props.CollectionProperty(type=CHUI_bones_snappig)
    bpy.types.Armature.dummy_snap = bpy.props.PointerProperty(type= CHUI_bones_snappig)
  
    bpy.types.Armature.list_index = bpy.props.IntProperty(name = "User Group)")
  


    bpy.app.handlers.load_post.append(CHUI_OP_other_rigs.reset_list)

    # bpy.types.WindowManager.prop_group = CollectionProperty(type=Entry)
    bpy.types.WindowManager.prop_data = bpy.props.CollectionProperty(type=custom_prop_data)
    bpy.types.WindowManager.prop_index = IntProperty()

    AddonKeymaps.new_keymap('Bone Layers Popup (Edit)',
                            'bonelayers.popup', None,
                            'Armature', 'EMPTY', 'WINDOW',
                            'M', 'PRESS', False, False, False, 'NONE'
                            )

    AddonKeymaps.new_keymap('Bone Layers Popup (Pose)',
                            'bonelayers.popup', None,
                            'Pose', 'EMPTY', 'WINDOW',
                            'M', 'PRESS', False, False, False, 'NONE'
                            )

    AddonKeymaps.new_keymap('Bone Layers Popup (Weight Paint)',
                            'bonelayers.popup', None,
                            'Weight Paint', 'EMPTY', 'WINDOW',
                            'M', 'PRESS', False, True, False, 'NONE'
                            )

    AddonKeymaps.new_keymap('Add Contraints Popup',
                            'wm.call_menu', 'QC_MT_popup',
                            'Pose', 'EMPTY', 'WINDOW',
                            'C', 'PRESS', True, True, False, 'NONE'
                            )

    AddonKeymaps.new_keymap('Clear All Contraints',
                            'qconstraint.constraint_clear', None,
                            'Pose', 'EMPTY', 'WINDOW',
                            'C', 'PRESS', True, False, True, 'NONE'
                            )

    AddonKeymaps.register_keymaps()


def unregister():

    AddonKeymaps.unregister_keymaps()

    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

    if bpy.app.version >= (2, 92, 0):
        for cls in custom_prop_cls:
            unregister_class(cls)

    del bpy.types.WindowManager.prop_data
    del bpy.types.WindowManager.prop_index
    del bpy.types.Armature.userProp_group
    del bpy.types.Armature.list_index


if __name__ == "__main__":
    register()
