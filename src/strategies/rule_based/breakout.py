from typing import List

from ..base import AbstractStrategy
from ..models import Candle, Order, OrderSide, Portfolio


class BreakoutStrategy(AbstractStrategy):
    """
    A simple breakout strategy.
    
    Buys when the price breaks above the N-period high.
    Sells when the price breaks below the N-period low.
    """

    def __init__(
        self,
        symbol: str,
        period: int = 20,
        position_size: float = 1.0,
    ):
        self._symbol = symbol
        self._period = period
        self._position_size = position_size
        
        self._highs: List[float] = []
        self._lows: List[float] = []

    @property
    def name(self) -> str:
        return f"Breakout_{self._period}"

    def on_init(self) -> None:
        self._highs = []
        self._lows = []

    def on_candle(self, candle: Candle, portfolio: Portfolio) -> List[Order]:
        orders: List[Order] = []

        if candle.symbol != self._symbol:
            return orders

        # Need at least self._period candles to detect a breakout
        if len(self._highs) < self._period:
            self._highs.append(candle.high)
            self._lows.append(candle.low)
            return orders

        # Current resistance and support (excluding the latest candle which we just got)
        resistance = max(self._highs)
        support = min(self._lows)

        position = portfolio.get_position(self._symbol)

        # Breakout ABOVE Resistance -> BUY
        if candle.close > resistance:
            if not position or position.side != OrderSide.BUY:
                orders.append(
                    self._create_market_order(
                        symbol=candle.symbol,
                        side=OrderSide.BUY,
                        size=self._position_size,
                    )
                )

        # Breakout BELOW Support -> SELL
        elif candle.close < support:
            if position and position.side == OrderSide.BUY:
                orders.append(
                    self._create_market_order(
                        symbol=candle.symbol,
                        side=OrderSide.SELL,
                        size=self._position_size,
                    )
                )

        # Maintain window
        self._highs.append(candle.high)
        self._lows.append(candle.low)
        if len(self._highs) > self._period:
            self._highs.pop(0)
            self._lows.pop(0)

        return orders
