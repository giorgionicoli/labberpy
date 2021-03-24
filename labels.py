class Label:
    def __init__(
        self,
        name: str = "",
        symbol: str = "",
        unit: str = "",
        prefix: str = "",
        subscript: str = "",
        superscript: str = "",
        multiplier: str = "",
    ):
        self.name = name
        self.symbol = symbol
        self.unit = unit
        self.prefix = prefix
        self.subscript = subscript
        self.superscript = superscript
        self.multiplier = multiplier

    @property
    def label(self):
        name = self.name
        if self.prefix:
            name = self.prefix + " " + name

        symbol = fr"${self.symbol}"
        if self.subscript:
            symbol += fr"_\mathrm{{{self.subscript}}}"
        if self.superscript:
            symbol += fr"^\mathrm{{{self.superscript}}}"
        symbol += "$"

        unit = self.unit
        if self.multiplier:
            unit = self.multiplier + unit

        return fr"{name} {symbol} ({unit})"

    def __repr__(self):
        obj_repr = [f"{k}='{v}'" for k, v in vars(self).items()]
        obj_repr = "Label(" + ", ".join(obj_repr) + ")"
        return obj_repr

    def __str__(self):
        return self.label
