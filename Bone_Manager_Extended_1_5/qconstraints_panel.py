import bpy
import bpy.ops

from bl_ui.properties_constraint import ConstraintButtonsPanel

bpy.types.PoseBone.constraint_active_index = bpy.props.IntProperty()

con_icons = {con.identifier: con.icon for con in bpy.types.Constraint.bl_rna.properties['type'].enum_items}

has_notarget = ['OBJECT_SOLVER', 'CAMERA_SOLVER', 'FOLLOW_TRACK',
                'LIMIT_LOCATION', 'LIMIT_ROTATION', 'LIMIT_SCALE',
                'MAINTAIN_VOLUME', 'TRANSFORM_CACHE', 'ARMATURE'
                ]

list_count = 0


def constraint_alert(con):
    # Constraint error check

    if con.type not in has_notarget:
        con_target = getattr(con, "target", None)

        if not con_target:
            return False

        elif con_target.type == 'ARMATURE':
            return con.subtarget != ""

    return True


class QC_MT_specials(bpy.types.Menu):
    # Constraints specials menu
    bl_label = "Constraint Specials"

    def draw(self, context):
        layout = self.layout
        layout.operator("qconstraint.copy", icon='DUPLICATE', text="Copy constraint to selected")
        # TODO
        layout.operator("qconstraint.xflipcopy", icon='DUPLICATE', text="Copy constraint to selected (X axis flip)")
        layout.separator()
        layout.operator("qconstraint.copyall", icon='DUPLICATE', text="Copy all constraints to selected")
        layout.separator()
        layout.operator("qconstraint.constraint_clear", icon='PANEL_CLOSE', text="Clear all constraints")


class QC_MT_popup(bpy.types.Menu):
    # Add Constraint Menu (Required for UIList redraw/update)
    bl_idname = "QC_MT_popup"
    bl_label = ""
    bl_description = "Add Constraint"

    def draw(self, context):
        layout = self.layout
        layout.ui_units_x = 27
        row = layout.row(align=True)
        split = row.split(align=True, factor=0.25)

        args = dict(operator='qconstraint.constraint_add')

        # MotionTracking
        col = split.column()
        col.label(text="Motion Tracking")
        col.separator()
        col.operator(**args, text="Camera Solver", icon='CON_CAMERASOLVER').ctype = 'CAMERA_SOLVER'
        col.operator(**args, text="Follow Track", icon='CON_FOLLOWTRACK').ctype = 'FOLLOW_TRACK'
        col.operator(**args, text="Object Solver", icon='CON_OBJECTSOLVER').ctype = 'OBJECT_SOLVER'

        # Transform
        col = split.column()
        col.label(text="Transform")
        col.separator()
        col.operator(**args, text="Copy Location", icon='CON_LOCLIKE').ctype = 'COPY_LOCATION'
        col.operator(**args, text="Copy Rotation", icon='CON_ROTLIKE').ctype = 'COPY_ROTATION'
        col.operator(**args, text="Copy Scale", icon='CON_SIZELIKE').ctype = 'COPY_SCALE'
        col.operator(**args, text="Copy Transforms", icon='CON_TRANSLIKE').ctype = 'COPY_TRANSFORMS'
        col.operator(**args, text="Limit Distance", icon='CON_DISTLIMIT').ctype = 'LIMIT_DISTANCE'
        col.operator(**args, text="Limit Location", icon='CON_LOCLIMIT').ctype = 'LIMIT_LOCATION'
        col.operator(**args, text="Limit Rotation", icon='CON_ROTLIMIT').ctype = 'LIMIT_ROTATION'
        col.operator(**args, text="Limit Scale", icon='CON_SIZELIMIT').ctype = 'LIMIT_SCALE'
        col.operator(**args, text="Maintain Volume", icon='CON_SAMEVOL').ctype = 'MAINTAIN_VOLUME'
        col.operator(**args, text="Transformation", icon='CON_TRANSFORM').ctype = 'TRANSFORM'
        col.operator(**args, text="Transform Cache", icon='CON_TRANSFORM_CACHE').ctype = 'TRANSFORM_CACHE'

        # Tracking
        col = split.column()
        col.label(text="Tracking")
        col.separator()
        col.operator(**args, text="Clamp To", icon='CON_CLAMPTO').ctype = 'CLAMP_TO'
        col.operator(**args, text="Damped Track", icon='CON_TRACKTO').ctype = 'DAMPED_TRACK'
        col.operator(**args, text="Inverse Kinemarics", icon='CON_KINEMATIC').ctype = 'IK'
        col.operator(**args, text="Locked Track", icon='CON_LOCKTRACK').ctype = 'LOCKED_TRACK'
        col.operator(**args, text="Spline IK", icon='CON_SPLINEIK').ctype = 'SPLINE_IK'
        col.operator(**args, text="Stretch To", icon='CON_STRETCHTO').ctype = 'STRETCH_TO'
        col.operator(**args, text="Track To", icon='CON_TRACKTO').ctype = 'TRACK_TO'

        # Relationship
        col = split.column()
        col.label(text="Relationship")
        col.separator()
        col.operator(**args, text="Action", icon='ACTION').ctype = 'ACTION'
        col.operator(**args, text="Armature", icon='CON_ARMATURE').ctype = 'ARMATURE'
        col.operator(**args, text="Child Of", icon='CON_CHILDOF').ctype = 'CHILD_OF'
        col.operator(**args, text="Floor", icon='CON_FLOOR').ctype = 'FLOOR'
        col.operator(**args, text="Follow Path", icon='CON_FOLLOWPATH').ctype = 'FOLLOW_PATH'
        col.operator(**args, text="Pivot", icon='CON_PIVOT').ctype = 'PIVOT'
        col.operator(**args, text="Shrinkwrap", icon='CON_SHRINKWRAP').ctype = 'SHRINKWRAP'


