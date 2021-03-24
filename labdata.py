from typing import List
import json

from labber import LabberFile
from labvar import LabVar
from labels import Label


class DataExtractor:
    def __init__(self, file_name: str):
        self._labber_file = LabberFile(file_name)

    def get_vars(self, var_list: List):
        data_out = list()
        for var_name in var_list:
            data = self._labber_file.get_phys_data(var_name)
            unit = self._labber_file.variables[var_name]["phys_unit"]
            label = Labeler()._autolabel(var_name, unit)
            data_out.append(LabVar(data, label))


class Labeler:
    _label_templates = {}

    def __init__(self, json_path: str = "label_templates.json"):
        with open(json_path) as json_file:
            self._label_templates.update(json.load(json_file))

    def _autolabel(self, var_name, unit):
        template_info = self._label_templates.get(unit, None)
        if template_info is not None:
            label = self.make_label(**template_info)
        return label

    def make_label(
        self,
        name: str = "",
        symbol: str = "",
        unit: str = "",
        subscript: str = "",
        prefix: str = "",
        pre_unit: str = "",
        short_form: bool = True,
    ):
        name = fr"{prefix} {name}"
        symbol = fr"${symbol}_\mathrm{subscript}$"
        unit = fr"{unit}"
        return Label(name, symbol, unit)


'''
def _guessSymbol(var_name: str) -> str:
    """uses regex and common nomenclature of labber variables to create
        LaTeX compatible str variable symbols"""

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

    return var_symbol
    '''
