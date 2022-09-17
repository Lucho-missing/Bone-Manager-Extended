from ctypes import alignment
import bpy
import random
import string
from bpy.props import StringProperty, EnumProperty, BoolProperty

from .create_layer_id import CHUI_OP_other_rigs
from .blmfuncs import ShowMessageBox, string_name
from bpy_extras.io_utils import ExportHelper
import os


class WRITEUI_OT_writeui(bpy.types.Operator, ExportHelper):
    # Create Rig UI script file from current layout
    bl_idname = "bone_layer_man.write_rig_ui"
    bl_label = "Export UI"
    bl_description = "Export Rig UI script from current layout"

    filename_ext = ".py"

    script_name = ""
    

    rig_linked = []

    filter_glob: StringProperty(
        default="*.py",
        options={'HIDDEN'},
        )

    blm_rig_id: StringProperty(name="BLM Rig ID",
                               description="Rig ID Used by Bone Layer Manager",
                               default="")

    rig_ui_pname: StringProperty(name="Bone Layers",
                                 description="Bone Layers panel header name",
                                 default="Bone Layers")

    rig_cp_pname: StringProperty(name="Bones Properties Panel",
                                 description="Bones Properties panel header name",
                                 default="Bones Properties")

    use_item_panel: BoolProperty(
        name="Add to 'Item' tab",
        description="Add to 'Item' tab or create dedicated 'Rig UI' tab",
        default=True,
        )
    
    create_prop_panel: BoolProperty(
        name="Create 'Rig Properties' panel",
        description="Create 'Rig Properties' panel or use Blender default",
        default=True,
        )

    rig_tweak: BoolProperty(
        name="Secondary Rigs to Main/Tweak",
        description="Place Secondary Rigs in Tweak or Main Bone Layer",
        default=True,
        )

    snap_place: BoolProperty(
        name="Place Snapping Buttons",
        description="Send Snapping Buttons to User Properties (alwais visible), or just to Bone Properties (only visible if the interested bones are selected)",
        default=False,
        )


    @classmethod
    def poll(self, context):
        return getattr(context.active_object, 'type', False) == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        grid = layout.column()
        row = grid.row()
        row.label(text="Rig Panel Options")
        row = layout.row()
        row.prop(self, "use_item_panel")
        row = layout.row()
        row.prop(self, "create_prop_panel")
        row = layout.row()
        row.label(text="Rig UI panel name")
        row.prop(self, "rig_ui_pname", text='')
        row = layout.row()
        row.label(text="Rig Properties panel name")
        row.prop(self, "rig_cp_pname", text='')

        use_tweak = False
        for nam in CHUI_OP_other_rigs.rig:
            if context.active_object.data.get(f'CHUI_L_{nam}') != None:
                use_tweak = True
                break

        grid = layout.column()
        grid.separator(factor = 2)
        row = grid.row()

        if use_tweak == True:
            row.label(text = 'Place Secondary Rig ')
            grid.separator(factor = 2)
            row = grid.row(align=True)
            row.prop(self, 'rig_tweak', text ="", toggle = True)
            # row.scale_x = 2
            if self.rig_tweak == True:
                row.label(text = 'Tweak Layers')
            else:
                row.label(text = 'Main Layers ')
            

        if len(context.active_object.data.list_snap) > 0:
            grid.separator(factor = 2)
            row = grid.row()
            row.label(text = 'Place Sanpping Buttons ')
            grid.separator(factor = 2)
            row = grid.row(align=True)
            row.prop(self, 'snap_place', text ="", toggle = True)
            # row.scale_x = 2
            if self.snap_place == True:
                row.label(text = 'Also User Properties')
            else:
                row.label(text = 'Only Bone Properties')
            

    def invoke(self, context, event):
        self.filepath = os.path.splitext(bpy.data.filepath)[0] + "_rigui.py"

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        
        file_write = open(self.filepath, 'w').write
        ac_ob = context.active_object
        scn = context.scene
        layout = self.layout
        blockstart = True
        endblock = False
        layer_ui = [None]

        if self.use_item_panel:
            panel_loc = 'Item'
        else:
            panel_loc = 'Rig UI'

        rig_ui_pname = self.rig_ui_pname

        rig_cp_pname = self.rig_cp_pname


        # generate random id for rig
        new_rig_id = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(12)])

        # Check for Rig ID and assign if not present
        set_rig_id = ac_ob.data.get('blm_rig_id', new_rig_id)
        ac_ob.data['blm_rig_id'] = set_rig_id
        
        self.rig_linked.clear()
        for nam in CHUI_OP_other_rigs.rig:
            if bpy.data.objects[nam] != ac_ob and ac_ob.data.get(f'CHUI_L_{nam}') != None: 
                for scen in bpy.data.objects[nam].users_scene:
                    if scen == context.scene:
                        self.rig_linked.append(nam)
                        break

        # Write Secondary Rigs
        def write_sec_rigs(self, context):
            
            file_write('\n' '\t''\t''col = layout.column(align = True)''\n'
                        '\t''\t''row = col.row(align = True)''\n')
            to_head = False                
            for nam in self.rig_linked:
                # ac_ob.data[f'dCH_{nam}'] = bpy.data.objects[nam]
                file_write(
                        '\t''\t'f'cell = row.column (align = True)''\n'
                        '\t''\t''try:''\n'
                        '\t''\t''\t'f'op = cell.operator(\"chui.to_secondary_rig_{set_rig_id}\", text = clean_string(bpy.context.active_object.data["dCH_{nam}"].name), depress = not bpy.context.active_object.data["dCH_{nam}"].hide_viewport)''\n'
                        '\t''\t''\t'f"op.rig_name = bpy.context.active_object.data['dCH_{nam}'].name"'\n'
                        '\t''\t''except (KeyError, AttributeError):''\n'
                        '\t''\t''\t''pass''\n'
                )
                
                if to_head == True:
                    file_write('\t''\t''row = col.row(align = True)''\n')
                to_head = not to_head
                        
                
                