class QC_PT_qcontraints(bpy.types.Panel):
    # Main Quick Constraints Panel
    bl_category = "Bone Layers"
    bl_label = "Quick Constraints"
    bl_idname = "QC_PT_qcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None) is not None:
            return context.mode == 'POSE'

    def draw(self, context):
        layout = self.layout


class QC_PT_subqcontraints(bpy.types.Panel):
    # Sub Quick Constraints Panel
    bl_category = "Bone Layers"
    bl_parent_id = "QC_PT_qcontraints"
    bl_label = ""
    bl_idname = "QC_PT_subqcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(self, context):
        return context.active_pose_bone is not None

    def draw(self, context):
        bone = context.active_pose_bone
        layout = self.layout
        row = layout.row()
        row.template_list("QC_UL_conlist", "", bone, "constraints",
                          bone, "constraint_active_index", rows=5,
                          sort_reverse=False)

        col = row.column(align=True)
        # draw menu or operator as placemarker (disabled by polling)
        if context.selected_pose_bones:
            sub = col.column(align=True)
            sub.menu("QC_MT_popup", icon='ADD', text="")
        else:
            col.operator("bone.constraint_action", icon='ADD', text="").action = 'ADD'

        col.operator("bone.constraint_action", icon='REMOVE', text="").action = 'REMOVE'
        col.separator()

        # conditional draw
        if context.selected_pose_bones:
            sub2 = col.column(align=True)
            sub2.menu("QC_MT_specials", icon='DOWNARROW_HLT', text="")
            col.separator()

            if len(bone.constraints) > 1:
                col.operator("bone.constraint_action", icon='TRIA_UP', text="").action = 'UP'
                col.operator("bone.constraint_action", icon='TRIA_DOWN', text="").action = 'DOWN'
                col.separator()


class QC_UL_conlist(bpy.types.UIList):
    # Quick Constraints UIList template
    def draw_item(self, context, layout, data, item, active_data, active_propname, index):

        bone = context.active_pose_bone

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            self.use_filter_show = False
            global list_count
            list_count += 1
            row = layout.split(factor=0.8)
            row.prop(item, "name", text="", emboss=False, icon=con_icons[item.type])
            row = layout.row(align=True)
            icon = 'BLANK1' if constraint_alert(item) else 'ERROR'
            row.label(text="", icon=icon)
            row = layout.row(align=True)
            # Blender 2.81 api change (causing wrong icon to be shown)
            if bpy.app.version >= (2, 81, 0):
                row.prop(item, "mute", text="", icon='HIDE_OFF', emboss=False)

            else:
                icon = 'HIDE_OFF' if not item.mute else 'HIDE_ON'
                row.prop(item, "mute", text="", icon=icon, emboss=False)


