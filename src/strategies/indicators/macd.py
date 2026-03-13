from typing import Tuple

from .moving_avg import ExponentialMovingAverage


class MACD:
    """
    Moving Average Convergence Divergence (MACD) indicator.
    Consists of:
    - MACD Line (12 EMA - 26 EMA)
    - Signal Line (9 EMA of MACD Line)
    - Histogram (MACD Line - Signal Line)
    """

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_ema = ExponentialMovingAverage(fast_period)
        self.slow_ema = ExponentialMovingAverage(slow_period)
        self.signal_ema = ExponentialMovingAverage(signal_period)
        
        self.macd_line: float | None = None
        self.signal_line: float | None = None
        self.histogram: float | None = None

    @property
    def is_ready(self) -> bool:
        return self.signal_ema.is_ready

    def update(self, price: float) -> Tuple[float | None, float | None, float | None]:
        fast = self.fast_ema.update(price)
        slow = self.slow_ema.update(price)

        if fast is not None and slow is not None:
            self.macd_line = fast - slow
            self.signal_line = self.signal_ema.update(self.macd_line)
            
            if self.signal_line is not None:
                self.histogram = self.macd_line - self.signal_line
        
        return self.macd_line, self.signal_line, self.histogram
