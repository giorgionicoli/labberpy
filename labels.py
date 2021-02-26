class Label:
    def __init__(
        self,
        quantity: str = "",
        symbol: str = "",
        units: str = "",
        plotgain: float = 1.0,
    ):
        self.quantity = quantity
        self.symbol = symbol
        self.units = units
        self.plotgain = plotgain

    def __repr__(self):
        pass

    @classmethod
    def autolabel(cls, autolabel: str = "", plotgain: float = 1.0):
        # should this method call the proper classmethod?
        pass

    @classmethod
    def tesla(cls, plotgain: float = 1.0):
        label_pieces = {
            "quantity": "Magnetic Field",
            "symbol": "$B$",
            "units": "T",
            "plotgain": plotgain,
        }
        return cls(**label_pieces)

    @classmethod
    def volt(cls):
        pass

    @classmethod
    def ohm(cls):
        pass

    @classmethod
    def ampere(cls):
        pass