class QC_PT_ConSettings(bpy.types.Panel):
    # Contraint Settings Panel
    bl_label = ""
    bl_idname = "QC_PT_ConSettings"
    bl_context = "constraint"
    bl_category = "Bone Layers"
    bl_parent_id = "QC_PT_qcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {"HIDE_HEADER"}

    @staticmethod
    def draw_influence(layout, con):
        layout.separator()
        if con.type in {'IK', 'SPLINE_IK'}:
            # constraint.disable_keep_transform doesn't work well
            # for these constraints.
            layout.prop(con, "influence")
        else:
            row = layout.row(align=True)
            row.prop(con, "influence")
            row.operator("qconstraint.disable_keep_transform", text="", icon='CANCEL')

    @staticmethod
    def target_template(layout, con, subtargets=True):
        col = layout.column()
        col.prop(con, "target")  # XXX limiting settings for only 'curves' or some type of object

        if con.target and subtargets:
            if con.target.type == 'ARMATURE':
                col.prop_search(con, "subtarget", con.target.data, "bones", text="Bone")

                if con.subtarget and hasattr(con, "head_tail"):
                    row = col.row(align=True)
                    row.use_property_decorate = False
                    sub = row.row(align=True)
                    sub.prop(con, "head_tail")
                    # XXX icon, and only when bone has segments?
                    sub.prop(con, "use_bbone_shape", text="", icon='IPO_BEZIER')
                    if bpy.app.version >= (2, 90, 0):
                        row.prop_decorator(con, "head_tail")
            elif con.target.type in {'MESH', 'LATTICE'}:
                col.prop_search(con, "subtarget", con.target, "vertex_groups", text="Vertex Group")

    @staticmethod
    def space_template(layout, con, target=True, owner=True):
        if target or owner:
            layout.separator()
            if target:
                layout.prop(con, "target_space", text="Target")
            if owner:
                layout.prop(con, "owner_space", text="Owner")

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None) is not None:
            return context.active_pose_bone is not None

    def draw(self, context):
        layout = self.layout
        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)

        if bone and bone.constraints:
            const = bone.constraints[idx]
            label = const.name + " :"

            for con in bone.constraints:

                if con.name == const.name:

                    # layout = self.layout.box()
                    layout = self.layout

                    if con.type == 'CAMERA_SOLVER':

                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        layout.prop(con, "use_active_clip")

                        if not con.use_active_clip:
                            layout.prop(con, "clip")

                        layout.operator("clip.constraint_to_fcurve")

                        self.draw_influence(layout, con)

                    elif con.type == 'FOLLOW_TRACK':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        clip = None
                        if con.use_active_clip:
                            clip = context.scene.active_clip
                        else:
                            clip = con.clip

                        layout.prop(con, "use_active_clip")
                        layout.prop(con, "use_3d_position")

                        row = layout.row()
                        row.active = not con.use_3d_position
                        row.prop(con, "use_undistorted_position")

                        if not con.use_active_clip:
                            layout.prop(con, "clip")

                        layout.prop(con, "frame_method")

                        if clip:
                            tracking = clip.tracking

                            layout.prop_search(con, "object", tracking, "objects", icon='OBJECT_DATA')

                            tracking_object = tracking.objects.get(con.object, tracking.objects[0])

                            layout.prop_search(con, "track", tracking_object, "tracks", icon='ANIM_DATA')

                        layout.prop(con, "camera")

                        row = layout.row()
                        row.active = not con.use_3d_position
                        row.prop(con, "depth_object")

                        layout.operator("clip.constraint_to_fcurve")

                        self.draw_influence(layout, con)

                    elif con.type == 'OBJECT_SOLVER':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        clip = None
                        if con.use_active_clip:
                            clip = context.scene.active_clip
                        else:
                            clip = con.clip

                        layout.prop(con, "use_active_clip")

                        if not con.use_active_clip:
                            layout.prop(con, "clip")

                        if clip:
                            layout.prop_search(con, "object", clip.tracking, "objects", icon='OBJECT_DATA')

                        layout.prop(con, "camera")

                        row = layout.row()
                        row.operator("bone.constraint_action", text="Set Inverse").action = 'OB_SET_INVERSE'
                        row.operator("bone.constraint_action", text="Clear Inverse").action = 'OB_CLEAR_INVERSE'

                        layout.operator("clip.constraint_to_fcurve")

                        self.draw_influence(layout, con)

                    elif con.type == 'COPY_LOCATION':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Axis", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Axis")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_x", text="X", toggle=True)
                        sub.prop(con, "use_y", text="Y", toggle=True)
                        sub.prop(con, "use_z", text="Z", toggle=True)
                        row.label(icon='BLANK1')

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Invert", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Invert")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "invert_x", text="X", toggle=True)
                        sub.prop(con, "invert_y", text="Y", toggle=True)
                        sub.prop(con, "invert_z", text="Z", toggle=True)
                        row.label(icon='BLANK1')

                        layout.prop(con, "use_offset")

                        self.space_template(layout, con)

                        self.draw_influence(layout, con)

                    elif con.type == 'COPY_ROTATION':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        layout.prop(con, "euler_order", text="Order")

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Axis", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Axis")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_x", text="X", toggle=True)
                        sub.prop(con, "use_y", text="Y", toggle=True)
                        sub.prop(con, "use_z", text="Z", toggle=True)
                        row.label(icon='BLANK1')

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Invert", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Invert")

                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "invert_x", text="X", toggle=True)
                        sub.prop(con, "invert_y", text="Y", toggle=True)
                        sub.prop(con, "invert_z", text="Z", toggle=True)
                        row.label(icon='BLANK1')

                        layout.prop(con, "mix_mode", text="Mix")

                        self.space_template(layout, con)

                        self.draw_influence(layout, con)

                    elif con.type == 'COPY_SCALE':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Axis", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Axis")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_x", text="X", toggle=True)
                        sub.prop(con, "use_y", text="Y", toggle=True)
                        sub.prop(con, "use_z", text="Z", toggle=True)
                        row.label(icon='BLANK1')

                        col = layout.column()
                        col.prop(con, "power")
                        col.prop(con, "use_make_uniform")

                        col.prop(con, "use_offset")
                        row = col.row()
                        row.active = con.use_offset
                        row.prop(con, "use_add")

                        self.space_template(layout, con)

                        self.draw_influence(layout, con)

                    elif con.type == 'COPY_TRANSFORMS':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        layout.prop(con, "mix_mode", text="Mix")

                        self.space_template(layout, con)

                        self.draw_influence(layout, con)

                    elif con.type == 'LIMIT_DISTANCE':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        row = layout.row()
                        row.prop(con, "distance")
                        row.operator("bone.constraint_action", text="", icon="X").action = 'LD_RESET'

                        layout.prop(con, "limit_mode", text="Clamp Region")

                        layout.prop(con, "use_transform_limit")

                        self.space_template(layout, con)

                        self.draw_influence(layout, con)

                    elif con.type == 'LIMIT_LOCATION':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        col = layout.column()

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Minimum X", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Minimum X")

                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_min_x", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_min_x
                        subsub.prop(con, "min_x", text="")

                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "min_x")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Y", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Minimum Y")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_min_y", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_min_y
                        subsub.prop(con, "min_y", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "min_y")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Z", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Minimum Z")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_min_z", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_min_z
                        subsub.prop(con, "min_z", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "min_z")

                        col.separator()

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Maximum X", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Maximum X")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_max_x", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_max_x
                        subsub.prop(con, "max_x", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "max_x")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Y", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Maximum Y")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_max_y", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_max_y
                        subsub.prop(con, "max_y", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "max_y")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Z", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Maximum Z")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_max_z", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_max_z
                        subsub.prop(con, "max_z", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "max_z")

                        layout.prop(con, "use_transform_limit")
                        layout.prop(con, "owner_space")

                        self.draw_influence(layout, con)

                    elif con.type == 'LIMIT_ROTATION':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        # Decorators and property split are really buggy with these properties
                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Limit X", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Limit X")

                        row.use_property_decorate = False
                        row.prop(con, "use_limit_x", text="")
                        sub = row.column(align=True)
                        sub.active = con.use_limit_x
                        sub.prop(con, "min_x", text="Min")
                        sub.prop(con, "max_x", text="Max")
                        row.label(icon="BLANK1")

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Y", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Limit Y")

                        row.use_property_decorate = False
                        row.prop(con, "use_limit_y", text="")
                        sub = row.column(align=True)
                        sub.active = con.use_limit_y
                        sub.prop(con, "min_y", text="Min")
                        sub.prop(con, "max_y", text="Max")
                        row.label(icon="BLANK1")

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Z", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Limit Z")

                        row.use_property_decorate = False
                        row.prop(con, "use_limit_z", text="")
                        sub = row.column(align=True)
                        sub.active = con.use_limit_z
                        sub.prop(con, "min_z", text="Min")
                        sub.prop(con, "max_z", text="Max")
                        row.label(icon="BLANK1")

                        layout.prop(con, "use_transform_limit")
                        layout.prop(con, "owner_space")

                        self.draw_influence(layout, con)

                    elif con.type == 'LIMIT_SCALE':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        col = layout.column()

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Minimum X", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Minimum X")

                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_min_x", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_min_x
                        subsub.prop(con, "min_x", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "min_x")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Y", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Minimum Y")

                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_min_y", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_min_y
                        subsub.prop(con, "min_y", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "min_y")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Z", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Minimum Z")

                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_min_z", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_min_z
                        subsub.prop(con, "min_z", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "min_z")

                        col.separator()

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Maximum X", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Maximum X")

                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_max_x", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_max_x
                        subsub.prop(con, "max_x", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "max_x")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Y", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Maximum Y")

                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_max_y", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_max_y
                        subsub.prop(con, "max_y", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "max_y")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Z", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Maximum Z")

                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_max_z", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_max_z
                        subsub.prop(con, "max_z", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "max_z")

                        layout.prop(con, "use_transform_limit")
                        layout.prop(con, "owner_space")

                        self.draw_influence(layout, con)

                    elif con.type == 'MAINTAIN_VOLUME':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        layout.prop(con, "mode")

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Free Axis", align=True)
                        else:
                            row = layout.row(align=True)
                            # row.label(text="Free Axis")

                        row.prop(con, "free_axis", expand=True)

                        layout.prop(con, "volume")

                        layout.prop(con, "owner_space")

                        self.draw_influence(layout, con)

                    elif con.type == 'TRANSFORM':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        layout.prop(con, "use_motion_extrapolate", text="Extrapolate")

                        self.space_template(layout, con)

                        self.draw_influence(layout, con)

                    elif con.type == 'TRANSFORM_CACHE':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        layout.template_cache_file(con, "cache_file")

                        cache_file = con.cache_file

                        if cache_file is not None:
                            layout.prop_search(con, "object_path", cache_file, "object_paths")

                        self.draw_influence(layout, con)

                    elif con.type == 'CLAMP_TO':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        layout.prop(con, "main_axis", expand=True)

                        layout.prop(con, "use_cyclic")

                        self.draw_influence(layout, con)

                    elif con.type == 'DAMPED_TRACK':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        layout.prop(con, "track_axis", expand=True)

                        self.draw_influence(layout, con)

                    elif con.type == 'IK':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        if context.object.pose.ik_solver == 'ITASC':
                            layout.prop(con, "ik_type")

                            # This button gives itself too much padding, so put it in a column with the subtarget
                            col = layout.column()
                            col.prop(con, "pole_target")

                            if con.pole_target and con.pole_target.type == 'ARMATURE':
                                col.prop_search(con, "pole_subtarget", con.pole_target.data, "bones", text="Bone")

                            col = layout.column()
                            if con.pole_target:
                                col.prop(con, "pole_angle")
                            col.prop(con, "use_tail")
                            col.prop(con, "use_stretch")
                            col.prop(con, "chain_count")

                            if con.ik_type == 'COPY_POSE':
                                layout.prop(con, "reference_axis", expand=True)

                                # Use separate rows and columns here to avoid an alignment issue with the lock buttons
                                loc_col = layout.column()
                                loc_col.prop(con, "use_location")

                                row = loc_col.row()
                                row.active = con.use_location
                                row.prop(con, "weight", text="Weight", slider=True)

                                if bpy.app.version >= (2, 90, 0):
                                    row = loc_col.row(heading="Lock", align=True)
                                else:
                                    row = loc_col.row(align=True)
                                    row.label(text="Lock")

                                row.use_property_decorate = False
                                row.active = con.use_location
                                sub = row.row(align=True)
                                sub.prop(con, "lock_location_x", text="X", toggle=True)
                                sub.prop(con, "lock_location_y", text="Y", toggle=True)
                                sub.prop(con, "lock_location_z", text="Z", toggle=True)
                                row.label(icon='BLANK1')

                                rot_col = layout.column()
                                rot_col.prop(con, "use_rotation")

                                row = rot_col.row()
                                row.active = con.use_rotation
                                row.prop(con, "orient_weight", text="Weight", slider=True)

                                if bpy.app.version >= (2, 90, 0):
                                    row = rot_col.row(heading="Lock", align=True)
                                else:
                                    row = rot_col.row(align=True)
                                    row.label(text="Lock")

                                row.use_property_decorate = False
                                row.active = con.use_rotation
                                sub = row.row(align=True)
                                sub.prop(con, "lock_rotation_x", text="X", toggle=True)
                                sub.prop(con, "lock_rotation_y", text="Y", toggle=True)
                                sub.prop(con, "lock_rotation_z", text="Z", toggle=True)
                                row.label(icon='BLANK1')

                            elif con.ik_type == 'DISTANCE':
                                layout.prop(con, "limit_mode")

                                col = layout.column()
                                col.prop(con, "weight", text="Weight", slider=True)
                                col.prop(con, "distance", text="Distance", slider=True)
                        else:
                            # Standard IK constraint
                            col = layout.column()
                            col.prop(con, "pole_target")

                            if con.pole_target and con.pole_target.type == 'ARMATURE':
                                col.prop_search(con, "pole_subtarget", con.pole_target.data, "bones", text="Bone")

                            col = layout.column()
                            if con.pole_target:
                                col.prop(con, "pole_angle")
                            col.prop(con, "iterations")
                            col.prop(con, "chain_count")
                            col.prop(con, "use_tail")
                            col.prop(con, "use_stretch")

                            col = layout.column()
                            if bpy.app.version >= (2, 90, 0):
                                row = col.row(heading="Weight Position", align=True)
                            else:
                                row = col.row(align=True)
                                row.label(text="Weight Position")

                            row.prop(con, "use_location", text="")
                            sub = row.row(align=True)
                            sub.active = con.use_location
                            sub.prop(con, "weight", text="", slider=True)

                            if bpy.app.version >= (2, 90, 0):
                                row = col.row(heading="Rotation", align=True)
                            else:
                                row = col.row(align=True)
                                row.label(text="Rotation")
                            row.prop(con, "use_rotation", text="")
                            sub = row.row(align=True)
                            sub.active = con.use_rotation
                            sub.prop(con, "orient_weight", text="", slider=True)

                        self.draw_influence(layout, con)

                    elif con.type == 'LOCKED_TRACK':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        layout.prop(con, "track_axis", expand=True)
                        layout.prop(con, "lock_axis", expand=True)

                        self.draw_influence(layout, con)

                    elif con.type == 'SPLINE_IK':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        self.draw_influence(layout, con)

                    elif con.type == 'TRACK_TO':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        layout.prop(con, "track_axis", expand=True)
                        layout.prop(con, "up_axis", text="Up", expand=True)
                        layout.prop(con, "use_target_z")

                        self.space_template(layout, con)

                        self.draw_influence(layout, con)

                    elif con.type == 'STRETCH_TO':
                        if bpy.app.version >= (2, 90, 0):
                            layout.use_property_split = True
                            layout.use_property_decorate = True
                        self.target_template(layout, con)

                        row = layout.row()
                        if bpy.app.version >= (2, 90, 0):
                            row.prop(con, "rest_length")
                        else:
                            row.prop(con, "rest_length", text="Rest Length")
                        # row.operator("constraint.stretchto_reset", text="", icon="X")
                        row.operator("bone.constraint_action", text="", icon="X").action = 'STRETCH_RESET'

                        layout.separator()

                        col = layout.column()
                        col.prop(con, "bulge", text="Volume Variation")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Volume Min", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Volume Min")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_bulge_min", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_bulge_min
                        subsub.prop(con, "bulge_min", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "bulge_min")

                        if bpy.app.version >= (2, 90, 0):
                            row = col.row(heading="Max", align=True)
                        else:
                            row = col.row(align=True)
                            row.label(text="Max")
                        row.use_property_decorate = False
                        sub = row.row(align=True)
                        sub.prop(con, "use_bulge_max", text="")
                        subsub = sub.row(align=True)
                        subsub.active = con.use_bulge_max
                        subsub.prop(con, "bulge_max", text="")
                        if bpy.app.version >= (2, 90, 0):
                            row.prop_decorator(con, "bulge_max")

                        row = col.row()
                        row.active = con.use_bulge_min or con.use_bulge_max
                        row.prop(con, "bulge_smooth", text="Smooth")

                        layout.prop(con, "volume", expand=True)
                        layout.prop(con, "keep_axis", text="Rotation", expand=True)

                        self.draw_influence(layout, con)

                    elif con.type == 'ACTION':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        if bpy.app.version >= (2, 91, 0):
                            row = layout.row(align=True, heading="Evaluation Time")
                            row.use_property_decorate = False
                            sub = row.row(align=True)
                            sub.prop(con, "use_eval_time", text="")
                            subsub = sub.row(align=True)
                            subsub.active = con.use_eval_time
                            subsub.prop(con, "eval_time", text="")
                            row.prop_decorator(con, "eval_time")

                        layout.prop(con, "mix_mode", text="Mix")

                        self.draw_influence(layout, con)

                    elif con.type == 'ARMATURE':

                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        col = layout.column()
                        col.prop(con, "use_deform_preserve_volume")
                        col.prop(con, "use_bone_envelopes")

                        col.prop(con, "use_current_location")

                        layout.operator("qconstraint.add_target", text="Add Target Bone")

                        layout.operator("qconstraint.normalize_target_weights")

                        self.draw_influence(layout, con)

                        if not con.targets:
                            layout.label(text="No target bones added", icon='ERROR')

                    elif con.type == 'CHILD_OF':

                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Location", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Location")

                        row.use_property_decorate = False
                        row.prop(con, "use_location_x", text="X", toggle=True)
                        row.prop(con, "use_location_y", text="Y", toggle=True)
                        row.prop(con, "use_location_z", text="Z", toggle=True)
                        row.label(icon='BLANK1')

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Rotation", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Rotation")

                        row.use_property_decorate = False
                        row.prop(con, "use_rotation_x", text="X", toggle=True)
                        row.prop(con, "use_rotation_y", text="Y", toggle=True)
                        row.prop(con, "use_rotation_z", text="Z", toggle=True)
                        row.label(icon='BLANK1')

                        if bpy.app.version >= (2, 90, 0):
                            row = layout.row(heading="Scale", align=True)
                        else:
                            row = layout.row(align=True)
                            row.label(text="Scale")

                        row.use_property_decorate = False
                        row.prop(con, "use_scale_x", text="X", toggle=True)
                        row.prop(con, "use_scale_y", text="Y", toggle=True)
                        row.prop(con, "use_scale_z", text="Z", toggle=True)
                        row.label(icon='BLANK1')

                        row = layout.row()
                        # row.operator("constraint.childof_set_inverse")
                        row.operator("bone.constraint_action", text="Set Inverse").action = 'CO_SET_INVERSE'
                        # row.operator("constraint.childof_clear_inverse")
                        row.operator("bone.constraint_action", text="Clear Inverse").action = 'CO_CLEAR_INVERSE'

                        self.draw_influence(layout, con)

                    elif con.type == 'FLOOR':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        layout.prop(con, "offset")
                        layout.prop(con, "floor_location", expand=True, text="Min/Max")
                        layout.prop(con, "use_rotation")

                        self.space_template(layout, con)

                        self.draw_influence(layout, con)

                    elif con.type == 'FOLLOW_PATH':

                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        if con.use_fixed_location:
                            layout.prop(con, "offset_factor", text="Offset Factor")
                        else:
                            layout.prop(con, "offset")

                        layout.prop(con, "forward_axis", expand=True)
                        layout.prop(con, "up_axis", expand=True)

                        col = layout.column()
                        col.prop(con, "use_fixed_location")
                        col.prop(con, "use_curve_radius")
                        col.prop(con, "use_curve_follow")

                        # layout.operator("constraint.followpath_path_animate", text="Animate Path", icon='ANIM_DATA')
                        layout.operator("bone.constraint_action", text="Animate Path", icon='ANIM_DATA').action = 'FOLLOW_PATH'

                        self.draw_influence(layout, con)

                    elif con.type == 'PIVOT':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con)

                        if con.target:
                            layout.prop(con, "offset", text="Pivot Offset")
                        else:
                            layout.prop(con, "use_relative_location")
                            if con.use_relative_location:
                                layout.prop(con, "offset", text="Pivot Point")
                            else:
                                layout.prop(con, "offset", text="Pivot Point")

                        col = layout.column()
                        col.prop(con, "rotation_range", text="Rotation Range")

                        self.draw_influence(layout, con)

                    elif con.type == 'SHRINKWRAP':
                        layout.use_property_split = True
                        layout.use_property_decorate = True

                        self.target_template(layout, con, False)

                        layout.prop(con, "distance")
                        layout.prop(con, "shrinkwrap_type", text="Mode")

                        layout.separator()

                        if con.shrinkwrap_type == 'PROJECT':
                            layout.prop(con, "project_axis", expand=True, text="Project Axis")
                            layout.prop(con, "project_axis_space", text="Space")
                            layout.prop(con, "project_limit", text="Distance")
                            layout.prop(con, "use_project_opposite")

                            layout.separator()

                            col = layout.column()
                            row = col.row()
                            row.prop(con, "cull_face", expand=True)
                            row = col.row()
                            row.active = con.use_project_opposite and con.cull_face != 'OFF'
                            row.prop(con, "use_invert_cull")

                            layout.separator()

                        if con.shrinkwrap_type in {'PROJECT', 'NEAREST_SURFACE', 'TARGET_PROJECT'}:
                            layout.prop(con, "wrap_mode", text="Snap Mode")

                            if bpy.app.version >= (2, 90, 0):
                                row = layout.row(heading="Align to Normal", align=True)
                            else:
                                row = layout.row(align=True)
                                row.label(text="Align to Normal")

                            row.use_property_decorate = False
                            sub = row.row(align=True)
                            sub.prop(con, "use_track_normal", text="")
                            subsub = sub.row(align=True)
                            subsub.active = con.use_track_normal
                            subsub.prop(con, "track_axis", text="")
                            if bpy.app.version >= (2, 90, 0):
                                row.prop_decorator(con, "track_axis")

                        self.draw_influence(layout, con)

                    elif con.type == 'PYTHON':
                        layout.label(text="Blender 2.6 doesn't support python constraints yet")

                    else:
                        return


