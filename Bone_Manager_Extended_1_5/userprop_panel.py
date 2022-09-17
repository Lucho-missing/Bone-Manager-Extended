
from typing import Any
import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty

from . blmfuncs import clean_string

# from . chui_data import CHUI_user_key_group, CHUI_user_key

#----------------LIST UI-----------------------------------------------

class CHUI_UL_group_prop(bpy.types.UIList):
    bl_options = {"COMPACT"}
    """List of Relevant Properties"""
    # active_index = None
    active_index : IntProperty()
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
   
       
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            grid = layout.column()
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            grid = layout.column()
        

        row = grid.row(align = True)

        if item.show_props == False: tria_ic = "DISCLOSURE_TRI_RIGHT"
        else: tria_ic = "DISCLOSURE_TRI_DOWN"
        if index == context.active_object.data.list_index: tria_em = True
        else: tria_em = False

        row.prop(item, "show_props", text = "", icon = tria_ic, emboss = tria_em)   

        row.prop(item, "group_name", icon = item.icon, text = "", emboss = False)

        
        row.separator()
        
        if index == context.active_object.data.list_index:
            row.alignment= "RIGHT"
            op0 = row.operator("chui_group.setting", text="", icon="SETTINGS")
            op0.index = context.active_object.data.list_index
            row.separator()
            op = row.operator("chui_remove.list", text="", icon="TRASH")
            op.index = index
            op.is_group = True
            row.separator()

        row.label(text = f"({len(item.keys)})")

        grid.separator()
        if item.show_props == True:
            if len(item.keys) < 1:
                row = grid.row(align = True)
                row.alignment = "LEFT"
                row.enabled = False
                row.label(text='    Use the add button next to property ---> ')
                row.label(text='', icon = 'FOLDER_REDIRECT')
            else:
                for ite in item.keys:
                    row = grid.row()
                    row.separator(factor = 0.5)
                    row.label(text = "-  " +  clean_string(ite.key))
                    if index == context.active_object.data.list_index:
                        op = row.operator("chui_remove.list", text="", icon="PANEL_CLOSE")
                        op.index = context.active_object.data.list_index
                        op.ind_pro = ite.index
                        op.is_group = False
                    row.separator(factor = 4)
            grid.separator()
            
       
   
   

#----------------MAIN PANEL-----------------------------------------------

class CHUI_PT_userproperties_select(bpy.types.Panel):
    bl_category = "Bone Layers"
    bl_label = "User Properties"
    bl_idname = "CHUI_PT_userproperties_select"
    bl_parent_id = "BLM_PT_customproperties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None):
            return True


    def draw(self, context):
        arm = context.active_object.data

        layout = self.layout
        tab = layout.row()
        grid = tab.column()
        row = grid.row()
       
        row.template_list("CHUI_UL_group_prop", 
                        "The_List", 
                        context.active_object.data,
                        "userProp_group", 
                        context.active_object.data, 
                        "list_index")
        
        grid = tab.column()
        row = grid.row()
        row = grid.row()
        row.operator('chui_add.user_group', text ="", icon ="NEWFOLDER")
        grid.separator()
        row = grid.row()
        
        up = row.operator('chui.move_item', text = "", icon = "TRIA_UP")
        up.direction = "UP"
        row = grid.row()
        up = row.operator('chui.move_item', text = "", icon = "TRIA_DOWN")
        up.direction = "DOWN"
        grid.separator()
        # for bone in context.selected_pose_bones:
        row = grid.row()
        row.operator('chui.clear_missing_data', text ="", icon = "FILE_REFRESH")

#----------------USER PROP PREVIEW-----------------------------------------------

class CHUI_PT_userproperties_preview(bpy.types.Panel):
    bl_category = "Bone Layers"
    bl_label = "User Properties Preview"
    bl_idname = "CHUI_PT_userproperties_preview"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None):
            return True


    def draw(self, context):
        groups = context.active_object.data.userProp_group

        layout = self.layout
        tab = layout.row()
        for group in groups:
            if group.show_header == True:
                tab = layout.row()
                tab.label(text = group.group_name, icon = group.icon)
            tab = layout.row()
            box = tab.box()
            if group.compact_ui == True: box.scale_y = 0.8
            grid = box.column()
            for key in group.keys:
                if getattr(context.active_object.pose.bones[key.bone], f'["{key.key}"]', None) != None:
                    row=grid.row()
                    row.label (text=clean_string(key.key))
                    row.separator()
                    row.prop(context.active_object.pose.bones[key.bone], f'["{key.key}"]', text ="", slider = True)
                else:
                    row=grid.row()
                    row.label (text = key.bone + f"  -  {key.key}  -  Data Missing.")
              



#----------------ADD GROUP-----------------------------------------------

class CHUI_OT_add_user_group(bpy.types.Operator):
    bl_idname = "chui_add.user_group"
    bl_label = "Add Property Group"
    bl_description = "Create Bones Propery Group always Visibile in the UI"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return getattr(context.active_object, 'pose', None)

    def execute(self, context):
        gr = context.active_object.data.userProp_group.add()
        # gr.group_name = "User Group"
        gr.group_name = f"User Group #{len(context.active_object.data.userProp_group)}"
        return{'FINISHED'}

#----------------ADD USER PROP-----------------------------------------------

