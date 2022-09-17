import string
from mathutils import Matrix
from math import isclose
import bpy

from . blmfuncs import clean_string

from . chui_data import CHUI_bones_snappig
from bpy.props import CollectionProperty, IntProperty

#------------ Funcions -------------------------------------------------------

def validate_limb(context, limb):
    arm = context.active_object.data
    if limb.limb_name == "": return False
    if limb.IK_pole == None or limb.IK_pole == "Not Found" or limb.IK_pole == "": return False
    if limb.IK_controller == None or limb.IK_controller == "Not Found" or limb.IK_controller == "": return False
    if limb.FK_ctrl_third == None or limb.IK_pole == "Not Found" or limb.IK_pole == "": return False
    if limb.IK_ctrl_third == None or limb.IK_pole == "Not Found" or limb.IK_pole == "": return False
    if limb.IK_ctrl_second == None or limb.IK_pole == "Not Found" or limb.IK_pole == "": return False
    if limb.FK_ctrl_second == None or limb.IK_pole == "Not Found" or limb.IK_pole == "": return False
    if limb.IK_ctrl_first == None or limb.IK_pole == "Not Found" or limb.IK_pole == "": return False
    if limb.FK_ctrl_first == None or limb.IK_pole == "Not Found" or limb.IK_pole == "": return False
    return True

def draw_limb_setting(self,context, box, limb, buttons = True):
    grid = box.row(align = True)

    tab = grid.column()
    tab.alignment = 'RIGHT'
    tab.label(text ="")
    tab.label(text ="First  ")
    tab.label(text ="Second ")
    tab.label(text ="Third  ") 
    if limb.IK_ctrl_third == "Not Found":
        tab.alert = True
    
    
    tab = grid.column()
    tab.label(text =" FK", icon="SEQUENCE_COLOR_04")
    tab.prop_search(limb, "FK_ctrl_first", context.active_object.data, "bones", text ="")
    tab.prop_search(limb, "FK_ctrl_second", context.active_object.data, "bones", text ="")
    tab.prop_search(limb, "FK_ctrl_third", context.active_object.data, "bones", text ="")
    


    tab = grid.column()
    tab.label(text =" IK", icon = "SEQUENCE_COLOR_01") 
    tab.prop_search(limb, "IK_ctrl_first", context.active_object.data, "bones", text ="")
    tab.prop_search(limb, "IK_ctrl_second", context.active_object.data, "bones", text ="")
    tab.prop_search(limb, "IK_ctrl_third", context.active_object.data, "bones", text ="")
    
    grid = box.row(align = True)
    
    tab = grid.column()
    tab.alignment = 'RIGHT'
    tab.label(text= "")
    tab.label(text="IK Controls ")
    tab.separator(factor = 2)
    tab.label(text = "Limb Name ")

    tab = grid.column()
    
    tab.label(text= "IK Controller")
    tab.prop_search(limb, "IK_controller", context.active_object.data, "bones", text ="")
    tab.separator(factor = 2)
    tab.prop(limb, "limb_name", text="")
    tab = grid.column()
    tab.label(text= "IK Pole")
    tab.prop_search(limb, "IK_pole", context.active_object.data, "bones", text ="")
    tab.separator(factor = 2)
    # if buttons == True:
    #     tab.operator("chui_create.snap_group")

    return tab

#---------------- PREVIEW PANEL -----------------------------------------------