class QC_PT_bArmatureConstraint_bones(bpy.types.Panel):
    bl_label = "Bones"
    bl_idname = "QC_PT_bArmatureConstraint_bones"
    bl_category = "Bone Layers"
    bl_parent_id = "QC_PT_qcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)

        if bone and bone.constraints:
            con = bone.constraints[idx]
            return con.type == 'ARMATURE'

        else:
            return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)
        con = bone.constraints[idx]

        for i, tgt in enumerate(con.targets):
            has_target = tgt.target is not None

            box = layout.box()
            header = box.row()
            header.use_property_split = False

            split = header.split(factor=0.45, align=True)
            split.prop(tgt, "target", text="")

            row = split.row(align=True)
            row.active = has_target
            if has_target:
                row.prop_search(tgt, "subtarget", tgt.target.data, "bones", text="")
            else:
                row.prop(tgt, "subtarget", text="", icon='BONE_DATA')

            header.operator("qconstraint.remove_target", text="", icon='X').index = i

            row = box.row()
            row.active = has_target and tgt.subtarget != ""
            row.prop(tgt, "weight", slider=True, text="Weight")


class QC_PT_bSplineIKConstraint_fitting(bpy.types.Panel):
    bl_label = "Fitting"
    bl_idname = "QC_PT_bSplineIKConstraint_fitting"
    bl_category = "Bone Layers"
    bl_parent_id = "QC_PT_qcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)

        if bone and bone.constraints:
            con = bone.constraints[idx]
            return con.type == 'SPLINE_IK'

        else:
            return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)
        con = bone.constraints[idx]

        col = layout.column()
        col.prop(con, "chain_count")
        col.prop(con, "use_even_divisions")
        col.prop(con, "use_chain_offset")


