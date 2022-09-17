import bpy

from bpy.props import BoolProperty, StringProperty, IntProperty





class CHUI_user_key(bpy.types.PropertyGroup):
    # bone : PointerProperty(type = bpy.types.PoseBone)
       bone : StringProperty(name="Bone",
              description="Later",
              default="Untitled")
       key : StringProperty(name="Key",
              description="Later",
              default="Untitled")
       index : IntProperty()
                  
       # tgt_bone : PointerProperty(type = bpy.types.Bone)

class CHUI_user_key_group(bpy.types.PropertyGroup):

       group_name : StringProperty(name="Group",
              description="Choose a Name for this Property Gruop",
              default="Untitled")

       show_header : BoolProperty(name="Show Header",
              description="Show Icon & Name of the Group in the UI",
              default=True)

       icon : StringProperty(name="Icon",
              description="To Select an Icon for this Group, type the Name uppercase without quotation marks ex: PARTICLE_DATA",
              default="FILE_FOLDER")
       
       show_props : BoolProperty(name="Show/Hide Properties",
              description="",
              default=True)

       compact_ui : BoolProperty(name="Compact UI", description = "If selected the group will hold less space in the UI", default = False)

       keys : bpy.props.CollectionProperty(type=CHUI_user_key)


class CHUI_bones_snappig(bpy.types.PropertyGroup):
       FK_ctrl_first : StringProperty(name="Higher FK in the Chain",
              description="",
              default="")

       IK_ctrl_first : StringProperty(name="Higher IK in the Chain",
              description="",
              default="")
       
       FK_ctrl_second : StringProperty(name="Median FK in the Chain",
              description="",
              default="")
       IK_ctrl_second : StringProperty(name="Median IK in the Chain",
              description="",
              default="")

       FK_ctrl_third : StringProperty(name="Lower FK in the Chain",
              description="",
              default="")
       
       IK_ctrl_third : StringProperty(name="Lower IK in the Chain",
              description="",
              default="")

       IK_controller : StringProperty(name="Controller for IK Chain",
              description="",
              default="")

       IK_pole : StringProperty(name="Pole of IK Chain",
              description="",
              default="")

       limb_name : StringProperty(name="Give a Name for this Limb",
              description="",
              default="")

       