class CHUI_PT_snap_preview(bpy.types.Panel):
    bl_category = "Bone Layers"
    bl_label = "IK/FK Snapping Preview"
    bl_idname = "CHUI_PT_snap_preview"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None):
            return True

    def draw(self, context):
        layout = self.layout
        grid = layout.column()
        row = grid.row()
        row.alignment = 'LEFT'

        col = row.column()
        
        if len(context.active_object.data.list_snap) > 0:
            col.label(text = "Current Frame")
            if context.active_object.data.use_frame_range == True:
                col.enabled = False
            col.scale_x = 0.5
            row.prop(context.active_object.data, "use_frame_range", text = "", slider = True)
            
            col = row.column()
            col.label(text = "Bake in Scene Frame Range")
            if context.active_object.data.use_frame_range == False:
                col.enabled = False
            grid.separator(factor = 2)

            row = grid.row()
            row.label(text="Snap FK to IK", icon = 'SNAP_ON')
            row.label(text="Snap IK to FK", icon = 'SNAP_ON')
            
            

            for inde in range(len(context.active_object.data.list_snap)):
                row = grid.row()
                op2 = row.operator('chui_snap.fktoik', text =context.active_object.data.list_snap[inde].limb_name , icon = "SEQUENCE_COLOR_04")
                op2.limb_index = inde
                op = row.operator('chui_snap.iktofk', text =context.active_object.data.list_snap[inde].limb_name , icon = "SEQUENCE_COLOR_01")
                op.limb_index = inde
                
                mo = row.operator('chui_modify.limb', text = "", icon= 'SETTINGS')
                mo.limb_index = inde
                de= row.operator('chui_remove.limb' ,text = "", icon= 'TRASH')
                de.limb_index = inde


#---------------- MAIN PANEL -----------------------------------------------

class CHUI_PT_snap_config(bpy.types.Panel):
    bl_category = "Bone Layers"
    bl_label = "IK/FK Snapping Configuration"
    bl_idname = "CHUI_PT_snap_config"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None):
            return True

    def draw(self, context):
        layout = self.layout
        grid = layout.row(align = True)
        tab = grid.column()
        tab.operator("chui_detect.ikfk_sys", icon = "SHADERFX")
        row = draw_limb_setting(self, context, layout, context.active_object.data.dummy_snap)
        row2 = row.row()
        row2.separator()
        row2.operator("chui_create.snap_group")
        row2.operator("chui_clear.fields", text="", icon = "TRASH")


#---------------- CREATE SNAP GROUP -----------------------------------------------

class CHUI_OT_create_snap_group(bpy.types.Operator):
    bl_idname = "chui_create.snap_group"
    bl_label = "Create Limb"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        dum = context.active_object.data.dummy_snap
        if dum.FK_ctrl_first  != '' and dum.IK_ctrl_first != '' and dum.FK_ctrl_second != '' and dum.IK_ctrl_second != '' and dum.FK_ctrl_third != ''  and dum.IK_ctrl_third != '' and dum.IK_controller != '' and dum.IK_pole != '' and dum.limb_name != "":
                return True
        else: return False

    def execute(self, context):
        dum = context.active_object.data.dummy_snap
        
        context.active_object.data.list_snap.add()
        context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].limb_name = dum.limb_name

        context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_pole = dum.IK_pole
        context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_controller = dum.IK_controller

        context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_ctrl_third = dum.IK_ctrl_third
        context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].FK_ctrl_third = dum.FK_ctrl_third
        context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_ctrl_second = dum.IK_ctrl_second
        context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].FK_ctrl_second = dum.FK_ctrl_second       
        context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_ctrl_first = dum.IK_ctrl_first
        context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].FK_ctrl_first = dum.FK_ctrl_first
        
        return{'FINISHED'}

#---------------- CLEAR FIELDS --------------------------------------

class CHUI_OT_clear_fields(bpy.types.Operator):
    bl_idname = "chui_clear.fields"
    bl_label = "Clear Fields"
    bl_options = {'UNDO'}


    def execute(self, context):
        dum = context.active_object.data.dummy_snap
        dum.limb_name = ""
        dum.IK_pole = ""
        dum.IK_controller = ""
        dum.IK_ctrl_third = ""
        dum.FK_ctrl_third = ""
        dum.IK_ctrl_second = ""
        dum.FK_ctrl_second = ""
        dum.IK_ctrl_first = ""
        dum.FK_ctrl_first = ""
        

        return{'FINISHED'}

#---------------- SNAP FK BUTTON --------------------------------------