class QC_PT_bSplineIKConstraint_chain_scaling(bpy.types.Panel):
    bl_label = "Chain Scaling"
    bl_idname = "QC_PT_bSplineIKConstraint_chain_scaling"
    bl_category = "Bone Layers"
    bl_parent_id = "QC_PT_qcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)

        if bone and bone.constraints:
            con = bone.constraints[idx]
            return con.type == 'SPLINE_IK'

        else:
            return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)
        con = bone.constraints[idx]

        layout.prop(con, "use_curve_radius")

        layout.prop(con, "y_scale_mode")
        layout.prop(con, "xz_scale_mode")

        if con.xz_scale_mode in {'INVERSE_PRESERVE', 'VOLUME_PRESERVE'}:
            layout.prop(con, "use_original_scale")

        if con.xz_scale_mode == 'VOLUME_PRESERVE':
            col = layout.column()
            col.prop(con, "bulge", text="Volume Variation")

            if bpy.app.version >= (2, 90, 0):
                row = col.row(heading="Volume Min", align=True)
            else:
                row = col.row(align=True)
                row.label(text="Volume Min")

            row.prop(con, "use_bulge_min", text="")
            sub = row.row()
            sub.active = con.use_bulge_min
            sub.prop(con, "bulge_min", text="")

            if bpy.app.version >= (2, 90, 0):
                row = col.row(heading="Max", align=True)
            else:
                row = col.row(align=True)
                row.label(text="MAx")

            row.prop(con, "use_bulge_max", text="")
            sub = row.row()
            sub.active = con.use_bulge_max
            sub.prop(con, "bulge_max", text="")

            row = layout.row()
            row.active = con.use_bulge_min or con.use_bulge_max
            row.prop(con, "bulge_smooth", text="Smooth")