class CHUI_OT_add_user_prop(bpy.types.Operator):
    bl_idname = "chui_add.user_prop"
    bl_label = "Send Property to the Selected Group:"
    # bl_description = ""
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None) and len(context.active_object.data.userProp_group) > 0:
            return True
        else:
            return False

    bone : StringProperty(name="Bone",
              description="Later",
              default="Untitled")
    key : StringProperty(name="Key",
            description="Later",
            default="Untitled")


    @classmethod
    def description(cls, context, properties):
        return context.active_object.data.userProp_group[context.active_object.data.list_index].group_name
        
        
    def execute(self, context):
        list_ =context.active_object.data.userProp_group
        ac_index = context.active_object.data.list_index
        # print (ag_index)
        pr = list_[ac_index].keys.add()
        pr.bone = self.bone
        pr.key = self.key
        pr.index = (len(list_[ac_index].keys))-1
        return{'FINISHED'}

#---------------------REMOVE ITEM -----------------------------------------

class CHUI_OT_remove_list(bpy.types.Operator):
    bl_idname = "chui_remove.list"
    bl_label = "Remove this Item:"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return getattr(context.active_object, 'pose', None)
    
    @classmethod
    def description(cls, context, properties):
        return context.active_object.data.userProp_group[context.active_object.data.list_index].group_name

    # us_list : CollectionProperty(type = CHUI_user_key_group)
    index : IntProperty()
    
    is_group :  BoolProperty()

    ind_pro : IntProperty()

    def execute(self, context):
        if self.is_group == True:
            context.active_object.data.userProp_group.remove(self.index)
            context.active_object.data.list_index = min(max(0, self.index - 1), len(context.active_object.data.userProp_group) - 1)
        else:
            key_list = context.active_object.data.userProp_group[self.index].keys
            key_list.remove(self.ind_pro)
            for it in range(self.ind_pro, (len(key_list))):
                key_list[it].index -= 1
        return{'FINISHED'}


class CHUI_OT_group_setting(bpy.types.Operator):
    bl_idname = "chui_group.setting"
    bl_label = "Customize Group UI"
    bl_options = {'REGISTER','UNDO'}

    
    @classmethod
    def description(cls, context, properties):
        return ("Change Icon, Show Header of " + clean_string(context.active_object.data.userProp_group[context.active_object.data.list_index].group_name))
    

    icon : StringProperty(name="Icon",
            description="To Select an Icon for this Group, type the Name uppercase without quotation marks ex: PARTICLE_DATA",
            default="FILE_FOLDER")

    index : IntProperty()

    def draw(self, context):
        layout = self.layout
        grid = layout.row()
        
        tab = grid.column()
        row = tab.row()
        try:
            row.label (text="", icon = self.icon)
            row = tab.row()
            row.label(text = "Icon Ok")
        except TypeError:
            row.label (text="")
            row = tab.row()
            row.alert = True
            row.label(text = "Icon Ivalid") 

        
        tab = grid.column()
        row = tab.row()
        row.prop(context.active_object.data.userProp_group[self.index], "group_name")
        tab.separator()
        row = tab.row()
        row.prop (self, "icon")
        try:
            row.operator("iv.icons_show", text = "" , icon = "COPYDOWN")
        except: pass
        tab.separator()
        row = tab.row()
        row.prop(context.active_object.data.userProp_group[self.index], "show_header")
        tab.separator()
        row = tab.row()
        # row.label(text = "Scale Group")
        row.prop(context.active_object.data.userProp_group[self.index], "compact_ui")
        tab.separator()

    def invoke(self, context, event):
        self.icon = context.active_object.data.userProp_group[self.index].icon
        context.window_manager.invoke_props_dialog(self, width=300)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # context.active_object.data.userProp_group[self.index].show_header = self.show_header
        found = False
        for ic in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys():
            if ic == self.icon:
                context.active_object.data.userProp_group[self.index].icon = self.icon
                found = True
                break
        if found == False:
            self.icon = context.active_object.data.userProp_group[self.index].icon
            self.report({'INFO'}, message="Icon NOT valid. Restored.")
        
            
        
        return{'FINISHED'}

class CHUI_OT_MoveItem(bpy.types.Operator):
    """Move an item in the list."""

    bl_idname = "chui.move_item"
    bl_label = "Move a Item Up/Down"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return len(context.active_object.data.userProp_group) > 1
    
    def move_index(self, context):
        """ Move index of an item render queue while clamping it. """
        groups = context.active_object.data.userProp_group
        index = context.active_object.data.list_index
        list_length = len(groups) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        context.active_object.data.list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        my_list = context.active_object.data.userProp_group
        index = context.active_object.data.list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        my_list.move(neighbor, index)
        self.move_index(context)

        return{'FINISHED'}

class CHUI_OT_update_user_prop(bpy.types.Operator):
    """Clear Invalid Data."""

    bl_idname = "chui.clear_missing_data"
    bl_label = "Update"

    def execute(self, context):
        counter=0
        for ind in range(len(context.active_object.data.userProp_group)):
            garbage = []
            for key in context.active_object.data.userProp_group[ind].keys:
                if getattr(context.active_object.pose.bones[key.bone], f'["{key.key}"]', None)  == None:
                    garbage.append(key.index)
            for item in garbage:
                # group.keys.remove(item.index)
                bpy.ops.chui_remove.list(index = ind, is_group = False, ind_pro = item)
                    # cleaner.is_group = False
                    # cleaner.ind_pro = item.index
                    # cleaner.index = context.active_object.data.userProp_group.find(group)

                counter += 1
        self.report({'INFO'}, message=f"Deleted {counter} invalid elements")
        

        return{'FINISHED'}
