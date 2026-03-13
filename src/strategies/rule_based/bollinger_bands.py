from typing import List
from ..base import AbstractStrategy
from ..indicators.bollinger_bands import BollingerBands
from ..models import Candle, Order, OrderSide, Portfolio


class BollingerBandsStrategy(AbstractStrategy):
    """
    Bollinger Bands Reversion Strategy.
    - BUY when price touches or drops below Lower Band.
    - SELL when price touches or rises above Upper Band.
    """

    def __init__(
        self,
        symbol: str,
        period: int = 20,
        std_dev: float = 2.0,
        position_size: float = 1.0,
    ):
        self._symbol = symbol
        self._period = period
        self._std_dev = std_dev
        self._position_size = position_size
        self.bb = BollingerBands(period=self._period, std_dev=self._std_dev)

    @property
    def name(self) -> str:
        return f"BollingerBands_{self._period}_{self._std_dev}"

    def on_init(self) -> None:
        self.bb = BollingerBands(period=self._period, std_dev=self._std_dev)

    def on_candle(self, candle: Candle, portfolio: Portfolio) -> List[Order]:
        orders: List[Order] = []
        if candle.symbol != self._symbol:
            return orders

        bands = self.bb.update(candle.close)
        if not self.bb.is_ready or bands is None:
            return orders

        upper, middle, lower = bands
        position = portfolio.get_position(self._symbol)

        # 1. Entry Logic: Price drops below lower band -> Mean Reversion BUY
        if candle.close <= lower:
            if not position or position.side != OrderSide.BUY:
                orders.append(
                    self._create_market_order(
                        symbol=candle.symbol,
                        side=OrderSide.BUY,
                        size=self._position_size,
                        timestamp=candle.timestamp,
                    )
                )

        # 2. Exit Logic: Price rises above upper band -> Mean Reversion SELL
        elif candle.close >= upper:
            if position and position.side == OrderSide.BUY:
                orders.append(
                    self._create_market_order(
                        symbol=candle.symbol,
                        side=OrderSide.SELL,
                        size=self._position_size,
                        timestamp=candle.timestamp,
                    )
                )

        return orders