#-------------------------------- HEADER -----------------------------------------------------

        file_write(f'#{set_rig_id}''\n'
                    '### Charater UI ###''\n'
                   '\n'
                   'import bpy''\n'
                   'from bpy.props import BoolProperty, IntProperty, StringProperty''\n'
                   'from mathutils import Matrix'
                   '\n'
                   f'blm_rig_id = "{set_rig_id}"\n'
                   'chui_limbs = []''\n''\n'

                 
                )   
        for limb in context.active_object.data.list_snap:
            file_write(
                    
                    f"{string_name(limb.limb_name)} =" "{"'\n'
                        f"'limb_name' : '{limb.limb_name}',"'\n'
                        f"'FK_ctrl_first' : '{limb.FK_ctrl_first}',"'\n'
                        f"'IK_ctrl_first' : '{limb.IK_ctrl_first}',"'\n'
                        f"'FK_ctrl_second' : '{limb.FK_ctrl_second}',"'\n'
                        f"'IK_ctrl_second' : '{limb.IK_ctrl_second}',"'\n'
                        f"'FK_ctrl_third' : '{limb.FK_ctrl_third}',"'\n'
                        f"'IK_ctrl_third' : '{limb.IK_ctrl_third}',"'\n'
                        f"'IK_controller' : '{limb.IK_controller}',"'\n'
                        f"'IK_pole' : '{limb.IK_pole}'"'\n'  
                        "}"'\n''\n'
                    )
        for ind in range(len(context.active_object.data.list_snap)):
            file_write(
                    f'chui_limbs.append({string_name(context.active_object.data.list_snap[ind].limb_name)})''\n'
            )
        file_write(
                   '\n'
                   '\n' 'def clean_string(value):'
                   '\n''\t' 'val = value.replace(".", " ")'
                   '\n''\t' 'val = val.replace("_", " ")'
                    '\n''\t''val = val.title()'
                   '\n''\t' 'return val'
                   '\n'
                    '\n' 'def bones_props(bones, layout, header):'
                    '\n'
                    '\t'"rna_properties = {"'\n'
                    '\t''\t'"prop.identifier for prop in bpy.types.PoseBone.bl_rna.properties"'\n'
                    '\t''\t'"if prop.is_runtime"'\n'
                    '\t'"}"'\n'
                    '\n'
                    
                    '\t'"for bone in bones:"'\n' 
                    '\t''\t'"skip=0"'\n'
                    '\t''\t'"for key in sorted(bone.keys()):"'\n'
                    '\t''\t''\t'"if key in rna_properties:"'\n'
                    '\t''\t''\t''\t'"skip+=1"'\n'

                    '\t''\t'"if len(bone.keys()) > skip:"'\n'
                    '\t''\t''\t'"box = layout.box()"'\n'
                    '\t''\t'"for key in sorted(bone.keys()):"'\n'
                    '\t''\t''\t'"if key not in rna_properties:"'\n'
                    '\t''\t''\t''\t'"val = bone.get(key, \"value\")"'\n'
                    '\t''\t''\t''\t'"row = box.row()"'\n'
                    '\t''\t''\t''\t'"split = row.split(align=True, factor=0.7)"'\n'
                    '\t''\t''\t''\t'"row = split.row(align=True)"'\n'
                    '\t''\t''\t''\t'"row.label(text=clean_string(key), translate=False)"'\n'
                    '\t''\t''\t''\t'"row = split.row(align=True)"'\n'
                    '\t''\t''\t''\t'"row.prop(bone, f'[\"{key}\"]', text = \"\", slider=True)"'\n'
                    '\n')

