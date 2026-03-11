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
    history: list[PortfolioSnapshot] = field(default_factory=list)

    @property
    def total_value(self) -> float:
        return self.cash + sum(
            p.value + p.unrealized_pnl for p in self.positions.values()
        )

    def get_position(self, symbol: str) -> Optional[Position]:
        return self.positions.get(symbol)

    def snapshot(self, timestamp: datetime) -> None:
        """Capture current state for history."""
        positions_value = sum(p.value + p.unrealized_pnl for p in self.positions.values())
        self.history.append(
            PortfolioSnapshot(
                timestamp=timestamp,
                equity=self.total_value,
                cash=self.cash,
                positions_value=positions_value,
            )
        )

    def update_position(self, order: Order, fill_price: float, commission: float) -> None:
        """Update portfolio state after an order fill."""
        cost = order.size * fill_price
        
        if order.side == OrderSide.BUY:
            self.cash -= (cost + commission)
            if order.symbol in self.positions:
                # Average up position
                pos = self.positions[order.symbol]
                new_size = pos.size + order.size
                new_entry = ((pos.entry_price * pos.size) + cost) / new_size
                self.positions[order.symbol] = Position(order.symbol, pos.side, new_entry, new_size)
            else:
                self.positions[order.symbol] = Position(order.symbol, order.side, fill_price, order.size)
        else:
            # Sell logic
            self.cash += (cost - commission)
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                if order.size >= pos.size:
                    self.positions.pop(order.symbol, None)
                else:
                    self.positions[order.symbol] = Position(order.symbol, pos.side, pos.entry_price, pos.size - order.size)
