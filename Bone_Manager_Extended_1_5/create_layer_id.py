
import bpy
from bpy.app.handlers import persistent
from bpy.props import IntProperty, StringProperty, BoolProperty, PointerProperty
from .blmfuncs import check_clear





class CREATEID_OT_name(bpy.types.Operator):
    # Assign and store a name for this layer as ID prop
    bl_idname = "bone_layer_man.layout_do_name"
    bl_label = "Assign Name"
    bl_description = "Assign and store a name for this layer"
    bl_options = {'REGISTER', 'UNDO'}

    layer_idx: IntProperty(name="Layer Index",
                           description="Index of the layer to be named",
                           default=0, min=0, max=31,
                           options = {'HIDDEN'})

    layer_name: StringProperty(name="Layer Name",
                               description="Name of the layer",
                               default="")

    @classmethod
    def poll(self, context):
        arm = getattr(context.active_object, 'data', None)
        not_link = (getattr(arm, 'library', None) is None)
        return not_link

    def execute(self, context):
        arm = context.active_object.data
        # Create ID prop by setting it
        arm[f"layer_name_{self.layer_idx}"] = self.layer_name

        return {'FINISHED'}
# ----------------------------------------------------------------
        ### OTHER RIG

class CHUI_OP_other_rigs(bpy.types.Operator):
    bl_idname = "chui.other_rigs"
    bl_label = "Update Armatures"
    bl_description = "Show the Armatures in the Scene and clean garbage data"
    bl_options = {'REGISTER','UNDO'}

    
    @classmethod
    def poll(self, context):
        arm = getattr(context.active_object, 'data', None)
        # not_link = (getattr(arm, 'library', None) is None)
        return arm

    visible = False
    never_run = True
    rig = []
    
    @persistent
    def reset_list(context):
        CHUI_OP_other_rigs.rig.clear()
        for obj in bpy.data.objects:
            # and getattr(obj, 'override_library') == None
            if obj.type == 'ARMATURE':
                for scen in obj.users_scene:
                    if scen == bpy.context.scene:
                        CHUI_OP_other_rigs.rig.append(obj.name)
                        break
    
    

    def execute(self, context):
        ac_ob = context.active_object
        
        CHUI_OP_other_rigs.reset_list(context)

        if CHUI_OP_other_rigs.never_run == False:
            CHUI_OP_other_rigs.visible = not CHUI_OP_other_rigs.visible 
        else:
             CHUI_OP_other_rigs.visible = True
        
        garbage = []
        for name, prop in ac_ob.data.items():
            if 'CHUI_L' in name:
                found = False
                for obj in CHUI_OP_other_rigs.rig:
                    if f"CHUI_L_{obj}" == name:
                        found = True
                        break
                if found == False: 
                    garbage.append(name)
        for name in garbage:
            del ac_ob.data[name]         

        CHUI_OP_other_rigs.never_run = False         
        
        return {'FINISHED'}


#------------------------------------------------------------------
    ### TO SECONDARY RIG

class CHUI_OT_to_secondary_rig(bpy.types.Operator): 
    bl_label = "Toggle Armature"
    bl_idname = "chui.to_secondary_rig"
    bl_description = "Show/Hide this Armature"
    bl_options = {"UNDO"}
    
    # rig_path : StringProperty ()
    rig_name : StringProperty()
    # vis : BoolProperty(default = False) = False
    
    
    @classmethod
    def poll(self, context):
        arm = getattr(context.active_object, 'data', None)
        # not_link = (getattr(arm, 'library', None) is None)
        return arm
    
 
    def execute(self, context):
        # rig = eval(self.rig_path)
        rig = bpy.data.objects[self.rig_name]
       
        mode_now = context.object.mode
        ac_ob = context.active_object
        
        if rig.visible_get() == False:
            rig.hide_viewport=False
            rig.hide_set(False)
            #rig.users_collection[0].hide_viewport=False
            # self.vis = True
            
            if mode_now == "POSE":      
                bpy.ops.object.posemode_toggle()    
                bpy.data.objects[self.rig_name].select_set(True)
                bpy.ops.object.posemode_toggle() 
        else:
            rig.hide_viewport=True
            # self.vis = False

        return {'FINISHED'}
#-----------------------------------------------------------------
        ### LINK RIG
class CHUI_OT_link_rig(bpy.types.Operator): 
    bl_label = "Link/Unlink Secondary Armature"
    bl_idname = "chui.link_rig"
    bl_description = "Link this Armature to the Active. It will appear like a Bone Layer"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(self, context):
        return getattr(context.active_object, 'type', False) == 'ARMATURE'
    
    rig_name : StringProperty ()
    # rig : PointerProperty(name = 'point_to_rig', type= CHUI_Data)

    def execute(self, context):
        ac_ob = context.active_object
        prop_name = f'CHUI_L_{self.rig_name}'
        if ac_ob.data.get(prop_name) == None:
            id_props = ac_ob.data[prop_name] = True
            id_props = ac_ob.data.id_properties_ui(prop_name)
            id_props.update(min = 0, max = 1)
            
            # ac_ob.data[prop_name] = bpy.data.objects[self.rig_name]
        else:
            del ac_ob.data[prop_name]

        

        return {'FINISHED'}

#-----------------------------------------------------------------
        ##   CLEAR RIG DATA
class CHUI_OP_clear_data(bpy.types.Operator): 
    bl_label = "Clear Data"
    bl_idname = "chui.clear_data"
    bl_description = "Clear Secondary Rig Data from Active Object"
    bl_options = {'UNDO'}

    # @classmethod
    # def poll(self, context):
    #     arm = getattr(context.active_object, 'data', None)
    #     return arm
    
    target : StringProperty()
    string : StringProperty()
    

    
    @classmethod
    def poll(self, context):
        return getattr(context.active_object, 'type', False) == 'ARMATURE'
    
        



    def execute(self, context):
        tgt = bpy.data.objects[self.target].data
        check_clear(tgt, self.string, CHUI_OP_other_rigs.rig)
        # CHUI_OP_other_rigs.rig.clear()
        return {'FINISHED'}