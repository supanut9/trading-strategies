from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from .models import Candle, Order, OrderSide, OrderType, Portfolio


class AbstractStrategy(ABC):
    """
    The base class that all trading strategies must inherit from.
    This guarantees a uniform interface for the backtest engine and the live bot.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the strategy for reporting and logging."""
        ...

    def on_init(self) -> None:
        """
        Called once before the engine starts feeding candles.
        Use this to initialize state, load models, or start indicator buffers.
        """
        pass

    @abstractmethod
    def on_candle(self, candle: Candle, portfolio: Portfolio) -> List[Order]:
        """
        The core engine loop. Called for every new candle.

        Args:
            candle: The newest market candle.
            portfolio: The current state of positions and cash.

        Returns:
            A list of new orders to execute. Return an empty list to do nothing.
        """
        ...

    def on_stop(self) -> None:
        """
        Called after the backtest ends or before the live bot shuts down.
        Use this for cleanup, saving metric tracking, or closing models.
        """
        pass

    # Helper methods for creating orders easily
    def _create_market_order(
        self, symbol: str, side: OrderSide, size: float, timestamp: datetime = None
    ) -> Order:
        return Order(
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            size=size,
            timestamp=timestamp,
        )

    def _create_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        size: float,
        price: float,
        timestamp: datetime = None,
    ) -> Order:
        return Order(
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            size=size,
            price=price,
            timestamp=timestamp,
        )
