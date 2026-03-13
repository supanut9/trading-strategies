from typing import List, Optional

from ..base import AbstractStrategy
from ..indicators.macd import MACD
from ..models import Candle, Order, OrderSide, Portfolio


class MACDStrategy(AbstractStrategy):
    """
    A trend-following strategy that uses MACD crossovers.
    - BUY when MACD line crosses ABOVE the signal line (Histogram becomes positive).
    - SELL when MACD line crosses BELOW the signal line (Histogram becomes negative).
    """

    def __init__(
        self,
        symbol: str,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        position_size: float = 1.0,
    ):
        self._symbol = symbol
        self._position_size = position_size
        self.macd = MACD(fast_period, slow_period, signal_period)
        self._prev_histogram: Optional[float] = None

    @property
    def name(self) -> str:
        return f"MACD_{self._symbol}"

    def on_candle(self, candle: Candle, portfolio: Portfolio) -> List[Order]:
        orders: List[Order] = []
        if candle.symbol != self._symbol:
            return orders

        _, _, histogram = self.macd.update(candle.close)

        if not self.macd.is_ready or self._prev_histogram is None:
            self._prev_histogram = histogram
            return orders

        position = portfolio.get_position(self._symbol)

        # Buy Signal: MACD crosses ABOVE signal line
        if self._prev_histogram <= 0 and histogram > 0:
            if not position or position.side != OrderSide.BUY:
                orders.append(
                    self._create_market_order(
                        self._symbol, OrderSide.BUY, self._position_size, candle.timestamp
                    )
                )

        # Sell Signal: MACD crosses BELOW signal line
        elif self._prev_histogram >= 0 and histogram < 0:
            if position and position.side == OrderSide.BUY:
                orders.append(
                    self._create_market_order(
                        self._symbol, OrderSide.SELL, self._position_size, candle.timestamp
                    )
                )

        self._prev_histogram = histogram
        return orders
