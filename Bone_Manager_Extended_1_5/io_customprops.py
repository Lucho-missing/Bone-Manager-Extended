import bpy
import os
import csv
import sys
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from .blmfuncs import ShowMessageBox
from bpy_extras.io_utils import ExportHelper, ImportHelper
import numpy as np
from dataclasses import fields

from rna_prop_ui import rna_idprop_value_item_type, rna_idprop_ui_create

# BLEND3.0 COMPAT
if bpy.app.version < (3, 0, 0):
    from rna_prop_ui import rna_idprop_ui_prop_get

if bpy.app.version >= (2, 90, 0):
    if sys.version_info >= (3, 8):
        from typing import TypedDict
    else:
        from typing_extensions import TypedDict


# property class types useds for value casting
class CSV_Record_main(TypedDict):
    proptype: str
    overridable: bool
    description: str
    subtype: str
    
class CSV_Record_int(CSV_Record_main):
    value: int
    default: int
    min: int
    max: int
    soft_min: int
    soft_max: int
    
    step: int


class CSV_Record_float(CSV_Record_main):
    value: float
    default: float
    min: float
    max: float
    soft_min: float
    soft_max: float
    
    step: float
    precision: int


class CSV_Record_list(CSV_Record_main):
    value: str
    default: str
    min: float
    max: float
    soft_min: float
    soft_max: float


class CSV_Record_float_array(CSV_Record_main):
    value: str
    default: str
    min: float
    max: float
    soft_min: float
    soft_max: float

    step: float
    precision: int

class CSV_Record_int_array(CSV_Record_main):
    value: str
    default: str
    min: int
    max: int
    soft_min: int
    soft_max: int
 
    step: int

class CSV_Record_string(CSV_Record_main):
    value: str
    default: str
    min: float
    max: float
    soft_min: float
    soft_max: float

#for debug only
def print_dict(func, dic):
    print(func)
    for key, value in dic.items():
        print(key, ' : ', value)

def dict_cast(dict_, typed_dict) -> dict:
    # Convert values in given dictionary to corresponding types in TypedDict
    fields = typed_dict.__annotations__

    if typed_dict.__name__ == 'CSV_Record_float_array':
        temp = {k: fields[k](v) for k, v in dict_.items() if k not in {'value', 'default', 'step', 'precision'}}
        temp['value'] = [float(x) for x in dict_['value'].strip("[]").split(",")]
        temp['default'] = [float(x) for x in dict_['default'].strip("[]").split(",")]
        #BLEND3.0 COMPAT
        if bpy.app.version >= (3, 0, 0):
            try:
                temp['step'] = float(dict_['step'])
                temp['precision'] = int(dict_['precision'])
            except KeyError:
                return temp
                
        return temp

    elif typed_dict.__name__ == 'CSV_Record_int_array':
        temp = {k: fields[k](v) for k, v in dict_.items() if k not in {'value', 'default', 'step', 'precision'}}
        temp['value'] = [int(x) for x in dict_['value'].strip("[]").split(",")]
        temp['default'] = [int(x) for x in dict_['default'].strip("[]").split(",")]
        #BLEND3.0 COMPAT
        if bpy.app.version >= (3, 0, 0):
            temp['step'] = int(dict_['step'])

        return temp

    elif typed_dict.__name__ == 'CSV_Record_list':

        temp = {k: fields[k](v) for k, v in dict_.items() if k not in {'value', 'default'}}

        temp['value'] = [x for x in dict_['value'].strip("[]").split(",")]
        temp['default'] = [x for x in dict_['default'].strip("[]").split(",")]

        return temp

    else:
        #BLEND3.0 COMPAT
        temp = {k: fields[k](v) for k, v in dict_.items() if k not in {'step', 'precision'}}
        #BLEND3.0 COMPAT
        if bpy.app.version >= (3, 0, 0) and typed_dict.__name__ == 'CSV_Record_float':
            try:
                temp['step'] = float(dict_['step'])
                temp['precision'] = int(dict_['precision'])

            except KeyError:
                return temp

        #BLEND3.0 COMPAT
        if bpy.app.version >= (3, 0, 0) and typed_dict.__name__ == 'CSV_Record_int':
            try:
                temp['step'] = int(dict_['step'])
            except KeyError:
                return temp
                
        return temp