class CHUI_OT_snap_FKtoIK(bpy.types.Operator):
    bl_idname = 'chui_snap.fktoik'
    bl_label = 'Snap FK to IK'

    limb_index : IntProperty(name = "snap_limb", default = -1)

    def execute(self, context):
        arma = context.active_object
        start_frame = context.scene.frame_start if context.active_object.data.use_frame_range else -1
        end_frame = context.scene.frame_end if context.active_object.data.use_frame_range else -1
        
        if start_frame < 0 or end_frame < 0:
            start_frame = bpy.context.scene.frame_current
            end_frame = start_frame + 1
        
        for frame in range(start_frame, end_frame):
            bpy.context.scene.frame_set(frame)
            self.snap_FK_to_IK(
                arma.pose.bones[arma.data.list_snap[self.limb_index].IK_ctrl_first],
                arma.pose.bones[arma.data.list_snap[self.limb_index].IK_ctrl_second],
                arma.pose.bones[arma.data.list_snap[self.limb_index].IK_ctrl_third],
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_first],
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_second],
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_third],
            )
            
            if context.active_object.data.use_frame_range:
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_first].keyframe_insert('location', frame=frame)
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_first].keyframe_insert('rotation_quaternion', frame=frame)
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_second].keyframe_insert('location', frame=frame)
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_second].keyframe_insert('rotation_quaternion', frame=frame)
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_third].keyframe_insert('location', frame=frame)
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_third].keyframe_insert('rotation_quaternion', frame=frame)
            
        return {'FINISHED'}
    
    def snap_FK_to_IK(self, IK_upper, IK_lower, IK_end, FK_upper, FK_lower, FK_end):
        FK_upper.matrix = IK_upper.matrix
        bpy.context.view_layer.update()
        
        FK_lower.matrix = IK_lower.matrix
        bpy.context.view_layer.update()
        
        FK_relative_to_IK = IK_end.bone.matrix_local.inverted() @ FK_end.bone.matrix_local
        FK_end.matrix = IK_end.matrix @ FK_relative_to_IK

#---------------- SNAP IK BUTTON --------------------------------------

class CHUI_OT_snap_IKtoFK(bpy.types.Operator):
    bl_idname = "chui_snap.iktofk"
    bl_label = "Snap"
    bl_description = "Snap IK to FK"
    bl_options = {'UNDO'}

    limb_index : IntProperty(name = "snap_limb", default = -1)

    def execute(self, context):
        arma = context.active_object
        start_frame = context.scene.frame_start if context.active_object.data.use_frame_range else -1
        end_frame = context.scene.frame_end if context.active_object.data.use_frame_range else -1
        
        if start_frame < 0 or end_frame < 0:
            start_frame = bpy.context.scene.frame_current
            end_frame = start_frame + 1
        
        

        for frame in range(start_frame, end_frame):
            bpy.context.scene.frame_set(frame)
            self.snap_IK_to_FK(
                arma,
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_first],
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_second],
                arma.pose.bones[arma.data.list_snap[self.limb_index].FK_ctrl_third],
                arma.pose.bones[arma.data.list_snap[self.limb_index].IK_controller],
                arma.pose.bones[arma.data.list_snap[self.limb_index].IK_pole]
            )
            
            if context.active_object.data.use_frame_range:
                arma.pose.bones[arma.data.list_snap[self.limb_index].IK_controller].keyframe_insert('location', frame=frame)
                arma.pose.bones[arma.data.list_snap[self.limb_index].IK_controller].keyframe_insert('rotation_quaternion', frame=frame)
                arma.pose.bones[arma.data.list_snap[self.limb_index].IK_pole].keyframe_insert('location', frame=frame)
                arma.pose.bones[arma.data.list_snap[self.limb_index].IK_pole].keyframe_insert('rotation_quaternion', frame=frame)
            
        return{'FINISHED'}

    def snap_IK_to_FK(self, armature, FK_upper, FK_lower, FK_end, IK_eff, IK_pole):
            
            # Set IK effector matrix relative to the original FK end bone in armature space
            IK_relative_to_Fk = FK_end.bone.matrix_local.inverted() @ IK_eff.bone.matrix_local
            IK_eff.matrix = FK_end.matrix @ IK_relative_to_Fk
            bpy.context.view_layer.update()
            
            # Get the vector bisecting each FK control (object space)
            PV_normal = ((FK_lower.vector.normalized() + FK_upper.vector.normalized() * -1)).normalized()
            
            # We push the pole control in the opposite direction of the FK bisecting vector (object space)
            PV_matrix_loc = FK_lower.matrix.to_translation() + (PV_normal * -0.2)
            PV_matrix = Matrix.LocRotScale(PV_matrix_loc, IK_pole.matrix.to_quaternion(), None)
            IK_pole.matrix = PV_matrix