#------------------------------ USER PROPERTIES -------------------------------------------------

        if len(context.active_object.data.userProp_group) > 0 or self.snap_place == True:
            file_write(
                    '\n'
                    f"class CHUI_PT_userproperties_{set_rig_id}(bpy.types.Panel):"'\n'
                    '\t'"bl_space_type = 'VIEW_3D'"'\n'
                    '\t'"bl_region_type = 'UI'"'\n'
                    '\t'"bl_category = 'Item'"'\n'
                    '\t'"bl_label = 'Relevant Properties'"'\n'
                    '\t'f"bl_idname = 'CHUI_PT_userproperties_{set_rig_id}'"'\n'
                    '\n'
                    '\t'"@classmethod"'\n'
                    '\t'"def poll(self, context):"'\n'
                    '\t''\t'"try:"'\n'
                    '\t''\t''\t'"return (context.active_object.data.get('blm_rig_id') == blm_rig_id)"'\n'
                    '\t''\t'"except (AttributeError, KeyError, TypeError):"'\n'
                    '\t''\t''\t'"return False"'\n'

                    '\t'"def draw(self, context):"'\n'
                    '\t''\t'"layout = self.layout"'\n'
                    )

            if len(context.active_object.data.list_snap) > 0 and self.snap_place == True:
                file_write(                    
                    '\t''\t'"tab = layout.row(align=False)"'\n'
                    '\t''\t'f"tab.label(text = 'Snap IK/FK', icon = 'SNAP_ON')"'\n'
                    '\t''\t'"box = layout.box()"'\n'
                    '\t''\t'"grid = box.column(align = True)"'\n'
                    '\t''\t'"row = grid.row()"'\n'

                    '\t''\t'"col = row.column()"'\n'
                    '\t''\t'"col.label(text = 'Current Frame')"'\n'
                    '\t''\t'"if context.scene.chui_bake_range == True:"'\n'
                    '\t''\t''\t'"col.active = False"'\n'
                    '\t''\t'"col.scale_x = 0.5"'\n'
                    '\t''\t'"col = row.column()"'\n'
                    '\t''\t'"col.prop(context.scene, 'chui_bake_range', text = '', toggle = True)"'\n'
                    # '\t''\t'"col.scale_x = 0.5"'\n'
                    '\t''\t'"col = row.column()"'\n'
                    '\t''\t'"col.label(text = ' Bake in Scene Frame Range')"'\n'
                    '\t''\t'"if context.scene.chui_bake_range == False:"'\n'
                    '\t''\t''\t'"col.active = False"'\n'
                    '\t''\t'"grid.separator()"'\n'
                    '\t''\t'"row=grid.row()"'\n'
                    '\t''\t'"row.label(text='FK to IK')"'\n'
                    '\t''\t'"row.label(text='IK to FK')"'\n'
                )
                for ind in range(len(context.active_object.data.list_snap)):
                    file_write(
                        '\t''\t'"row=grid.row()"'\n'
                        '\t''\t'f"fk=row.operator('chui_snap.fktoik_{set_rig_id}', text = '{context.active_object.data.list_snap[ind].limb_name}', icon ='SEQUENCE_COLOR_04')"'\n'
                        '\t''\t'f"fk.limb_index = {ind}"'\n'

                        '\t''\t'f"ik=row.operator('chui_snap.iktofk_{set_rig_id}', text = '{context.active_object.data.list_snap[ind].limb_name}', icon ='SEQUENCE_COLOR_01')"'\n'
                        '\t''\t'f"ik.limb_index = {ind}"'\n'
                    )


            groups = context.active_object.data.userProp_group
            for group in groups:
                if group.show_header == True:
                    file_write(
                    '\t''\t'"tab = layout.row(align=False)"'\n'
                    '\t''\t'f"tab.label(text = '{group.group_name}', icon = '{group.icon}')"'\n')
                file_write(
                    '\t''\t'"tab = layout.row()"'\n' 
                    '\t''\t'"box = tab.box()"'\n' )
                if group.compact_ui == True: 
                    file_write('\t''\t'"box.scale_y = 0.8"'\n')
                file_write('\t''\t'"grid = box.column()"'\n')
                for key in group.keys:   
                    file_write(
                    '\t''\t'"row=grid.row()"'\n'
                    '\t''\t'f"row.label (text=clean_string('{key.key}'))"'\n'
                    '\t''\t'"row.separator()"'\n'
                    '\t''\t'f"row.prop(context.active_object.pose.bones['{key.bone}'], '[\"{key.key}\"]', text ='', slider = True)"'\n'
                    )

