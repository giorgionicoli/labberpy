from labels import Label


class LabVariable:
    def __init__(self, data):
        self.data = data
        self.label = None
        self.metadata = {
            "filename": "",
        }

    def __add__(self, other):
        data1 = self.data

        if isinstance(other, LabVariable):
            data2 = other.data
        else:
            data2 = other

        return LabVariable(data1+data2)


    # LabberFile could decide which autolabel to use (if any) by
    # looking at the units of the variable
    def make_label(
        self,
        quantity: str = "",
        symbol: str = "",
        units: str = "",
        plotgain: float = 1.0,
        autolabel: str = "",
        update: bool = False,
    ):
        if (not self.label) or update:
            if not autolabel:
                self.label = Label(quantity, symbol, units, plotgain)
            else:
                self.label = Label.autolabel(autolabel, plotgain)
        else:
            print("Label already present. Can't update without permission.")
            print("Set 'update = True' to set a new label")
