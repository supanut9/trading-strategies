from typing import List

from .base import AbstractStrategy
from .models import Candle, Order, OrderSide, Portfolio


class EnsembleStrategy(AbstractStrategy):
    """
    A strategy that combines multiple strategies.
    It returns a BUY signal only if a majority of strategies suggest BUY.
    It returns a SELL signal if any strategy suggests SELL (risk-averse).
    """

    def __init__(self, strategies: List[AbstractStrategy]):
        self.strategies = strategies

    @property
    def name(self) -> str:
        names = [s.name for s in self.strategies]
        return f"Ensemble({', '.join(names)})"

    def on_init(self) -> None:
        for s in self.strategies:
            s.on_init()

    def on_candle(self, candle: Candle, portfolio: Portfolio) -> List[Order]:
        all_orders: List[Order] = []
        buy_votes = 0
        sell_votes = 0

        for s in self.strategies:
            orders = s.on_candle(candle, portfolio)
            for order in orders:
                if order.side == OrderSide.BUY:
                    buy_votes += 1
                elif order.side == OrderSide.SELL:
                    sell_votes += 1

        # Logic for ensemble signal:
        # 1. Majority vote for BUY
        # 2. Risk-averse: any SELL signal triggers a SELL
        
        position = portfolio.get_position(candle.symbol)
        
        if sell_votes > 0:
            if position and position.side == OrderSide.BUY:
                return [self._create_market_order(candle.symbol, OrderSide.SELL, 1.0, candle.timestamp)]
        
        if buy_votes >= len(self.strategies) / 2 and buy_votes > 0:
            if not position or position.side != OrderSide.BUY:
                return [self._create_market_order(candle.symbol, OrderSide.BUY, 1.0, candle.timestamp)]
        
        return []

    def on_stop(self) -> None:
        for s in self.strategies:
            s.on_stop()