#--------------------------------- RIG UI ------------------------------------------------

        file_write(f'class BLOP_PT_rigui_{set_rig_id}(bpy.types.Panel):''\n'
                   '\t'"bl_space_type = 'VIEW_3D'"'\n'
                   '\t'"bl_region_type = 'UI'"'\n'
                   '\t'f"bl_category = '{panel_loc}'"'\n'
                   '\t'f"bl_label = \"{rig_ui_pname}\""'\n'
                   '\t'f"bl_idname = \"BLOP_PT_rigui_{set_rig_id}\""'\n''\n'
                   '\t''@classmethod''\n'
                   '\t''def poll(self, context):''\n'
                   '\t''\t''try:''\n'
                   '\t''\t''\t''return (context.active_object.data.get(\"blm_rig_id\") == blm_rig_id)''\n'
                   '\t''\t''except (AttributeError, KeyError, TypeError):''\n'
                   '\t''\t''\t'"return False"'\n''\n'
                   '\n')

        for nam in self.rig_linked:
            file_write('\t'f"bpy.context.active_object.data['dCH_{nam}'] = bpy.data.objects['{nam}']"'\n')

        file_write(
                   '\n'
                   '\t''def draw(self, context):''\n'
                   '\t''\t''layout = self.layout''\n'
                   '\t''\t''col = layout.column(align=True)''\n'
                   '\n'

                    '\t''\t''row = col.row(align=False)''\n'
                    '\t''\t''row.alignment = \"CENTER\"''\n'
		            '\t''\t''row .label(text = clean_string(context.active_object.name), icon = \"ARMATURE_DATA\")''\n'
		            '\t''\t'f"row.operator('chui.all_layers_{set_rig_id}')"'\n'
                    '\t''\t'f"op = row.operator('chui.active_layer_{set_rig_id}')"'\n'
                    '\t''\t''op.from_button = True''\n'
		            '\t''\t''col.separator()''\n')

                    
        ##############################

        # Iterate through layers writing rows for the Rig UI
        layer_ui.clear()
        for x in range(33):
            blockstart = True

            for i in range(16):
                name_id_prop = f"layer_name_{i}"
                rigui_id_prop = f"rigui_id_{i}"
                name = ac_ob.data.get(name_id_prop, "*NO NAME*")
                uselayer = ac_ob.data.get(rigui_id_prop, -1)

                # Set start of UI row
                if uselayer == x and endblock is False:
                    if blockstart is True:
                        file_write('\n')
                        file_write('\t''\t'"row = col.row(align=True)"'\n')
                        blockstart = False

                    while uselayer < (x + 1):
                        if uselayer == (x + 1):
                            continue
                        file_write('\t''\t'f"row.prop(context.active_object.data,'layers', index={i}, toggle=True, text='{name}')"'\n')
                        layer_ui.append(i)
                        
                        uselayer += 1
                    # Mark end of current row in iteration
                    if i == 16:
                        endblock = True
            
        ### SEC RIG -MAIN -  WRITE:
        if self.rig_tweak == False:
            write_sec_rigs(self, context)
        