def insert_rna_posebone(pose_bone, prop_name, prop_dict):

    #BLEND3.0 COMPAT
    if bpy.app.version < (3, 0, 0):
        prop_dict.pop('precision', None)
        prop_dict.pop('step', None)      
        if not pose_bone.get('_RNA_UI'):
            pose_bone['_RNA_UI'] = {}

    proptype = prop_dict.pop('proptype')
    overridable = prop_dict.pop('overridable')
    prop_import = prop_dict.pop('prop_import')
    array_type = prop_dict.pop('array_type')
    # name key is sneaking in... 
    prop_dict.pop('name', None)

    rna_dict = {k: v for k, v in prop_dict.items() if v != ''}

    if proptype == 'float':
        prop_dict = dict_cast(rna_dict, CSV_Record_float)

    elif proptype == 'int':
         prop_dict = dict_cast(rna_dict, CSV_Record_int)

    elif proptype == 'list':
        prop_dict = dict_cast(rna_dict, CSV_Record_list)

    elif proptype == 'str':
        prop_dict = dict_cast(rna_dict, CSV_Record_string)

    elif proptype == 'IDPropertyArray':
        if array_type == 'd':
            prop_dict = dict_cast(rna_dict, CSV_Record_float_array)
        elif array_type == 'i':
            prop_dict = dict_cast(rna_dict, CSV_Record_int_array)
        else:
            print(f"Property {proptype} typecode : {array_type} not supported")
    else:
        print(f"Property {proptype} typecode : {array_type} not supported")

    value = prop_dict.pop('value')

    import_skip = ""

    #BLEND3.0 COMPAT
    if bpy.app.version < (3, 0, 0):
        if prop_name not in pose_bone["_RNA_UI"]:
            pose_bone[prop_name] = value
            pose_bone["_RNA_UI"][prop_name] = prop_dict

            if overridable == 'True':
                pose_bone.property_overridable_library_set(f'["{prop_name}"]', True)

        else:
            import_skip = "SKIP"
    
    else:
        if prop_name not in pose_bone.keys():
            if proptype == 'list':
                pose_bone[prop_name] = value
                            
            else:
                try:
                    pose_bone[prop_name] = value 
                    ui = pose_bone.id_properties_ui(prop_name)
                    ui.update(**prop_dict)
                    if overridable == 'True':
                        pose_bone.property_overridable_library_set(f'["{prop_name}"]', True)
                
                # clean and leave
                except:
                    if prop_name in pose_bone.keys():
                        del pose_bone[prop_name]
                    return "ERROR"

        else:
            import_skip = True

    return import_skip


