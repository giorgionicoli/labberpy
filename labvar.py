import numpy as np

from typing import Dict


class LabVar(np.ndarray):
    def __new__(
        cls, input_array: np.ndarray, label: str = "", metadata: Dict = dict()
    ):
        obj = np.asarray(input_array).view(cls)
        obj.label = label
        obj.metadata = metadata
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.label = getattr(obj, "label", "")
        self.metadata = getattr(obj, "metadata", dict())
