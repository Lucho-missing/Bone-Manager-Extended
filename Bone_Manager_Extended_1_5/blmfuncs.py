import string
from tokenize import String
import bpy
from bpy.props import BoolProperty, IntProperty, StringProperty


# Utility functions #

def clean_string(value):
    val = value
    val = val.replace(".", " ")
    val = val.replace("_", " ")
    # val = val.replace("-", " ")
    # val = val.casefold()
    val = val.title()
    return val

def string_name(value):
    val = value
    val = val.replace(" ", "_")
    return val

def check_clear(target, string, list):
    garbage = []
    for name, prop in target.items():
        if string in name:
            found = False
            for obj in list:
                if string == name:
                    found = True
                    break
            if found == False: 
                garbage.append(name)
    for name in garbage:
        del target[name]     

def ShowMessageBox(message="", title="Message Box", icon='INFO'):
    # Simple display message utility

    def draw(self, context):
        for line in message:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def get_bones(arm, context, selected):
    # Get armature bones according to current context

    if context.mode == 'EDIT_ARMATURE':
        if selected:
            bones = [b for b in arm.edit_bones if b.select is True]
        else:
            bones = arm.edit_bones
    elif context.mode == 'OBJECT':
        if selected:
            bones = []
        else:
            bones = arm.bones
    else:
        if selected:
            # Ugly Try/except to catch weight paint context error if armature is not related to mesh.
            try:
                # fails if bone layer is invisible
                # pose_bones = context.selected_pose_bones
                # bones = [b.id_data.data.bones[b.name] for b in pose_bones]
                bones = [b for b in arm.bones if b.select is True]
            except TypeError:
                return []
        else:
            bones = arm.bones

    return bones


def check_used_layer(arm, layer_idx, context):
    # Check whether the given layer is used

    bones = get_bones(arm, context, False)

    is_use = 0

    for bone in bones:
        if bone.layers[layer_idx]:
            is_use = 1
            break

    return is_use


def check_selected_layer(arm, layer_idx, context):
    # Check wHether selected bones are in layer

    bones = get_bones(arm, context, True)

    is_sel = 0

    for bone in bones:
        if bone.layers[layer_idx]:
            is_sel = 1
            break

    return is_sel


def prefs():
    # Pointer for preferences where UI settings are stored

    return bpy.context.preferences.addons[__package__].preferences
