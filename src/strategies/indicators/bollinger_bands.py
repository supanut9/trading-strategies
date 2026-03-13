import numpy as np
from typing import Optional, Tuple


class BollingerBands:
    """
    Bollinger Bands indicator.
    Consists of a Middle Band (SMA), Upper Band, and Lower Band.
    """

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
        self.values: list[float] = []
        self.is_ready = False

    def update(self, price: float) -> Optional[Tuple[float, float, float]]:
        """
        Update the indicator with a new price.
        Returns (Upper, Middle, Lower) or None if not ready.
        """
        self.values.append(price)
        if len(self.values) > self.period:
            self.values.pop(0)

        if len(self.values) == self.period:
            self.is_ready = True
            middle_band = np.mean(self.values)
            std = np.std(self.values)
            upper_band = middle_band + (self.std_dev * std)
            lower_band = middle_band - (self.std_dev * std)
            return (float(upper_band), float(middle_band), float(lower_band))

        return None
