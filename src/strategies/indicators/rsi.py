from typing import Optional


class RSI:
    """
    Relative Strength Index (RSI) indicator.
    Uses Wilder's smoothing method (standard in trading charts).
    Calculates iteratively for O(1) per update.
    """

    def __init__(self, period: int = 14):
        if period < 1:
            raise ValueError("Period must be at least 1")
        self.period = period
        self._prices: list[tuple[float, float]] = []
        self._avg_gain: Optional[float] = None
        self._avg_loss: Optional[float] = None
        self._last_price: Optional[float] = None

    @property
    def value(self) -> Optional[float]:
        """Returns the current RSI value (0-100), or None if not ready."""
        if self._avg_gain is None or self._avg_loss is None:
            return None
        
        if self._avg_loss == 0:
            return 100.0
        
        rs = self._avg_gain / self._avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    @property
    def is_ready(self) -> bool:
        """Returns True if the indicator has enough data points to output a value."""
        return self._avg_gain is not None and self._avg_loss is not None

    def update(self, price: float) -> Optional[float]:
        """Adds a new price point to the RSI calculation."""
        if self._last_price is None:
            self._last_price = price
            return None

        gain = max(0, price - self._last_price)
        loss = max(0, self._last_price - price)
        self._last_price = price

        # Phase 1: Not enough data for initial average
        if self._avg_gain is None or self._avg_loss is None:
            self._prices.append((gain, loss))
            if len(self._prices) == self.period:
                # Calculate initial simple averages
                self._avg_gain = sum(g for g, _ in self._prices) / self.period
                self._avg_loss = sum(loss for _, loss in self._prices) / self.period
        else:
            # Phase 2: Wilder's smoothing
            # AvgGain = ((PrevAvgGain * (period-1)) + CurrentGain) / period
            self._avg_gain = (self._avg_gain * (self.period - 1) + gain) / self.period
            self._avg_loss = (self._avg_loss * (self.period - 1) + loss) / self.period

        return self.value