#-------------- REMOVE LIMB ----------------------------------

class CHUI_OT_remove_limb(bpy.types.Operator):
    bl_idname = "chui_remove.limb"
    bl_label = "Delete Limb System"
    bl_options = {'UNDO'}

    limb_index : IntProperty(name = "snap_limb", default = -1)

    def execute(self, context):
        context.active_object.data.list_snap.remove(self.limb_index)
        return{'FINISHED'}

#---------- AUTODETECTION OPERATOR -------------------------------------------

class CHUI_OT_detect_ikfk_sys(bpy.types.Operator):
    bl_idname = "chui_detect.ikfk_sys"
    bl_label = "Autodetect (Rest Pose)"
    bl_description = "Search for Compatible IK/FK Chain, the Armature needs to be in Rest Pose!"
    bl_options = {'REGISTER','UNDO'}


    def are_similar_bones(self, context, bone_1, bone_2):
        head_close = isclose(bone_1.head.x, bone_2.head.x, abs_tol=0.01) and isclose(bone_1.head.y, bone_2.head.y, abs_tol=0.01) and isclose(bone_1.head.z, bone_2.head.z, abs_tol=0.01)
        len_close = isclose(bone_1.length, bone_2.length, abs_tol=0.01)

        return head_close and len_close
    
    def is_org_bone (self, bone):
        for constr in bone.constraints:
            if constr.type == 'COPY_TRANSFORMS' or constr == 'COPY_LOCATION':
                return True
        return False

    def draw(self, context):
        layout = self.layout
        if len(context.active_object.data.list_snap) < 1:
            row= layout.row()
            row.label (text = "No elegible chain found, use manual insertion.")
        for ind in range(len(context.active_object.data.list_snap)): 
            layout = self.layout
            layout.scale_y = 0.8
            pan = layout.column()
            grid = pan.row()
            box = grid.box()
            tab = draw_limb_setting(self, context, box, context.active_object.data.list_snap[ind])          
            op = tab.operator("chui_remove.limb", text = "Delete Limb", icon ="TRASH")
            op.limb_index = ind
            pan.separator()

    def invoke(self, context, event):
        for bon_i in context.active_object.pose.bones:
            if bon_i.is_in_ik_chain:
                for child_i in bon_i.children:
                        if child_i.is_in_ik_chain:
                            #check if the second in the chain got IK with valid pole
                            is_ik_solved = False                           
                            for ik_constr in child_i.constraints:
                                if ik_constr.type == 'IK'and ik_constr.pole_subtarget != '':                                  
                                    ik_pole = context.active_object.pose.bones[ik_constr.pole_subtarget]
                                    niece_i = context.active_object.pose.bones[ik_constr.subtarget]      
                                    # IK ACCEPTED
                                    if "IK" in niece_i.name.upper() and "MCH" not in niece_i.name.upper() and "ORG" not in niece_i.name.upper() and "spin" not in niece_i.name.lower() and "roll" not in niece_i.name.lower() and "heel" not in niece_i.name.lower():
                                        ik_ctrl = niece_i
                                        is_ik_solved = True
                                    #solve the ik controller: check if there is a copy constr with valid target
                                    if is_ik_solved == False:
                                        for copy_constr in niece_i.constraints:
                                            if copy_constr.type == 'COPY_LOCATION' or copy_constr == 'COPY_TRANSFORMS':
                                                if "IK" in copy_constr.subtarget.upper() and "MCH" not in copy_constr.subtarget.upper() and "ORG" not in copy_constr.subtarget.upper() and "spin" not in copy_constr.subtarget.lower() and "roll" not in copy_constr.subtarget.lower() and "heel" not in copy_constr.subtarget.lower():
                                                    ik_ctrl = context.active_object.pose.bones[copy_constr.subtarget]
                                                    is_ik_solved = True
                                    #solve the ik controller: check parent recursive
                                    if is_ik_solved == False:
                                        for proniece in niece_i.parent_recursive:
                                            if "IK" in proniece.name.upper() and "MCH" not in proniece.name.upper() and "ORG" not in proniece.name.upper() and "spin" not in proniece.name.lower() and "roll" not in proniece.name.lower() and "heel" not in proniece.name.lower():
                                                ik_ctrl = proniece
                                                is_ik_solved = True
                                                break
                                    #give up
                                    if is_ik_solved == False:
                                        ik_ctrl = None
                                                                           
                                    #look for a chain compatible with the ik
                                    for bon_f in context.active_object.pose.bones:
                                        if bon_f.is_in_ik_chain == False and self.are_similar_bones(context, bon_i, bon_f) and self.is_org_bone(bon_f) == False:
                                            for child_f in bon_f.children:
                                                if child_f.is_in_ik_chain == False and self.are_similar_bones(context, child_i, child_f) and self.is_org_bone(child_f) == False:
                                                    is_fk_solved = False
                                                    # print (bon_f.name)                                          # FK ACCEPTED
                                                    # print (child_f.name)
                                                    #serch for the last in the chain
                                                    for niece_f in child_f.children_recursive:
                                                        if niece_f.is_in_ik_chain == False and self.are_similar_bones(context, niece_f, niece_i) and self.is_org_bone(niece_f) == False and "FK" in niece_f.name.upper() and "MCH" not in niece_f.name.upper() and "ORG" not in niece_f.name.upper() and "spin" not in niece_f.name.lower() and "roll" not in niece_f.name.lower() and "heel" not in niece_f.name.lower():
                                                                is_fk_solved = True
                                                                break
                                                      
                                                    if is_fk_solved == False:
                                                        niece_f = None

                                                    context.active_object.data.list_snap.add()
                                                    context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].limb_name = clean_string(bon_f.name)

                                                    context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_pole = ik_pole.name

                                                    if ik_ctrl == None: context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_controller = "Not Found"
                                                    else:  context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_controller = ik_ctrl.name

                                                    context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_ctrl_third = niece_i.name
                                                    
                                                    if niece_f == None: context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].FK_ctrl_third = "Not Found"
                                                    else: context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].FK_ctrl_third = niece_f.name
                                                    
                                                    
                                                    context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_ctrl_second = child_i.name
                                                    context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].FK_ctrl_second = child_f.name     
                                                    context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].IK_ctrl_first = bon_i.name
                                                    context.active_object.data.list_snap[len(context.active_object.data.list_snap)-1].FK_ctrl_first = bon_f.name   
                                                    

        context.window_manager.invoke_props_dialog(self, width=400)
       
        return {'RUNNING_MODAL'}

    def execute(self, context):
        garbage=[]
        for ind in range(len(context.active_object.data.list_snap)):
            if validate_limb(context, context.active_object.data.list_snap[ind]) == False:
                garbage.append(ind)

        for ind in reversed(garbage):
            context.active_object.data.list_snap.remove(ind)
        return{'FINISHED'}                    


    def cancel(self, context) :
        garbage=[]
        for ind in range(len(context.active_object.data.list_snap)):
            if validate_limb(context, context.active_object.data.list_snap[ind]) == False:
                garbage.append(ind)

        for ind in reversed(garbage):
            context.active_object.data.list_snap.remove(ind)

        
        return None                  

class CHUI_OT_modify_limb(bpy.types.Operator):
    bl_idname = "chui_modify.limb"
    bl_label = "Tweak Limb System"
    bl_options = {'UNDO'}

    limb_index : IntProperty(name = "snap_limb", default = -1)


    def draw(self, context):
        layout = self.layout
        draw_limb_setting(self,context, layout, context.active_object.data.list_snap[self.limb_index])

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, width=400)
        return {'RUNNING_MODAL'}
    def execute(self, context):
        
        return{'FINISHED'}       