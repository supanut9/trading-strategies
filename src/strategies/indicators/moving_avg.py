
class SimpleMovingAverage:
    """
    A lightweight, iterative Simple Moving Average (SMA) indicator.
    Calculates efficiently as new candles stream in (O(1) time complexity) 
    instead of recalculating across the whole history.
    """
    
    def __init__(self, period: int):
        if period < 1:
            raise ValueError("Period must be at least 1")
        self.period = period
        self._window: list[float] = []
        self._sum = 0.0

    @property
    def value(self) -> float | None:
        """Returns the current SMA value, or None if the period isn't reached yet."""
        if len(self._window) < self.period:
            return None
        return self._sum / self.period

    @property
    def is_ready(self) -> bool:
        """Returns True if the indicator has enough data points to output a value."""
        return len(self._window) == self.period

    def update(self, price: float) -> float | None:
        """Adds a new price point to the SMA calculation."""
        self._window.append(price)
        self._sum += price

        if len(self._window) > self.period:
            # Remove the oldest element
            oldest = self._window.pop(0)
            self._sum -= oldest
            
        return self.value
