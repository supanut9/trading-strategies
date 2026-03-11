from typing import List

from ..base import AbstractStrategy
from ..indicators.rsi import RSI
from ..models import Candle, Order, OrderSide, Portfolio


class RSIStrategy(AbstractStrategy):
    """
    A mean-reversion strategy based on the RSI indicator.
    
    Buys when RSI is oversold (< 30).
    Sells when RSI is overbought (> 70).
    """

    def __init__(
        self,
        symbol: str,
        period: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
        position_size: float = 1.0,
    ):
        self._symbol = symbol
        self._period = period
        self._oversold = oversold
        self._overbought = overbought
        self._position_size = position_size
        
        self.rsi = RSI(period=self._period)

    @property
    def name(self) -> str:
        return f"RSI_{self._period}_{self._oversold}_{self._overbought}"

    def on_init(self) -> None:
        self.rsi = RSI(period=self._period)

    def on_candle(self, candle: Candle, portfolio: Portfolio) -> List[Order]:
        orders: List[Order] = []

        if candle.symbol != self._symbol:
            return orders

        current_rsi = self.rsi.update(candle.close)
        
        if not self.rsi.is_ready or current_rsi is None:
            return orders

        position = portfolio.get_position(self._symbol)

        # Oversold -> BUY (Mean Reversion)
        if current_rsi < self._oversold:
            if not position or position.side != OrderSide.BUY:
                orders.append(
                    self._create_market_order(
                        symbol=candle.symbol,
                        side=OrderSide.BUY,
                        size=self._position_size,
                    )
                )

        # Overbought -> SELL (Mean Reversion)
        elif current_rsi > self._overbought:
            if position and position.side == OrderSide.BUY:
                orders.append(
                    self._create_market_order(
                        symbol=candle.symbol,
                        side=OrderSide.SELL,
                        size=self._position_size,
                    )
                )

        return orders
