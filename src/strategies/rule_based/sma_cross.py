from typing import List

from ..base import AbstractStrategy
from ..indicators.moving_avg import SimpleMovingAverage
from ..models import Candle, Order, OrderSide, Portfolio


class SmaCrossStrategy(AbstractStrategy):
    """
    A classic trend-following strategy.

    Buys when the fast SMA crosses ABOVE the slow SMA.
    Sells when the fast SMA crosses BELOW the slow SMA.
    """

    def __init__(
        self,
        symbol: str,
        fast_period: int = 10,
        slow_period: int = 30,
        position_size: float = 1.0,
    ):
        self._symbol = symbol
        self._fast_period = fast_period
        self._slow_period = slow_period
        self._position_size = position_size

        self.fast_sma = SimpleMovingAverage(period=self._fast_period)
        self.slow_sma = SimpleMovingAverage(period=self._slow_period)

        self._prev_fast: float | None = None
        self._prev_slow: float | None = None

    @property
    def name(self) -> str:
        return f"SMA_Cross_{self._fast_period}_{self._slow_period}"

    def on_init(self) -> None:
        # Reset indicators and state
        self.fast_sma = SimpleMovingAverage(period=self._fast_period)
        self.slow_sma = SimpleMovingAverage(period=self._slow_period)
        self._prev_fast = None
        self._prev_slow = None

    def on_candle(self, candle: Candle, portfolio: Portfolio) -> List[Order]:
        orders: List[Order] = []

        # Only process candles for our target symbol
        if candle.symbol != self._symbol:
            return orders

        # Update indicators
        current_fast = self.fast_sma.update(candle.close)
        current_slow = self.slow_sma.update(candle.close)

        # Wait for the slow SMA to warm up before generating signals
        if not self.slow_sma.is_ready:
            return orders

        # Need previous values to detect a CROSSOVER (not just "is greater than")
        prev_fast = self._prev_fast
        prev_slow = self._prev_slow

        if (
            prev_fast is not None
            and prev_slow is not None
            and current_fast is not None
            and current_slow is not None
        ):
            position = portfolio.get_position(self._symbol)

            # Golden Cross: Fast crosses ABOVE Slow -> BUY
            if prev_fast <= prev_slow and current_fast > current_slow:
                if not position or position.side != OrderSide.BUY:
                    # If we hold a short, close it first (simplified for this strategy: just go long)
                    orders.append(
                        self._create_market_order(
                            symbol=candle.symbol,
                            side=OrderSide.BUY,
                            size=self._position_size,
                            timestamp=candle.timestamp,
                        )
                    )

            # Death Cross: Fast crosses BELOW Slow -> SELL
            elif prev_fast >= prev_slow and current_fast < current_slow:
                # If we have a long position, flat it. Or if we allow shorts, short it.
                # Assuming this goes flat if long.
                if position and position.side == OrderSide.BUY:
                    orders.append(
                        self._create_market_order(
                            symbol=candle.symbol,
                            side=OrderSide.SELL,
                            size=self._position_size,  # For now just selling identical size
                            timestamp=candle.timestamp,
                        )
                    )

        # Keep state for next candle
        self._prev_fast = current_fast
        self._prev_slow = current_slow

        return orders