class QC_PT_bTransformConstraint_from(bpy.types.Panel):
    bl_label = "Map From"
    bl_idname = "QC_PT_bTransformConstraint_from"
    bl_category = "Bone Layers"
    bl_parent_id = "QC_PT_qcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)

        if bone and bone.constraints:
            con = bone.constraints[idx]
            return con.type == 'TRANSFORM'

        else:
            return False

    def draw(self, context):
        layout = self.layout

        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)
        con = bone.constraints[idx]

        layout.prop(con, "map_from", expand=True)

        layout.use_property_split = True
        layout.use_property_decorate = True

        from_axes = [con.map_to_x_from, con.map_to_y_from, con.map_to_z_from]

        if con.map_from == 'ROTATION':
            layout.prop(con, "from_rotation_mode", text="Mode")

        ext = "" if con.map_from == 'LOCATION' else "_rot" if con.map_from == 'ROTATION' else "_scale"

        col = layout.column(align=True)
        col.active = "X" in from_axes
        col.prop(con, "from_min_x" + ext, text="X Min")
        col.prop(con, "from_max_x" + ext, text="Max")

        col = layout.column(align=True)
        col.active = "Y" in from_axes
        col.prop(con, "from_min_y" + ext, text="Y Min")
        col.prop(con, "from_max_y" + ext, text="Max")

        col = layout.column(align=True)
        col.active = "Z" in from_axes
        col.prop(con, "from_min_z" + ext, text="Z Min")
        col.prop(con, "from_max_z" + ext, text="Max")


