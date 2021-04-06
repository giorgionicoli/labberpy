import h5py as h5
import numpy as np


def _decode_if_necessary(input_):
    if isinstance(input_, bytes):
        return input_.decode()
    return input_


class LabberFile:
    def __init__(self, file_name: str):
        self._h5handle = h5.File(file_name)
        self.metadata = {"file": self._h5handle.filename}
        self._initVariables()
        self._initRawData()

    def _initVariables(self) -> None:
        logged: dict = {
            _decode_if_necessary(var[0]): {"type": "log"}
            for var in self._h5handle["Log list"]
        }
        stepped: dict = {
            _decode_if_necessary(var[0]): {"type": "step"}
            for var in list(self._h5handle["Data/Channel names"])
            if _decode_if_necessary(var[0]) not in logged
        }
        fixed: dict = {
            _decode_if_necessary(var[0]): {"type": "fixed"}
            for var in list(self._h5handle["Step list"])
            if _decode_if_necessary(var[0]) not in stepped
        }
        self.variables = stepped | fixed | logged
        self._initVarInfo()

    def _initVarInfo(self) -> None:

        steps = dict(
            zip(
                [
                    _decode_if_necessary(x[0])
                    for x in self._h5handle["Step list"]
                ],
                list(self._h5handle.attrs["Step dimensions"]),
            )
        )

        self.metadata["steps_list"] = tuple(x for x in steps.values() if x > 1)

        self.metadata["sweep_dimension"] = len(self.metadata["steps_list"])

        channels = {
            _decode_if_necessary(name[0]): i
            for i, name in enumerate(self._h5handle["Data/Channel names"])
        }

        for var_info in self._h5handle["Channels"]:

            var_name = _decode_if_necessary(var_info[0])

            if var_name in self.variables.keys():

                id_num = channels.get(var_name, None)
                instr_name = _decode_if_necessary(var_info[1])
                channel_name = _decode_if_necessary(var_info[2])
                phys_unit = _decode_if_necessary(var_info[3])
                instr_unit = _decode_if_necessary(var_info[4])
                instr_gain = var_info[5]
                instr_offset = var_info[6]
                instr_ampl = var_info[7]
                step = steps.get(var_name, 0)

                path = "Instrument config/" + instr_name
                instr_value = self._h5handle[path].attrs[channel_name]

                if isinstance(instr_value, (int, float, np.float64)):
                    phys_value = (
                        instr_value / instr_ampl - instr_offset
                    ) / instr_gain
                else:
                    phys_value = ""

                self.variables[var_name].update(
                    {
                        "id": id_num,
                        "instr_name": instr_name,
                        "channel_name": channel_name,
                        "phys_unit": phys_unit,
                        "instr_unit": instr_unit,
                        "instr_gain": instr_gain,
                        "instr_offset": instr_offset,
                        "instr_ampl": instr_ampl,
                        "instr_value": instr_value,
                        "phys_value": phys_value,
                        "steps": step,
                    }
                )

    def _initRawData(self) -> None:
        """doc-string"""

        data: np.ndarray = np.array(self._h5handle["Data/Data"])
        """
        if self.metadata["sweep_dimension"] == 1:
            new_shape = self.metadata["steps_list"][0]
        elif self.metadata["sweep_dimension"] > 2:
            steps_list = self.metadata["steps_list"]
            new_shape = (
                steps_list[0],
                steps_list[1],
                (data.shape[2] / steps_list[1]).astype(int),
            )
        elif self.metadata["sweep_dimension"] == 2:
            new_shape = data[:, 0, :].shape
        """

        new_shape = self.metadata["steps_list"]

        for k, var in self.variables.items():

            var_id = var["id"]

            if var_id is None:
                continue

            self.variables[k]["raw_data"] = data[:, var_id, :].reshape(
                new_shape, order="F"
            )

    def get_phys_data(self, var_name):
        var = self.variables.get(var_name, None)
        if var is not None:
            gain = var["instr_gain"]
            offset = var["instr_offset"]
            ampl = var["instr_ampl"]
            data = var.get("raw_data", None)
            if data is not None:
                return (data / ampl - offset) / gain
            else:
                return var["phys_value"]
