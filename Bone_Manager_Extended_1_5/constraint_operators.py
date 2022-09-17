import bpy
import re

from .blmfuncs import ShowMessageBox
from math import degrees
from mathutils import *

bpy.types.PoseBone.constraint_active_index = bpy.props.IntProperty(options = {'HIDDEN'})

readonly_attr = ['__doc__', '__module__', '__slots__', 'bl_rna', 'error_location',
                 'error_rotation', 'is_proxy_local', 'is_valid', 'rna_type', 'type']

l_names = ['Left', 'left', 'LEFT', 'L', 'l']
r_names = ['Right', 'right', 'RIGHT', 'R', 'r']


def getPolePos(ikbone, parent):  # Stackexchange : Marco Giordano

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    # Get points to define the plane on which to put the pole target
    # arm = bpy.data.objects[arm_name]
    arm = bpy.context.active_object.data
    ebones = arm.edit_bones
    A = ebones[parent].head
    B = ebones[ikbone].head
    C = ebones[ikbone].tail

    # Vector of chain root (parent.head) to chain tip (ikbone.tail)
    AC = C - A

    # Vector of chain root (parent.head) to constrained bone head (ikbone.head)
    AB = B - A

    # Multiply the two vectors to get the dot product
    dot_prod = AB @ AC

    # Find the point on the vector AC projected from point B
    proj = dot_prod / AC.length

    # Normalize AC vector
    start_end_norm = AC.normalized()

    # Project an arrow from AC projection point to point B (pole vector)
    proj_vec = start_end_norm * proj
    pole_vec = AB - proj_vec

    # Set pole location based chain bones length(average)
    distance = (ebones[parent].length + ebones[ikbone].length) / 2
    final_pole_vec = pole_vec + Vector((distance, distance, distance))

    return final_pole_vec


def signed_angle(vector_u, vector_v, normal):  # Stackexchange Jerryno
    # Normal specifies orientation
    angle = vector_u.angle(vector_v)
    if vector_u.cross(vector_v).angle(normal) < 1:
        angle = -angle

    return angle


def get_pole_angle(parent, ikbone, pole_location):  # Stackexchange : Jerryno
    # Calculates pole angle for 2 bone IK chains
    pole_normal = (ikbone.tail - parent.head).cross(pole_location - parent.head)
    projected_pole_axis = pole_normal.cross(parent.tail - parent.head)
    pole_angle = signed_angle(parent.x_axis, projected_pole_axis, parent.tail - parent.head)

    return pole_angle


def getmirror(side, oside, name):
    # get mirror name from name
    mir_name = name

    for i, value in enumerate(side):
        if value == name:
            mir_name = oside[i]
            break

    return mir_name


def xflip(xname):
    # Flip names
    arm = bpy.context.active_object
    full_mir_prefix = base = full_mir_suffix = number = ""
    l_joined = "|".join(l_names)
    r_joined = "|".join(r_names)

    find_l = r'^((' + l_joined + r')[._\- ])?(.*?)?([._\- ](' + l_joined + r'))?([._\- ]\d+)?$'
    find_r = r'^((' + r_joined + r')[._\- ])?(.*?)?([._\- ](' + r_joined + r'))?([._\- ]\d+)?$'

    l_match = re.match(find_l, xname)
    r_match = re.match(find_r, xname)

    match = l_match if True else r_match

    if match:
        full_prefix = match.group(1) if match.group(1) is not None else ""
        prefix = match.group(2) if match.group(2) is not None else ""
        base = match.group(3) if match.group(3) is not None else ""
        full_suffix = match.group(4) if match.group(4) is not None else ""
        suffix = match.group(5) if match.group(5) is not None else ""
        number = match.group(6) if match.group(6) is not None else ""

        if prefix is not None:
            side = l_names if prefix in l_names else r_names
            oside = l_names if prefix not in l_names else r_names
            mir_prefix = getmirror(side, oside, prefix)
            full_mir_prefix = re.sub(prefix, mir_prefix, full_prefix)

        if suffix is not None:
            side = l_names if suffix in l_names else r_names
            oside = l_names if suffix not in l_names else r_names
            mir_suffix = getmirror(side, oside, suffix)
            full_mir_suffix = re.sub(suffix, mir_suffix, full_suffix)

    mir_name = f'{full_mir_prefix}{base}{full_mir_suffix}{number}'
    # if bone not found return original target
    if arm.pose.bones.get(mir_name) is None:
        ShowMessageBox(("Mirror target not found!",), "Bone Layer Manager", 'ERROR')
        return xname

    return mir_name


