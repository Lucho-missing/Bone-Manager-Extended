import bpy

from bpy.props import IntProperty
from .blmfuncs import get_bones


class BLMERGE_OT_merge(bpy.types.Operator):
    # Move Selected Bones to this Layer, Shift + Click to assign to multiple layers
    bl_idname = "bone_layer_man.blmergeselected"
    bl_label = ""
    # bl_description = "Move selected Bones to this Layer.\nShift + Click to assign to multiple layers"

    layer_idx: IntProperty(name="Layer Index",
                           description="Index of the layer to assign",
                           default=0, min=0, max=31)

    @classmethod
    def poll(self, context):
        arm = getattr(context.active_object, 'data', None)
        not_link = (getattr(arm, 'library', None) is None)
        return not_link

    @classmethod
    def description(self, context, properties):
        arm = context.active_object.data

        name_id_prop = f"layer_name_{properties.layer_idx}"

        if name_id_prop in arm:
            text = f'{arm[name_id_prop]}'
            if text == '':
                text = f'Unamed Layer [{properties.layer_idx}]'
        else:
            text = f'Unamed Layer [{properties.layer_idx}]'

        return (
            f'{text}\n'
            f'Move selected Bones (Shift = Multi-assign, Alt = Visibility).'
        )

    def __init__(self):
        self.shift = False
        self.alt = False
        self.ctrl = False

    def invoke(self, context, event):
        self.shift = event.shift
        self.alt = event.alt

        return self.execute(context)

    def execute(self, context):
        arm = context.active_object.data

        bones = get_bones(arm, context, True)

        if self.alt:
            arm.layers[self.layer_idx] = not arm.layers[self.layer_idx]
            return {'FINISHED'}

        for bone in bones:

            if self.shift:
                bone.layers[self.layer_idx] ^= True

            else:
                is_layers = [False] * (self.layer_idx)
                is_layers.append(True)
                is_layers.extend([False] * (len(bone.layers) - self.layer_idx - 1))
                bone.layers = is_layers

        return {'FINISHED'}