class BLM_OT_exportprops(bpy.types.Operator, ExportHelper):
    # Export Custom Properties
    bl_idname = "bone_layer_man.exportprops"
    bl_label = "Export Properties"
    bl_description = "Export active bone custom properties"

    filename_ext = ".csv"

    filter_glob: StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        )

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None) is not None and bpy.context.active_pose_bone:
            bone = context.active_pose_bone

            if bone.bone.select:
                rna_properties = {
                    prop.identifier for prop in bpy.types.PoseBone.bl_rna.properties
                    if prop.is_runtime
                    }

                if getattr(context.active_object, 'pose', None) is not None:
                    bone = context.active_pose_bone
                    # BLEND3.0 COMPAT
                    if bpy.app.version < (3, 0, 0):
                        props = [k for k, v in sorted(bone.items()) if k != '_RNA_UI' and k not in rna_properties]

                    else:
                        props = [k for k, v in sorted(bone.items()) if k not in rna_properties]
                    return len(props) > 0

                else:
                    return False

        else:
            return False

    def invoke(self, context, event):
        self.filepath = os.path.splitext(bpy.data.filepath)[0] + "_custom_properties.csv"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        rows = {}

        # BLEND3.0 COMPAT
        if bpy.app.version < (3, 0, 0):
            fields = ['prop_name', 'proptype', 'value', 'default', 'min', 'max', 'soft_min', 'soft_max', 'overridable', 'description', 'subtype', 'array_type']
        
        else:
            fields = ['prop_name', 'proptype', 'value', 'default', 'min', 'max', 'soft_min', 'soft_max', 'step', 'precision', 'overridable', 'description', 'subtype', 'array_type']

        pose_bone = bpy.context.active_pose_bone

        rna_properties = {
            prop.identifier for prop in bpy.types.PoseBone.bl_rna.properties
            if prop.is_runtime
        }

        # BLEND3.0 COMPAT
        if bpy.app.version < (3, 0, 0):
            if not pose_bone.get('_RNA_UI'):
                pose_bone['_RNA_UI'] = {}
            items = {k: v for k, v in sorted(pose_bone.items()) if k != '_RNA_UI'}

        else:
            items = {k: v for k, v in sorted(pose_bone.items())}

        export_dict = {}


        for i, (k, v) in enumerate(items.items()):

            # BLEND3.0 COMPAT
            # Try fetch UI Data as dictionary
            # to_dict = getattr(val, "to_dict", None)
            # to_list = getattr(val, "to_list", None)
            is_list = isinstance(pose_bone[k], list)

            export_dict[f'{k}'] = {}

            if not is_list:
                try:
                    if bpy.app.version < (3, 0, 0):
                        ui = rna_idprop_ui_prop_get(pose_bone, k).to_dict()
                    else:
                        ui = pose_bone.id_properties_ui(k).as_dict()

                    export_dict[f'{k}'] = ui

                except TypeError:
                    continue
            

            proptype, is_array = rna_idprop_value_item_type(pose_bone[k])

            export_dict[f'{k}']['value'] = v

            if is_array:
                if is_list:
                    export_dict[f'{k}']['proptype'] = 'list'
                else:    
                    export_dict[f'{k}']['proptype'] = 'IDPropertyArray'
            else:
                export_dict[f'{k}']['proptype'] = proptype.__name__

            export_dict[f'{k}']['overridable'] = pose_bone.is_property_overridable_library(f'["{k}"]')

            if is_array:

                if is_list:
                    np_default = np.array(pose_bone[k])  
                    np_dstring = np.array2string(np_default, separator=',')
                    export_dict[f'{k}']['default'] = np_dstring
                
                else:
                    export_dict[f'{k}']['array_type'] = pose_bone[k].typecode

                    np_value = np.array(v)

                    np_vstring = np.array2string(np_value, separator=',', precision=6, formatter={'float_kind': lambda x: "%.6f" % x})
                    export_dict[f'{k}']['value'] = np_vstring

                    # if 'default' is not configured correctly use 'value'
                    try:
                        np_default = np.array(ui['default'])                
                        np_dstring = np.array2string(np_default, separator=',', precision=6, formatter={'float_kind': lambda x: "%.6f" % x})
                    
                    except KeyError:
                        np_dstring = np.array2string(np_value, separator=',', precision=6, formatter={'float_kind': lambda x: "%.6f" % x})

                    export_dict[f'{k}']['default'] = np_dstring

        with open(f'{self.filepath}', 'w', encoding="utf-8", newline='') as csv_file:

            writer = csv.DictWriter(csv_file, fields)
            writer.writeheader()
            for k in export_dict:
                if k != 'constraint_active_index':
                    export_dict[k]['prop_name'] = k
                    writer.writerow(export_dict[k])

        csv_file.close()

        ShowMessageBox(("custom properties exported successfully",), "Bone Layer Manager")

        return {'FINISHED'}