class QC_OT_contraint_action(bpy.types.Operator):
    # Call constraint operators by action

    bl_idname = "bone.constraint_action"
    bl_label = ""

    
    action_items=(
        ('UP', "Up", "Move Up (Shift = Move to Top)"),
        ('DOWN', "Down", "Move Down (Shift = Move to Bottom)"),
        ('ADD', "Add", "Add Constraint"),
        ('REMOVE', "Remove", "Remove Active Constraint"),
        ('FOLLOW_PATH', "Follow_Path", ""),
        ('OB_SET_INVERSE', "Ob_Set_Inverse", ""),
        ('OB_CLEAR_INVERSE', "Ob_Clear_Inverse", ""),
        ('LD_RESET', "Ld_Reset", ""),
        ('STRETCH_RESET', "Stretch_reset", ""),
        ('ADD_TARGET', "Add_Target", ""),
        ('REMOVE_TARGET', "Remove_Target", ""),
        ('NORMALIZE_TARGET', "Normalize_Target", ""),
        ('CO_SET_INVERSE', "Co_Set_Inverse", ""),
        ('CO_CLEAR_INVERSE', "Co_Set_Inverse", ""),
    )

    action: bpy.props.EnumProperty(items = action_items)

    @classmethod
    def description(cls, context, properties):
        items = {id: desc for id, name, *desc, in cls.action_items}
        desc = items[properties.action][0]
        return desc

    @classmethod
    def poll(cls, context):
        return context.selected_pose_bones

    def invoke(self, context, event):
        bone = context.active_pose_bone
        idx = bone.constraint_active_index
        con_count = len(bone.constraints)

        if con_count > 0:
            con = bone.constraints[idx]
            name = con.name
            # set the constraint in the context
            context_py = context.copy()
            context_py["constraint"] = con
        else:
            bone.constraint_active_index = 0

        # general move\add\remove operators
        if self.action == 'DOWN' and idx < con_count - 1 and not event.shift:
            if bpy.ops.constraint.move_down(context_py, constraint=name, owner='BONE') == {'FINISHED'}:
                bone.constraint_active_index += 1
        if self.action == 'DOWN' and idx < con_count - 1 and event.shift and bpy.app.version > (2, 9, 1):
            if bpy.ops.constraint.move_to_index(context_py, constraint=name, owner='BONE', index=con_count-1) == {'FINISHED'}:
                bone.constraint_active_index = con_count-1
        elif self.action == 'UP' and idx > 0 and not event.shift:
            if bpy.ops.constraint.move_up(context_py, constraint=name, owner='BONE') == {'FINISHED'}:
                bone.constraint_active_index -= 1
        elif self.action == 'UP' and idx > 0 and event.shift and bpy.app.version > (2, 9, 1):
            if bpy.ops.constraint.move_to_index(context_py, constraint=name, owner='BONE', index=0) == {'FINISHED'}:
                bone.constraint_active_index = 0
        elif self.action == 'ADD':
            bpy.ops.qconstraint.popup('INVOKE_DEFAULT')
        elif self.action == 'REMOVE' and con_count > 0:
            bone.constraints.remove(con)
            if idx > 0:
                bone.constraint_active_index -= 1
            # remove active index property if exists and not in use
            if con_count == 1 and bone.get('constraint_active_index') is not None:
                del bone["constraint_active_index"]

        # contraint specific operators
        # FOLLOW PATH
        elif self.action == 'FOLLOW_PATH':
            bpy.ops.constraint.followpath_path_animate(context_py, constraint=name, owner='BONE', frame_start=1, length=100)
        # OBJECT SOLVER
        elif self.action == 'OB_SET_INVERSE':
            bpy.ops.constraint.objectsolver_set_inverse(context_py, constraint=name, owner='BONE')
        elif self.action == 'OB_CLEAR_INVERSE':
            bpy.ops.constraint.objectsolver_clear_inverse(context_py, constraint=name, owner='BONE')
        # LIMIT DISTANCE
        elif self.action == 'LD_RESET':
            bpy.ops.constraint.limitdistance_reset(context_py, constraint=name, owner='BONE')
        # STRETCH TO
        elif self.action == 'STRETCH_RESET':
            bpy.ops.constraint.stretchto_reset(context_py, constraint=name, owner='BONE')
        # ARMATURE
        elif self.action == 'ADD_TARGET':
            bpy.ops.constraint.add_target(context_py)
        elif self.action == 'REMOVE_TARGET':
            bpy.ops.constraint.remove_target(context_py)
        elif self.action == 'NORMALIZE_TARGET':
            bpy.ops.constraint.normalize_target_weights(context_py)
        # CHILD OF
        elif self.action == 'CO_SET_INVERSE':
            bpy.ops.constraint.childof_set_inverse(context_py, constraint=name, owner='BONE')
        elif self.action == 'CO_CLEAR_INVERSE':
            bpy.ops.constraint.childof_clear_inverse(context_py, constraint=name, owner='BONE')

        return {"FINISHED"}