#---------------- TWEAK LAYERS  WRITE:---------------------------------------------
        
        layer_lenght =  len(layer_ui)
        use_tweak = True
        file_write(
            '\n'
            '\n'
            f"class CHUI_PT_tweaks_layers_{set_rig_id}(bpy.types.Panel):"'\n'
            '\t'f"bl_idname = \"CHUI_PT_tweaks_layers_{set_rig_id}\""'\n'
            '\t'"bl_label = \"Tweaks Layers\""'\n'
            '\t'f"bl_parent_id = \"BLOP_PT_rigui_{set_rig_id}\""'\n'
            '\t'"bl_space_type = 'VIEW_3D'"'\n'
            '\t'"bl_region_type = 'UI'"'\n'
            '\t'"bl_options = {'DEFAULT_CLOSED'}"'\n'
            '\n'
            '\t'"def draw(self, context):"'\n'
            '\t''\t'"layout = self.layout"'\n'
            '\t''\t'"col = layout.column(align=True)"'\n')
        
        for x in range(33):
            blockstart = True
            for i in range(16, 32):
                name_id_prop = f"layer_name_{i}"
                rigui_id_prop = f"rigui_id_{i}"
                name = ac_ob.data.get(name_id_prop, "*NO NAME*")
                uselayer = ac_ob.data.get(rigui_id_prop, -1)

                # Set start of UI row
                if uselayer == x and endblock is False:
                    if blockstart is True:
                        file_write('\n')
                        file_write('\t''\t'"row = col.row(align=True)"'\n')
                        blockstart = False

                    while uselayer < (x + 1):
                        if uselayer == (x + 1):
                            continue
                        file_write('\t''\t'f"row.prop(context.active_object.data,'layers', index={i}, toggle=True, text='{name}')"'\n')
                        layer_ui.append(i)
                        
                        uselayer += 1
                    # Mark end of current row in iteration
                    if i == 33:
                        endblock = True
        if layer_lenght ==  len(layer_ui):
            use_tweak = False
        
        ### SEC RIG -TWEAK -  WRITE:
        if self.rig_tweak == True:
            write_sec_rigs(self, context)

 #----------------- CUSTOM PROP ----------------------------------------

        if self.create_prop_panel:
            file_write(
                '\n'
                '\n'f"class BLOP_PT_customprops_{set_rig_id}(bpy.types.Panel):"'\n'
                '\t'f"bl_category = '{panel_loc}'"'\n'
                '\t'f"bl_label = \"{rig_cp_pname}\""'\n'
                '\t'f"bl_idname = \"BLOP_PT_customprops_{set_rig_id}\""'\n'
                '\t'"bl_space_type = 'VIEW_3D'"'\n'
                '\t'"bl_region_type = 'UI'"'\n'
                '\t'"bl_options = {'DEFAULT_CLOSED'}"'\n'
                '\n'
                '\t''@classmethod''\n'
                '\t''def poll(self, context):''\n'
                '\t''\t''try:''\n'
                '\t''\t''\t''return (context.active_object.data.get(\"blm_rig_id\") == blm_rig_id)''\n'
                '\t''\t''except (AttributeError, KeyError, TypeError):''\n'
                '\t''\t''\t'"return False"'\n'
                '\n'
                '\t''def draw(self, context):''\n'
                '\t''\t''layout = self.layout''\n'
                '\t''\t''col = layout.column(align=True)''\n'
                
                '\n'
                '\t'"def draw(self, context):"'\n'
                '\t''\t'"layout = self.layout"'\n'
                '\t''\t'"pose_bones = context.active_object.pose.bones"'\n'
                '\t''\t'"if context.selected_pose_bones:"'\n'
                '\t''\t''\t'"bones = context.selected_pose_bones"'\n'
                '\n'
                '\t''\t'"elif context.selected_editable_bones:"'\n'
                '\t''\t''\t'"bones = [pose_bones[bone.name] for bone in context.selected_editable_bones]"'\n'
                '\n'
                '\t''\t'"else:"'\n'
                '\t''\t''\t'"bones = []"'\n'
                '\n'
                
                '\t''\t'"bones_props(bones, layout, False)"'\n'
                )

  

            for ind in range(len(context.active_object.data.list_snap)):

                file_write(
                    '\n'
                    '\t''\t'f"if context.active_object.pose.bones[chui_limbs[{ind}]['FK_ctrl_first']] in bones or context.active_object.pose.bones[chui_limbs[{ind}]['IK_ctrl_first']] in bones or context.active_object.pose.bones[chui_limbs[{ind}]['FK_ctrl_second']] in bones or context.active_object.pose.bones[chui_limbs[{ind}]['IK_ctrl_second']] in bones or context.active_object.pose.bones[chui_limbs[{ind}]['FK_ctrl_third']] in bones or context.active_object.pose.bones[chui_limbs[{ind}]['IK_ctrl_third']] in bones or context.active_object.pose.bones[chui_limbs[{ind}]['IK_controller']] in bones or context.active_object.pose.bones[chui_limbs[{ind}]['IK_pole']] in bones: "'\n' 
                    '\t''\t''\t'"row = layout.row()"'\n'
                    '\t''\t''\t'"row.alignment = 'LEFT'"'\n'
                    '\t''\t''\t'f"row.label(text='{context.active_object.data.list_snap[ind].limb_name}', icon = 'SNAP_ON')"'\n'
                    '\t''\t''\t'"row.prop(context.scene, 'chui_bake_range', text = '', toggle = True)"'\n'
                    # '\t''\t''\t'"row.scale_x = 0.5"'\n'
                    '\t''\t''\t'"if context.scene.chui_bake_range== True:"'\n'
                    '\t''\t''\t''\t'"row.label(text='Bake in Scene Frame Range')"'\n'
                    '\t''\t''\t'"else:"'\n'
                    '\t''\t''\t''\t'"row.label(text='Current Frame')"'\n'
                    '\t''\t''\t'"row = layout.row()"'\n'
                    '\t''\t''\t'f"fk = row.operator ('chui_snap.fktoik_{set_rig_id}', text = 'Snap FK to IK', icon = 'SEQUENCE_COLOR_04')"'\n'
                    '\t''\t''\t'f"fk.limb_index = {ind}"'\n'
                    '\t''\t''\t'f"ik = row.operator ('chui_snap.iktofk_{set_rig_id}', text = 'Snap IK to FK', icon = 'SEQUENCE_COLOR_01')"'\n'
                    '\t''\t''\t'f"ik.limb_index = {ind}"'\n'
                        

                )


