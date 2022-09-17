import bpy
import random
import string
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from .blmfuncs import ShowMessageBox
from .create_rigui_id import insert_rna_default
from bpy_extras.io_utils import ExportHelper, ImportHelper
import os
import csv


class BLM_OT_exportlayers(bpy.types.Operator, ExportHelper):
    # Export Layer config
    bl_idname = "bone_layer_man.exportlayers"
    bl_label = "Export Layers"
    bl_description = "Export layer names and RigUI config"

    filename_ext = ".csv"

    filter_glob: StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        )

    @classmethod
    def poll(self, context):
        return getattr(context.active_object, 'type', False) == 'ARMATURE'

    def invoke(self, context, event):
        self.filepath = os.path.splitext(bpy.data.filepath)[0] + "_layerconfig.csv"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        ac_ob = context.active_object
        scn = context.scene
        rows = {}

        for key, value in ac_ob.data.items():
            if key.startswith(("layer_name_", "rigui_id_")):
                rows[key] = value

        with open(f'{self.filepath}', 'w', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in rows.items():
                writer.writerow([key, value])

        csv_file.close()
        ShowMessageBox(("Layer config exported successfully",), "Bone Layer Manager")

        return {'FINISHED'}


class BLM_OT_Importlayers(bpy.types.Operator, ImportHelper):
    # Import Layer Config
    bl_idname = "bone_layer_man.importlayers"
    bl_label = "Import Layers"
    bl_description = "Import layer names and RigUI config"

    filename_ext = ".csv"

    filter_glob: StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        )

    layer_idx: IntProperty(
        name="Layer Index",
        description="Index of the layer to be named",
        default=-1, min=-1, max=31)

    rigui_id: IntProperty(
        name="RigUI Layer",
        description="Index of the RigUI layer",
        default=-1, min=-1, max=31, soft_min=-1, soft_max=31)

    @classmethod
    def poll(self, context):
        return getattr(context.active_object, 'type', False) == 'ARMATURE'

    def draw(self, context):
        layout = self.layout

    def execute(self, context):

        try:
            self.file = open(f'{self.filepath}', 'r', encoding='utf-8')
        except IOError:
            ShowMessageBox(("Cannot access file",), "Bone Layer Manager", 'ERROR')
            return

        # check for file format with sniffer
        sample = self.file.read(1024)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except UnicodeDecodeError:
            ShowMessageBox(("File Format (encoding) not recognised",), "Bone Layer Manager", 'ERROR')
            return
        except csv.Error:
            ShowMessageBox(("File Format (dialect) not recognised",), "Bone Layer Manager", 'ERROR')
            return

        try:
            with open(f'{self.filepath}', 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                custom_prop_dict = dict(reader)

                arm = context.active_object.data

                #BLEND3.0 COMPAT
                if bpy.app.version < (3, 0, 0):
                    if not arm.get('_RNA_UI'):
                        arm['_RNA_UI'] = dict()

                for key, value in custom_prop_dict.items():

                    if key.startswith("layer_name_"):
                        arm[f"{key}"] = value

                    elif key.startswith("rigui_id_"):
                        self.rigui_id = int(value)
                        arm[key] = self.rigui_id
                        insert_rna_default(arm, self.rigui_id, int(value))
                
                csv_file.close()
        
        except:
            ShowMessageBox(("File read error!",), "Bone Layer Manager", 'ERROR')
            csv_file.close()

        # redraw Properties panel
        for window in bpy.context.window_manager.windows:
            screen = window.screen

            for area in screen.areas:
                if area.type == 'PROPERTIES':
                    area.tag_redraw()
                    break

        return {'FINISHED'}
