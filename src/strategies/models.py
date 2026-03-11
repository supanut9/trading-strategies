from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


@dataclass
class Candle:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Order:
    symbol: str
    side: OrderSide
    order_type: OrderType
    size: float
    price: Optional[float] = None
    timestamp: Optional[datetime] = None


@dataclass
class Position:
    symbol: str
    side: OrderSide
    entry_price: float
    size: float
    unrealized_pnl: float = 0.0

    @property
    def value(self) -> float:
        return self.size * self.entry_price

    def mark_to_market(self, current_price: float) -> None:
        if self.side == OrderSide.BUY:
            self.unrealized_pnl = (current_price - self.entry_price) * self.size
        else:
            self.unrealized_pnl = (self.entry_price - current_price) * self.size


@dataclass
class PortfolioSnapshot:
    timestamp: datetime
    equity: float
    cash: float
    positions_value: float


@dataclass
class Portfolio:
    initial_capital: float
    cash: float
    positions: dict[str, Position] = field(default_factory=dict)
    
    @property
    def total_equity(self) -> float:
        return self.cash + sum(p.value + p.unrealized_pnl for p in self.positions.values())

    def get_position(self, symbol: str) -> Optional[Position]:
        return self.positions.get(symbol)