#------------------------ LAYERS OPERATORS WRITE:-----------------------------------
        
        #all ON
        file_write(
                '\n'
                '\n'f"class CHUI_OT_all_layers_{set_rig_id}(bpy.types.Operator):"'\n'
                '\t'f"bl_label = \"All ON\""'\n'
                '\t'f"bl_idname = \"chui.all_layers_{set_rig_id}\""'\n'
                '\t'"bl_description = \"Make All Bone Layers Visible\""'\n'
                '\t'"bl_options = {\"REGISTER\", \"UNDO\"}"'\n'
                '\n'
                '\t''@classmethod''\n'
                '\t''def poll(self, context):''\n'
                '\t''\t''try:''\n'
                '\t''\t''\t''return (context.active_object.data.get(\"blm_rig_id\") == blm_rig_id)''\n'
                '\t''\t''except (AttributeError, KeyError, TypeError):''\n'
                '\t''\t''\t'"return False"'\n'
                '\n'
                '\t''layer_ui = (')
                ### write used layers
        for i in layer_ui:
            file_write(f"{i}, ")
        
        #active ON
        file_write(
                ')''\n'
                '\n'
                '\t'"def execute(self, context):"'\n'
                '\t''\t'"for i in self.layer_ui:"'\n'
			    '\t''\t''\t'"context.active_object.data.layers[i] = True"'\n'
		        '\t''\t'"return {'FINISHED'}"'\n')

        file_write(
                '\n'
                '\n'f"class CHUI_OT_active_layer_{set_rig_id}(bpy.types.Operator):"'\n'
                '\t'f"bl_label = \"Only Active\""'\n'
                '\t'f"bl_idname = \"chui.active_layer_{set_rig_id}\""'\n'
                '\t'"bl_description = \"Make Visibile Only Layer(s) from active bone\""'\n'
                '\t'"bl_options = {\"REGISTER\", \"UNDO\"}"'\n'
                '\n'
                '\t''@classmethod''\n'
                '\t''def poll(self, context):''\n'
                '\t''\t''try:''\n'
                '\t''\t''\t''return (context.active_object.data.get(\"blm_rig_id\") == blm_rig_id)''\n'
                '\t''\t''except (AttributeError, KeyError, TypeError):''\n'
                '\t''\t''\t'"return False"'\n'
                '\n'
                '\t''layer_ui = (')
                ### write used layers
        for i in layer_ui:
            file_write(f"{i}, ")
        file_write(
                ')''\n'
                '\n'
                '\t'"from_button : BoolProperty(name=\"Switch To\", default = False)"'\n'
                '\t'"switch : IntProperty(name=\"Switch to Layer\", default = 0, min = 0, max = 31 )"'\n'
                '\t'"def draw(self, context):"'\n'
                '\t''\t'"self.from_button = False"'\n'
                '\t''\t'"layout = self.layout"'\n'
                '\t''\t'"row = layout.column()"'\n'
                '\t''\t'"row.prop(self, 'switch', expand = True)"'\n'
                '\n'


                '\t'"def execute(self, context):"'\n'
                '\t''\t'"if self.from_button == True:"'\n'
                '\t''\t''\t'"context.active_object.data.layers[28] = True"'\n'
                '\t''\t''\t'"for layer in self.layer_ui:"'\n'
                '\t''\t''\t''\t'"if context.active_object.data.bones.active.layers[layer] == False:"'\n'
                '\t''\t''\t''\t''\t'"context.active_object.data.layers[layer] = False"'\n'
                '\t''\t''\t''\t'"else:"'\n'
                '\t''\t''\t''\t''\t'"self.switch = layer"'\n'
                '\t''\t''\t'"context.active_object.data.layers[28] = False"'\n'
                
                '\t''\t'"else:"'\n'
                '\t''\t''\t'"context.active_object.data.layers[self.switch] = True"'\n'
                '\t''\t''\t'"for layer in self.layer_ui:"'\n'
                '\t''\t''\t''\t'"if layer != self.switch:"'\n'
                '\t''\t''\t''\t''\t'"context.active_object.data.layers[layer] = False"'\n'
                
                '\t''\t'"return {'FINISHED'}"'\n')