class BLM_OT_importprops(bpy.types.Operator, ImportHelper):
    # Import Custom Properties
    bl_idname = "bone_layer_man.importprops"
    bl_label = "Import Properties"
    bl_description = "Import custom properties to active bone"

    filename_ext = ".csv"

    filter_glob: StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        )

    @classmethod
    def poll(self, context):
        if getattr(context.active_object, 'pose', None) is not None and bpy.context.active_pose_bone:
            return context.active_pose_bone.bone.select

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        # BLEND3.0 COMPAT
        if bpy.app.version < (3, 0, 0):
            fields = ['prop_name', 'proptype', 'value', 'default', 'min', 'max', 'soft_min', 'soft_max', 'overridable', 'description', 'subtype', 'array_type']
        
        else:
            fields = ['prop_name', 'proptype', 'value', 'default', 'min', 'max', 'soft_min', 'soft_max', 'step', 'precision', 'overridable', 'description', 'subtype', 'array_type']

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

        
        with open(f'{self.filepath}', 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)

            write_dic = {}
            context.window_manager.prop_data.clear()

            try:
                for row in reader:
                    prop = row.pop('prop_name')
                    a = {k: v for k, v in row.items()}
                    write_dic[prop] = a
                    prop_item = context.window_manager.prop_data.add()
                    prop_item.name = prop
                    prop_item.prop_import = True
                    for k, v in row.items():
                        if k not in fields:
                            continue
                        prop_item[f'{k}'] = v

                csv_file.close()

            except KeyError:
                ShowMessageBox(("File read error!",), "Bone Layer Manager", 'ERROR')
                csv_file.close()
                return {'FINISHED'}


        bpy.ops.bone_layer_man.proppopup('INVOKE_DEFAULT')

        return {'FINISHED'}


class BLM_UL_proplist(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, active_data, active_propname, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False)

            # BLEND3.0 COMPAT
            if bpy.app.version < (3, 0, 0):
                row.emboss = 'UI_EMBOSS_NONE_OR_STATUS'
            else:
                row.emboss = 'NONE_OR_STATUS'

            props = bpy.context.window_manager.prop_data

            if not props[f'{item.name}'].prop_import:
                row.active = False

            checkbox = "CHECKBOX_HLT" if row.active else "CHECKBOX_DEHLT"
            row.prop(props[f'{item.name}'], "prop_import", text="", emboss=False, icon=checkbox)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")


class BLM_OT_proppopup(bpy.types.Operator):
    bl_idname = "bone_layer_man.proppopup"
    bl_label = "Import Custom Properties"
    bl_options = {'REGISTER'}

    def execute(self, context):

        pose_bone = bpy.context.active_pose_bone

        write_set = context.window_manager.prop_data
        import_skip = {}

        for key, v in write_set.items():
            if write_set[f'{key}'].prop_import:
                import_skip[key] = insert_rna_posebone(pose_bone, key, v)

        for window in bpy.context.window_manager.windows:
            screen = window.screen

            for area in screen.areas:
                if area.type == 'PROPERTIES':
                    area.tag_redraw()
                    break

        for region in context.area.regions:
            if region.type == "UI":
                region.tag_redraw()

        if 'ERROR' or 'SKIP' in import_skip.values():
            skip_count = len([i for i in import_skip.values() if i == 'SKIP'])
            err_count = len([i for i in import_skip.values() if i == 'ERROR'])
            ShowMessageBox((f"{skip_count} Entries skipped", f"{err_count} Entries failed"), "Bone Layer Manager")

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def check(self, context):
        return True

    def draw(self, context):
        wm = bpy.context.window_manager
        layout = self.layout
        row = layout.row()
        row.template_list("BLM_UL_proplist", "", wm, "prop_data", wm, "prop_index", rows=10)
