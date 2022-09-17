from email.policy import default
from queue import Empty
import bpy

from .blmfuncs import prefs, clean_string
from .create_layer_id import CHUI_OP_clear_data, CHUI_OP_other_rigs, CHUI_OT_to_secondary_rig




class BLM_PT_rigui(bpy.types.Panel):
    # Creates a Rig UI Panel for based on the assigned Rig_ui_ID
    bl_category = "Bone Layers"
    bl_label = "Rig UI & Export All"
    bl_idname = "BLM_PT_rigui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    

    @classmethod
    def poll(self, context):
        if context.active_object == None:
            return False
        if getattr(context.active_object, 'pose', None):
            return True
        for ob in context.selected_objects:  # Check for armature in all objects (Add support for Weight Painting)
            if ob.type == 'ARMATURE':
                return True
    
    
    


    def draw(self, context):
        need_ud = True
        layout = self.layout
        ac_ob = context.active_object
        
        if CHUI_OP_other_rigs.never_run == True: 
            need_ud = True
        else: need_ud = False

        
        objects = (
            # List of selected rigs, starting with the active object (if it's a rig)
            *[o for o in {ac_ob} if o and o.type == 'ARMATURE'],
            *[o for o in context.selected_objects
              if (o != ac_ob and o.type == 'ARMATURE')],
        )

        

        empty_ui = True
        grid = layout.column(align = True) #grid BIGGER COLUMN
               #---ok
        
        
        col = grid.row()       # INVERT FLOW
        row = col.column()
        row.alignment = 'LEFT'
        row.label(text = clean_string(ac_ob.name), icon='ARMATURE_DATA')
        # row = col.column()

        col.scale_x = 1.2
        row = col.column()
        
        row.operator("bone_layer_man.write_rig_ui", emboss=True, icon='EXPORT', text="Export")  
        row = col.column()        
        row.operator("chui.bind_script", emboss=True,  icon='PIVOT_MEDIAN', text="Bind")
        grid.separator()

        box = grid.box()
        inv = box.column()
        col = inv.row()       # INVERT FLOW
        row = col.column()
        row.alert = need_ud
        if CHUI_OP_other_rigs.visible == True and CHUI_OP_other_rigs.never_run == False:
            row.operator('chui.other_rigs', icon = 'TRIA_UP', text = "")
        else:
            row.operator('chui.other_rigs', icon = 'FILE_REFRESH', text = "")
        row = col.column()
        row.label(text = "Link Rig:")
               
        row = col.column()
        op = row.operator("chui.clear_data", icon = 'TRASH', text = "")
        op.target = ac_ob.name
        op.string = "CHUI"
        
        # row.prop(op, "['hide_mp']")
        
        
        
        
        
            # rig list & selection

        if len(CHUI_OP_other_rigs.rig) > 0 :
            first_row = True      
            if CHUI_OP_other_rigs.visible == True:
                for obj in CHUI_OP_other_rigs.rig:
                    if obj != ac_ob.name:
                        if first_row == True :
                            col = box.column()
                            row = col.row()
                            first_row = False
                        
                        row = col.row()
                        row.label(text = clean_string(obj), icon = 'ARMATURE_DATA') 
                        row.scale_x = 0.5
                        if ac_ob.data.get(f'CHUI_L_{obj}') != None:
                            op = row.operator('chui.link_rig', text = "Unlink", icon = "UNLINKED")
                        else:
                            op = row.operator('chui.link_rig', text = "Link", icon = "LINKED")
                        op.rig_name = obj
                        #op.rig = bpy.data.objects[obj]
                        row = col.row()
                              
            col = grid.column(align = True)
            col.separator()
            to_head = True
            fr_row = True
            for obj in CHUI_OP_other_rigs.rig:
                if ac_ob.data.get(f'CHUI_L_{obj}') != None: 
                    if to_head == True: 
                        row = col.row (align=True)
                        if fr_row == True:
                            row.label(text = "Connected Rigs:")
                            row = col.row (align=True)
                            fr_row = False
                    try:
                        ro = row.operator('chui.to_secondary_rig', text = clean_string(obj), depress = not bpy.data.objects[obj].hide_viewport)
                        ro.rig_name = obj
                        # ro.rig = obj
                    except (KeyError):
                        CHUI_OP_other_rigs.reset_list(context)
                        CHUI_OP_other_rigs.never_run = True
                        
                    to_head = not to_head
            col.separator()  
        
        

        for ac_ob in objects:
            arm = ac_ob.data
            rows = {}

            # Iterate through layers finding rows for the Rig UI


            for x in range(33):
                name = arm.get(f"layer_name_{x}", "*NO NAME*")
                if name == "":
                    name = "*NO NAME*"
                layer = arm.get(f"rigui_id_{x}", None)

                if layer is not None and layer in range(33):
                    if x > 15: layer += 15
                    # If the row hasn't been assigned, create empty list for it
                    row = rows[layer] = rows.get(layer, [])
                    row.append([name, x])

        

            if not rows:
                continue
            empty_ui = False

            grid.separator()
            # Display Rig name
            # if (len(objects) > 1):
            med = grid.box()
            col=med.row(align = True)

            row = col.column()
            row.label (text="Main Layers:")
            if len(objects) > 1:
                row = col.column()
                row.label (text=clean_string(ac_ob.name), icon = 'ARMATURE_DATA')
            
            pol=med.row(align = True)
            col = pol.column(align = True)
      
            # Display layer buttons

            breaked = False

            for i in sorted(rows):
                row = col.row(align=True)
                for (name, x) in rows[i]:
                    if x > 15 and breaked == False:
                        breaked = True
                        # col.separator()
                        row = col.row(align=True)
                        row.label(text = "Tweak")
                        row = col.row(align=True)
                        
                    row.prop(arm, 'layers', index=x, toggle=True, text=name)
            

        if empty_ui:
            layout.label(text="No available UI layers in rigs", icon='INFO')

        
        
        

        
        


                