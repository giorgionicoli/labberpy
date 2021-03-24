from typing import List
import json
import regex as re

from labber import LabberFile
from labvar import LabVar
from labels import Label


class DataExtractor:
    def __init__(self, file_name: str):
        self._labber_file = LabberFile(file_name)

    def get_vars(self, *var_list: List):
        data_out = list()
        for var_name in var_list:
            data = self._labber_file.get_phys_data(var_name)
            unit = self._labber_file.variables[var_name]["phys_unit"]
            label = Labeler()._autolabel(var_name, unit)
            data_out.append(LabVar(data, label))


class Labeler:
    _label_templates = {}

    def __init__(self, json_path: str = "label_templates.json"):
        try:
            with open(json_path) as json_file:
                self._label_templates.update(json.load(json_file))
        except Exception:
            print(f"Labeler.__init__() Exception: Json file not found."
                  f"Continuing without updating _label_templates.")

    def _autolabel(self, var_name, unit):
        label_info = self._label_templates.get(unit, None)
        if label_info is not None:
            var_parse = re.match(label_info["symbol"] + r'_?([a-zA-Z0-9]+)', var_name)
            label_info.update(self._label_templates.get(var_parse.group(1).title(), {}))
            try:
                return Label(**label_info)
            except Exception:
                print(f"Labeler._autolabel() Exception: args passed to Label() object not correct."
                      f"Continuing with empty Label() object for variable --> {var_name}")
        return Label()

    '''def make_label(
        self,
        name: str = "",
        symbol: str = "",
        unit: str = "",
        prefix: str = "",
        subscript: str = "",
        superscript: str = "",
        multiplier: str = "",
        short_form: bool = True,
    ):

        return Label(
            name = name,
            symbol = symbol,
            unit = unit,
            prefix = prefix,
            subscript = subscript,
            superscript = superscript,
            multiplier = multiplier
        )

    def _parse_var_name(self, var_name: str, var_symbol: str) -> str:
        var_parse = re.match(var_symbol + r'_?([a-zA-Z0-9]+)', var_name)


        no_match = True

        v_test = re.match(r'V_?([a-zA-Z0-9]+)', var_name)
        if v_test:
            var_symbol = r'$V_\mathrm{' + v_test.group(1) + r'}$'
            no_match = False

        if no_match:
            b_test = re.match(r'([mM]agnetic|[bB])_?[fF]ield', var_name)
            if b_test:
                var_symbol = r'$B$'
                no_match = False

        if no_match:
            i_test = re.match(r'I_?([a-zA-Z0-9]+)', var_name)
            if i_test:
                var_symbol = r'$I_\mathrm{' + i_test.group(1) + r'}$'
                no_match = False

        if no_match:
            var_symbol = ''
        else:
            phase_test = re.search(r'[pP]hase', var_name)
            if phase_test:
                # add the \angle character in the front
                var_symbol = r'$\angle ' + var_symbol[1:]

        return var_symbol'''

