class Label:
    def __init__(
        self,
        name: str = "",
        symbol: str = "",
        unit: str = "",
    ):
        self.name = name
        self.symbol = symbol
        self.unit = unit

    @property
    def label(self):
        return fr"{self.name} {self.symbol} ({self.unit})"

    def __repr__(self):
        return fr"Label('{self.name}', '{self.symbol}', '{self.unit}')"

    def __str__(self):
        return self.label
