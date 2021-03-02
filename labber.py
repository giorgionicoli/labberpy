import h5py as h5
import numpy as np
import re

from labvar import LabVar


class LabberFile:
    def __init__(self, file_name: str, path: str = ""):
        """still missing custom path choice"""
        self._h5handle = h5.File(file_name)
        logged: dict = {
            var[0].decode(): {"type": "log"}
            for var in self._h5handle["Log list"]
        }
        stepped: dict = {
            var[0].decode(): {"type": "step"}
            for var in list(self._h5handle["Data/Channel names"])
            if var[0].decode() not in logged
        }
        fixed: dict = {
            var[0].decode(): {"type": "fixed"}
            for var in list(self._h5handle["Step list"])
            if var[0].decode() not in stepped
        }
        self._variables = stepped | fixed | logged
        self._initMetadata()

    def _initMetadata(self) -> None:

        for var_info in self._h5handle["Channels"]:

            var_name = var_info[0].decode()

            if var_name in self._variables.keys():

                instr_name = var_info[1].decode()
                channel_name = var_info[2].decode()
                phys_unit = var_info[3].decode()
                instr_unit = var_info[4].decode()
                instr_gain = var_info[5]
                instr_offset = var_info[6]
                instr_ampl = var_info[7]

                path = "Instrument config/" + instr_name
                instr_value = self._h5handle[path].attrs[channel_name]

                if isinstance(instr_value, (int, float, np.float64)):
                    phys_value = (
                        instr_value / instr_ampl - instr_offset
                    ) / instr_gain
                else:
                    phys_value = ""

                self._variables[var_name].update(
                    {
                        "instr_name": instr_name,
                        "channel_name": channel_name,
                        "phys_unit": phys_unit,
                        "instr_unit": instr_unit,
                        "instr_gain": instr_gain,
                        "instr_offset": instr_offset,
                        "instr_ampl": instr_ampl,
                        "instr_value": instr_value,
                        "phys_value": phys_value,
                    }
                )


'''class LabberFile():
    """Class to extracts data and metadata from .hdf5 files generated
       by the Labber measurement editor"""

    def __init__(self, file_name: str):
        """initializes the instance attributes"""

        self.file_name = file_name # name of the file to retrieve
        self.handle = h5.File(file_name) # file handle to the .hdf5 file, used to access the data
        self.file_num = self._initFileNum() # number that identifies the file in my dataset
        self.variables = self._initVariables() # list of experimental variables, even those not swept
        self.logs = self._initLogs() # list of logged variables
        self.channels = self._initChannels() # list of the relevant channels names (actively swept and logged)
        self.all_channels = self._initAllChannels() # variables + logs, just for convenience of operations
        self.swept_vars = self._initSweptVars() # list of actively swept variables
        self.step_size = self._initStepSizes() # k, v = var_name, step size (number of steps)
        self.units = self._initUnits() # k, v = var_name, units: str
        self.sweep_dim = self._initSweepDim() # int indicating how many step channels were swept for the measurement
        self.rawdata = self._initRawData() # k, v = var_name, np.ndarray variable
        self.var_relations = self._initVarRelations() # k, v = var_name, dict equation and variables
        self.metadata = self._initMetadata() # k, v = var_name, value (either from step items or evaluated from relation), only for vars not in channels)
        self.labdata = self._initLabData() # k, v = var_name, LabData variable

    def _initFileNum(self) -> str:
        """uses regex to find the numbers at the beginning of the file name
           that identify that file in the dataset"""

        return re.match(r'^(\d+)_', self.file_name).group(1)

    def _initVariables(self) -> list:
        """doc-string"""

        return [x[0].decode() for x in self.handle['Step list']]

    def _initLogs(self) -> list:
        """doc-string"""

        return [x[0].decode() for x in self.handle['Log list']]

    def _initChannels(self) -> list:
        """initialiazes the list of channels for which values are stored
           in the Data/Data dataset of the .hdf5 Labber file.
           It's crucial to leave the order of this list as found in the original
           file, because they are connected of the 2nd dimension index of the
           array containing the data. See also the _initData() method"""

        return [ch[0].decode() for ch in list(self.handle['Data/Channel names'])]

    def _initAllChannels(self) -> list:
        """doc-string"""

        return self.variables + self.logs

    def _initSweptVars(self) -> list:
        """doc-string"""

        return [var for var in self.channels if var not in self.logs]

    def _initStepSizes(self) -> dict:
        """doc-string"""

        return dict(zip(self.variables, list(self.handle.attrs['Step dimensions'])))

    def _initUnits(self) -> dict:
        """doc-string"""

        channel_data = list(self.handle['Channels'])
        units_list = {ch[0].decode(): ch[3].decode() for ch in channel_data
                      if ch[0].decode() in self.all_channels}

        return units_list

    def _initSweepDim(self) -> int:
        """doc-string"""

        return len(self.swept_vars)

    def _initRawData(self) -> dict: # return k, v = var_name, var_data as np.ndarray
        """doc-string"""

        data = dict()
        data_array = self.handle['Data/Data'][:]
        var_num = len(self.channels)
        steps_list = [self.step_size[var] for var in self.swept_vars]

        for i in range(var_num):

            var_data = data_array[:,i,:]

            if self.sweep_dim == 1:
                new_shape = steps_list[0]
                var_data = var_data.reshape(new_shape, order='F')
            elif self.sweep_dim > 2:
                new_shape = (steps_list[0], steps_list[1], (var_data.shape[1]/steps_list[1]).astype(int))
                var_data = var_data.reshape(new_shape, order='F')

            data[self.channels[i]] = var_data

        return data

    def _initVarRelations(self) -> 'dict(dict)':
        """doc-string"""

        relations = dict()

        for item in self.handle['Step list']:

            rel_key = item[0].decode() # channel/variable name
            rel_dict = dict()

            equation = ''
            equation_variables = list()

            if item[5]:

                equation = item[6].decode()

                path = 'Step config/' + rel_key + '/Relation parameters'

                for a_var in list(self.handle[path][:]):
                    eq_var = a_var[0].decode()
                    exp_var = a_var[1].decode()
                    equation_variables.append((eq_var, exp_var,))

            rel_dict['equation'] = equation
            rel_dict['variables'] = equation_variables
            relations[rel_key] = rel_dict

        return relations

    def _initLabData(self) -> dict:
        """doc-string"""
        pass

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

    def _guessPlotGain(data: 'some form of data to base the guess on') -> float:
        """doc-string"""
        pass


class LabData():

    def __init__(self, data: 'np.ndarray',
                 variable_name: str = '', symbol: str = '',
                 unit: str = '', plot_gain: float = 1.0,
                 tags: set = set(),
                 **kwargs):
        self.data = data
        self.attrs = {'variable_name': variable_name,
                      'symbol': symbol,
                      'unit': unit,
                      'plot_gain': plot_gain,
                      'tags': tags}
        self.exp_param = dict()
'''