class QC_OT_constraint_add(bpy.types.Operator):
    # Add constraint to active bone
    bl_idname = "qconstraint.constraint_add"
    bl_label = "Add Constraint"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Add Constraint to Active Bone"

    ctype: bpy.props.StringProperty(options = {'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        bone = context.active_pose_bone
        if len(context.selected_pose_bones) > 1:
            bpy.ops.pose.constraint_add_with_targets(type=self.ctype)
        else:
            bpy.ops.pose.constraint_add(type=self.ctype)
        # Redraw required to update QC_UL_conlist
        for region in context.area.regions:
            if region.type == "UI":
                region.tag_redraw()
        # Add index if not present
        if bone.get('constraint_active_index') is None:
            bone.constraint_active_index = 0

        return {'FINISHED'}


class QC_OT_constraint_clear(bpy.types.Operator):
    # Clear all contraints
    bl_idname = "qconstraint.constraint_clear"
    bl_label = "Clear All Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear all constraints for the selected bones"

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        if bone:
            return len(bone.constraints) > 0 and len(context.selected_pose_bones) > 0
        else:
            return None

    def execute(self, context):
        bpy.ops.pose.constraints_clear('INVOKE_DEFAULT')
        # Redraw required to update QC_UL_conlist
        for region in context.area.regions:
            if region.type == "UI":
                region.tag_redraw()

        # remove index property from all bones
        for bone in context.selected_pose_bones:
            if bone.get('constraint_active_index') is not None:
                del bone["constraint_active_index"]

        return {'FINISHED'}


class QC_OT_add_target(bpy.types.Operator):
    """Add a target to the constraint"""
    bl_idname = "qconstraint.add_target"
    bl_label = "Add Target"
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        bone = context.active_pose_bone
        idx = bone.constraint_active_index
        constraint = bone.constraints[idx]
        constraint.targets.new()
        return {'FINISHED'}


class QC_OT_remove_target(bpy.types.Operator):
    # Remove the target from the constraint
    bl_idname = "qconstraint.remove_target"
    bl_label = "Remove Target"
    bl_options = {'UNDO', 'INTERNAL'}
    bl_description = "Remove the target from the constraint"

    index: bpy.props.IntProperty()

    def execute(self, context):
        bone = context.active_pose_bone
        idx = bone.constraint_active_index
        constraint = bone.constraints[idx]
        tgts = constraint.targets
        tgts.remove(tgts[self.index])
        return {'FINISHED'}


class QC_OT_normalize_target_weights(bpy.types.Operator):
    """Normalize weights of all target bones"""
    bl_idname = "qconstraint.normalize_target_weights"
    bl_label = "Normalize Weights"
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        bone = context.active_pose_bone
        idx = bone.constraint_active_index
        constraint = bone.constraints[idx]
        tgts = constraint.targets
        total = sum(t.weight for t in tgts)

        if total > 0:
            for t in tgts:
                t.weight = t.weight / total

        return {'FINISHED'}


class QC_OT_disable_keep_transform(bpy.types.Operator):
    """Set the influence of this constraint to zero while """
    """trying to maintain the object's transformation. Other active """
    """constraints can still influence the final transformation"""

    bl_idname = "qconstraint.disable_keep_transform"
    bl_label = "Disable and Keep Transform"
    bl_options = {'UNDO', 'INTERNAL'}
    bl_description = "Disable constraint while maintaining the visual transform."

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        idx = bone.constraint_active_index
        constraint = bone.constraints[idx]

        return constraint and constraint.influence > 0.0

    def execute(self, context):
        bone = context.active_pose_bone
        idx = bone.constraint_active_index
        constraint = bone.constraints[idx]

        is_bone_constraint = True
        ob = context.object
        mat = ob.matrix_world @ bone.matrix
        constraint.influence = 0.0
        bone.matrix = ob.matrix_world.inverted() @ mat

        return {'FINISHED'}


class QC_OT_copyconstraint(bpy.types.Operator):
    # Copy active constraint to selected bones
    bl_idname = "qconstraint.copy"
    bl_label = ""
    bl_description = "Copy active constraint to selected bones"

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        if bone:
            return len(bone.constraints) > 0 and len(context.selected_pose_bones) > 1
        else:
            return None

    def execute(self, context):

        source_bone = context.active_pose_bone
        idx = source_bone.constraint_active_index
        source_con = source_bone.constraints[idx]
        selected = context.selected_pose_bones[:]
        selected.remove(source_bone)
        string = ""

        for target_bone in selected:
            target = target_bone.constraints.new(source_con.type)

            # assign property if required
            if len(target_bone.constraints) == 1:
                target_bone.constraint_active_index = 0

            for attr in dir(source_con):
                if attr.find(string) != -1 and attr not in readonly_attr:
                    setattr(target, attr, getattr(source_con, attr))

        return {'FINISHED'}


class QC_OT_copyflipx(bpy.types.Operator):
    # Copy active constraint to selected bones (flip x subtarget name)
    bl_idname = "qconstraint.xflipcopy"
    bl_label = ""
    bl_description = "Copy active constraint to selected bones (X axis flip)"

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        if bone:
            return len(bone.constraints) > 0 and len(context.selected_pose_bones) > 1
        else:
            return None

    def execute(self, context):

        source_bone = context.active_pose_bone
        idx = source_bone.constraint_active_index
        source_con = source_bone.constraints[idx]
        selected = context.selected_pose_bones[:]
        selected.remove(source_bone)
        string = ""

        for target_bone in selected:
            target = target_bone.constraints.new(source_con.type)

            # assign property if required
            if len(target_bone.constraints) == 1:
                target_bone.constraint_active_index = 0

            for attr in dir(source_con):
                if attr.find(string) != -1 and attr not in readonly_attr:
                    if attr == "subtarget":
                        xname = getattr(source_con, attr)
                        setattr(target, attr, xflip(xname))
                    else:
                        setattr(target, attr, getattr(source_con, attr))
                    # print(f'{attr} Copied')

        return {'FINISHED'}


class QC_OT_copyall(bpy.types.Operator):
    # Copy active constraint to selected bones
    bl_idname = "qconstraint.copyall"
    bl_label = ""
    bl_description = "Copy all constraints to selected bones"

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        if bone:
            return len(bone.constraints) > 0 and len(context.selected_pose_bones) > 1
        else:
            return None

    def execute(self, context):

        source_bone = context.active_pose_bone
        idx = source_bone.constraint_active_index
        selected = context.selected_pose_bones[:]
        selected.remove(source_bone)

        for target_bone in selected:
            # assign property if required
            if len(target_bone.constraints) == 0:
                target_bone.constraint_active_index = 0

        bpy.ops.pose.constraints_copy('INVOKE_DEFAULT')

        return {'FINISHED'}


class QC_OT_autopole(bpy.types.Operator):
    # set pole target locatation and pole angle in contraint
    bl_idname = "qconstraint.autopole"
    bl_label = ""
    bl_description = "Automatic pole target location and pole angle"

    @classmethod
    def poll(self, context):
        # only supports chains of length 2        ########## NOTE: Added try exept
        try:
            cbone = context.active_pose_bone
            idx = cbone.constraint_active_index
            con = cbone.constraints[idx]
            pole_target = con.pole_subtarget

            return pole_target != "" and con.chain_count == 2
        except (AttributeError):
            print ("constraint_operators")
            print ("line 505")
            return False

    def execute(self, context):
        arm = bpy.context.active_object
        cbone = context.active_pose_bone
        ikbone = cbone.name
        parent = cbone.parent.name
        idx = cbone.constraint_active_index
        con = cbone.constraints[idx]
        pole_target = con.pole_subtarget

        # clear transforms and IK influence during calcultions
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for pbones in arm.pose.bones:
            pbones.matrix_basis = Matrix()

        con.influence = 0

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        ebones = arm.data.edit_bones
        pole_position = getPolePos(ikbone, parent)
        length = ebones[pole_target].length
        ebones[pole_target].head = pole_position
        ebones[pole_target].tail = pole_position + Vector((0.0, length, 0.0))

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        parent = arm.pose.bones[parent]
        ikbone = arm.pose.bones[ikbone]
        pole_target = arm.pose.bones[pole_target]

        pole_location = pole_target.matrix.translation
        con.pole_angle = get_pole_angle(parent, ikbone, pole_location)
        con.influence = 1

        return {'FINISHED'}