#---------------------WRITE _TO SECONDARY RIG---------------------------------
        file_write(
                '\n'
                '\n'
                f"class CHUI_OT_to_secondary_rig_{set_rig_id}(bpy.types.Operator):"'\n'
                '\t''bl_label = \"Toggle Armature\"''\n'
                '\t'f'bl_idname = \"chui.to_secondary_rig_{set_rig_id}\"''\n'
                '\t''bl_description = \"Show/Hide this Armature\"''\n'
                '\t''bl_options = {\"UNDO\"}''\n'
                '\n'    
                '\t''rig_name : StringProperty()''\n'
                '\n'   
                '\t''@classmethod''\n'
                '\t''def poll(self, context):''\n'
                '\t''\t''try:''\n'
                '\t''\t''\t''return (context.active_object.data.get(\"blm_rig_id\") == blm_rig_id)''\n'
                '\t''\t''except (AttributeError, KeyError, TypeError):''\n'
                '\t''\t''\t''return False''\n'
                '\n'
                '\t''def execute(self, context):''\n'
                '\t''\t''rig = bpy.data.objects[self.rig_name]''\n'
                '\t''\t''mode_now = context.object.mode''\n'
                '\t''\t''ac_ob = context.active_object''\n'
                '\n'       
                '\t''\t''if rig.visible_get() == False:''\n'
                '\t''\t''\t''rig.hide_viewport=False''\n'
                '\t''\t''\t''rig.hide_set(False)''\n'
                '\n'          
                '\t''\t''\t''if mode_now == \"POSE\":''\n'
                '\t''\t''\t''\t''bpy.ops.object.posemode_toggle()''\n'
                '\t''\t''\t''\t''bpy.data.objects[self.rig_name].select_set(True)''\n'
                '\t''\t''\t''\t''bpy.ops.object.posemode_toggle()''\n'
                '\t''\t''else:''\n'
                '\t''\t''\t''rig.hide_viewport=True''\n'

                '\t''\t''return {\'FINISHED\'}''\n' 
                )

            #---------------- SNAP FK BUTTON --------------------------------------

        if len(context.active_object.data.list_snap) > 0:
            file_write(
'\n'
'\n'
f'class CHUI_OT_snap_FKtoIK_{set_rig_id}(bpy.types.Operator):''\n'
'\t'f"bl_idname = 'chui_snap.fktoik_{set_rig_id}'"'\n'
'\t'"bl_label = 'Snap FK to IK'"'\n'
'\n'
'\t'"limb_index : IntProperty(name = 'snap_limb', default = -1)"'\n'
'\n'
'\t'"def execute(self, context):"'\n'
'\t''\t'"arma = context.active_object"'\n'
'\t''\t'"start_frame = context.scene.frame_start if context.scene.chui_bake_range else -1"'\n'
'\t''\t'"end_frame = context.scene.frame_end if context.scene.chui_bake_range else -1"'\n'
'\n'       
'\t''\t'"if start_frame < 0 or end_frame < 0:"'\n'
'\t''\t''\t'"start_frame = bpy.context.scene.frame_current"'\n'
'\t''\t''\t'"end_frame = start_frame + 1"'\n'
'\n'        
'\t''\t'"for frame in range(start_frame, end_frame):"'\n'
'\t''\t''\t'"bpy.context.scene.frame_set(frame)"'\n'
'\t''\t''\t'"self.snap_FK_to_IK("'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['IK_ctrl_first']],"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['IK_ctrl_second']],"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['IK_ctrl_third']],"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_first']],"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_second']],"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_third']])"'\n'
'\n'            
'\t''\t''\t'"if context.scene.chui_bake_range:"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_first']].keyframe_insert('location', frame=frame)"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_first']].keyframe_insert('rotation_quaternion', frame=frame)"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_second']].keyframe_insert('location', frame=frame)"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_second']].keyframe_insert('rotation_quaternion', frame=frame)"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_third']].keyframe_insert('location', frame=frame)"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_third']].keyframe_insert('rotation_quaternion', frame=frame)"'\n'
'\n'            
'\t''\t'"return {'FINISHED'}"'\n'
'\n'    
'\t'"def snap_FK_to_IK(self, IK_upper, IK_lower, IK_end, FK_upper, FK_lower, FK_end):"'\n'
'\t''\t'"FK_upper.matrix = IK_upper.matrix"'\n'
'\t''\t'"bpy.context.view_layer.update()"'\n'
'\n'       
'\t''\t'"FK_lower.matrix = IK_lower.matrix"'\n'
'\t''\t'"bpy.context.view_layer.update()"'\n'
'\n'        
'\t''\t'"FK_relative_to_IK = IK_end.bone.matrix_local.inverted() @ FK_end.bone.matrix_local"'\n'
'\t''\t'"FK_end.matrix = IK_end.matrix @ FK_relative_to_IK"'\n'
'\n'
#---------------- SNAP IK BUTTON --------------------------------------

'\n'
f"class CHUI_OT_snap_IKtoFK_{set_rig_id}(bpy.types.Operator):"'\n'
'\t'f"bl_idname = 'chui_snap.iktofk_{set_rig_id}'"'\n'
'\t'"bl_label = 'Snap'"'\n'
'\t'"bl_description = 'Snap IK to FK'"'\n'
'\t'"bl_options = {'UNDO'}"'\n'
'\n'
'\t'"limb_index : IntProperty(name = 'snap_limb', default = -1)"'\n'
'\n'
'\t'"def execute(self, context):"'\n'
'\t''\t'"arma = context.active_object"'\n'
'\t''\t'"start_frame = context.scene.frame_start if context.scene.chui_bake_range else -1"'\n'
'\t''\t'"end_frame = context.scene.frame_end if context.scene.chui_bake_range else -1"'\n'
'\n'      
'\t''\t'"if start_frame < 0 or end_frame < 0:"'\n'
'\t''\t''\t'"start_frame = bpy.context.scene.frame_current"'\n'
'\t''\t''\t'"end_frame = start_frame + 1"'\n'
'\n'               
'\t''\t'"for frame in range(start_frame, end_frame):"'\n'
'\t''\t''\t'"bpy.context.scene.frame_set(frame)"'\n'
'\t''\t''\t'"self.snap_IK_to_FK("'\n'
'\t''\t''\t''\t'"arma,"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_first']],"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_second']],"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['FK_ctrl_third']],"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['IK_controller']],"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['IK_pole']])"'\n'
'\n'           
'\t''\t''\t'"if context.scene.chui_bake_range:"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['IK_controller']].keyframe_insert('location', frame=frame)"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['IK_controller']].keyframe_insert('rotation_quaternion', frame=frame)"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['IK_pole']].keyframe_insert('location', frame=frame)"'\n'
'\t''\t''\t''\t'"arma.pose.bones[chui_limbs[self.limb_index]['IK_pole']].keyframe_insert('rotation_quaternion', frame=frame)"'\n'
'\n'           
'\t''\t'"return{'FINISHED'}"'\n'
'\n'
'\t'"def snap_IK_to_FK(self, armature, FK_upper, FK_lower, FK_end, IK_eff, IK_pole):"'\n'            