class QC_PT_bTransformConstraint_to(bpy.types.Panel):
    bl_label = "Map To"
    bl_idname = "QC_PT_bTransformConstraint_to"
    bl_category = "Bone Layers"
    bl_parent_id = "QC_PT_qcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)

        if bone and bone.constraints:
            con = bone.constraints[idx]
            return con.type == 'TRANSFORM'

        else:
            return False

    def draw(self, context):
        layout = self.layout

        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)
        con = bone.constraints[idx]

        layout.prop(con, "map_to", expand=True)

        layout.use_property_split = True
        layout.use_property_decorate = True

        if con.map_to == 'ROTATION':
            layout.prop(con, "to_euler_order", text="Order")

        ext = "" if con.map_to == 'LOCATION' else "_rot" if con.map_to == 'ROTATION' else "_scale"

        col = layout.column(align=True)
        col.prop(con, "map_to_x_from", expand=False, text="X Source Axis")
        col.prop(con, "to_min_x" + ext, text="Min")
        col.prop(con, "to_max_x" + ext, text="Max")

        col = layout.column(align=True)
        col.prop(con, "map_to_y_from", expand=False, text="Y Source Axis")
        col.prop(con, "to_min_y" + ext, text="Min")
        col.prop(con, "to_max_y" + ext, text="Max")

        col = layout.column(align=True)
        col.prop(con, "map_to_z_from", expand=False, text="Z Source Axis")
        col.prop(con, "to_min_z" + ext, text="Min")
        col.prop(con, "to_max_z" + ext, text="Max")

        layout.prop(con, "mix_mode" + ext, text="Mix")


