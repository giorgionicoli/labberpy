from typing import List
import json
import re
import glob
import os.path

from labber import LabberFile
from labvar import LabVar
from labels import Label


BASE_PATH = ""


class DataExtractor:
    def __init__(self, file_name: str = "", file_num: str = ""):
        if not file_name:
            if file_num:
                file_name = f"{file_num}_*.hdf5"
            else:
                print(
                    f"DataExtractor.__init__ Error: "
                    f"No file_name or file_num provided.\n"
                    f"Please give a valid hdf5 file identifier."
                )
                return

        if BASE_PATH:
            file_path = BASE_PATH + r"/2*/*/*/"
        else:
            file_path = ""

        try:
            file_path = os.path.abspath(glob.glob(file_path + file_name)[0])
            self._labber_file = LabberFile(file_path)
        except Exception:
            print(
                f"DataExtractor.__init__ Error: "
                f"The specified file couldn't be found.\n"
                f"Please check the correctnes of the inputs.\n"
                f"Also check the value of BASE_PATH."
            )

    def get_vars(self, *var_list: List):
        data_out = list()
        for var_name in var_list:
            data = self._labber_file.get_phys_data(var_name)
            unit = self._labber_file.variables[var_name]["phys_unit"]
            label = Labeler().autolabel(var_name, unit)
            data_out.append(LabVar(data, label))
        return data_out


class Labeler:
    _label_templates = {}

    def __init__(self, json_path: str = "label_templates.json"):
        try:
            with open(json_path) as json_file:
                self._label_templates.update(json.load(json_file))
        except Exception:
            print(
                f"Labeler.__init__() Exception: Json file not found."
                f"Continuing without updating _label_templates."
            )

    def autolabel(self, var_name, unit):
        label_info = self._label_templates.get(unit, None)
        if label_info is not None:
            var_parse = re.match(
                label_info["symbol"] + r"_?([a-zA-Z0-9]+)", var_name
            )
            label_info.update(
                self._label_templates.get(var_parse.group(1).title(), {})
            )
            try:
                return Label(**label_info)
            except Exception:
                print(
                    f"Labeler.autolabel() Exception: "
                    f"arguments passed to Label() object not correct.\n"
                    f"Continuing with empty Label() object "
                    f"for variable --> {var_name}"
                )
        return Label()