'\t''\t''\t'"IK_relative_to_Fk = FK_end.bone.matrix_local.inverted() @ IK_eff.bone.matrix_local"'\n'
'\t''\t''\t'"IK_eff.matrix = FK_end.matrix @ IK_relative_to_Fk"'\n'
'\t''\t''\t'"bpy.context.view_layer.update()"'\n'
            

'\t''\t''\t'"PV_normal = ((FK_lower.vector.normalized() + FK_upper.vector.normalized() * -1)).normalized()"'\n'

'\t''\t''\t'"PV_matrix_loc = FK_lower.matrix.to_translation() + (PV_normal * -0.2)"'\n'
'\t''\t''\t'"PV_matrix = Matrix.LocRotScale(PV_matrix_loc, IK_pole.matrix.to_quaternion(), None)"'\n'
'\t''\t''\t'"IK_pole.matrix = PV_matrix"'\n'            
            )      

# -----register--      
        
        file_write('\n''\n'"bpy.types.Scene.chui_bake_range = bpy.props.BoolProperty(name = 'Bake in Scene Frame Range', default = False, override = {'LIBRARY_OVERRIDABLE'})"'\n')
        
        if self.create_prop_panel:
            file_write('\n''\n'f"classes = [BLOP_PT_rigui_{set_rig_id}, BLOP_PT_customprops_{set_rig_id}, CHUI_OT_all_layers_{set_rig_id}, CHUI_OT_active_layer_{set_rig_id}] "'\n''\n')

        else:
            file_write('\n''\n'f"classes = (BLOP_PT_rigui_{set_rig_id}, CHUI_OT_all_layers_{set_rig_id}, class CHUI_OT_active_layer_{set_rig_id})"'\n''\n')
        
        if use_tweak == True or self.rig_tweak == True:
            file_write('\n' f"classes.append(CHUI_PT_tweaks_layers_{set_rig_id})"'\n''\n')

        if len(context.active_object.data.list_snap) > 0:
            file_write('\n' f"classes.append(CHUI_OT_snap_FKtoIK_{set_rig_id})"'\n''\n')
            file_write('\n' f"classes.append(CHUI_OT_snap_IKtoFK_{set_rig_id})"'\n''\n')

        if len(self.rig_linked) > 0:
            file_write('\n' f"classes.append(CHUI_OT_to_secondary_rig_{set_rig_id})"'\n''\n')

        if len(context.active_object.data.userProp_group) > 0 or self.snap_place == True:
            file_write('\n' f"classes.append(CHUI_PT_userproperties_{set_rig_id})"'\n''\n')

        file_write('register, unregister = bpy.utils.register_classes_factory(classes)''\n''\n')

        file_write("if __name__ == \"__main__\":"'\n')

        file_write('\t''register()')

        script_name = WRITEUI_OT_writeui.script_name = bpy.path.basename(self.filepath)
        if bpy.data.texts.get(script_name) != None:
            bpy.data.texts.remove(bpy.data.texts[script_name])
        bpy.data.texts.load(self.filepath)     

        ShowMessageBox(("Script generated successfully",), "Bone Layer Manager")
        
        return {'FINISHED'}



#-----------------  BIND -------------------------------------------------------------------------


class CHUI_OT_bind_scritp(bpy.types.Operator): 
    bl_label = "Bind"
    bl_idname = "chui.bind_script"
    bl_description = "Bind Last Generated UI to the Active Armature, Run the script and Register it."'\n'"Also Unbind old Sctipt if genereted by the add-on"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(self, context):
        try:
            context.active_object.data['blm_rig_id']            
            bpy.data.texts[WRITEUI_OT_writeui.script_name]
        except (KeyError, AttributeError, TypeError):
            return False
        return getattr(context.active_object, 'type', False) == 'ARMATURE'


    def execute(self, context):
        script_name = WRITEUI_OT_writeui.script_name
        # override = context.copy()                          NOTE:example override
        # override["edit_text"] =  bpy.data.texts[script_name]
        # with context.temp_override(**override):
        #     bpy.ops.text.reload()
        #     bpy.ops.text.run_script()
 
        area = bpy.context.area
        old_type = area.type
        area.type = 'TEXT_EDITOR'
        area.spaces[0].text = bpy.data.texts[script_name]
        bpy.ops.text.reload()
        if context.active_object.data.get('blm_rig_id') in bpy.data.texts[script_name].lines[0].body:
            garbage = []
            for name, prop in context.active_object.data.items():
                if 'dCH_' in name: 
                    garbage.append(name)
            for name in garbage:
                del context.active_object.data[name]

            bpy.ops.text.run_script()
            context.active_object['CH_Bind_UI'] = bpy.data.texts[script_name]
            bpy.data.texts[script_name].use_module = True
            self.report({'INFO'}, message = 'Script Loaded, Registered and Bound to the Active')
        else:
            self.report({'ERROR'}, message = f'{script_name} NOT compatible with {context.active_object.name}. Export Again!') 

        area.type = old_type
        

        return {'FINISHED'}