class QC_PT_bActionConstraint_target(bpy.types.Panel):
    bl_label = "Target"
    bl_idname = "QC_PT_bActionConstraint_target"
    bl_category = "Bone Layers"
    bl_parent_id = "QC_PT_qcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)

        if bone and bone.constraints:
            con = bone.constraints[idx]
            return con.type == 'ACTION'

        else:
            return False

    def draw(self, context):
        layout = self.layout

        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)
        con = bone.constraints[idx]

        layout.use_property_split = True
        layout.use_property_decorate = True
        if bpy.app.version >= (2, 90, 0):
            layout.active = not con.use_eval_time
        layout.prop(con, "transform_channel", text="Channel")
        layout.prop(con, "target_space")

        col = layout.column(align=True)
        col.prop(con, "min", text="Range Min")
        col.prop(con, "max", text="Max")


class QC_PT_bActionConstraint_action(bpy.types.Panel):
    bl_label = "Action"
    bl_idname = "QC_PT_bActionConstraint_action"
    bl_category = "Bone Layers"
    bl_parent_id = "QC_PT_qcontraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(self, context):
        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)

        if bone and bone.constraints:
            con = bone.constraints[idx]
            return con.type == 'ACTION'

        else:
            return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        bone = context.active_pose_bone
        idx = getattr(bone, "constraint_active_index", None)
        con = bone.constraints[idx]

        layout.prop(con, "action")
        layout.prop(con, "use_bone_object_action")

        col = layout.column(align=True)
        col.prop(con, "frame_start", text="Frame Start")
        col.prop(con, "frame_end", text="End")
