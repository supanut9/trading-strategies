from datetime import datetime
from strategies.models import Candle, Portfolio, OrderSide
from strategies.rule_based.macd_strategy import MACDStrategy

def test_macd_strategy_buy_signal():
    strategy = MACDStrategy(symbol="BTCUSDT")
    portfolio = Portfolio(initial_capital=10000.0, cash=10000.0)
    
    # We need enough candles to prime the MACD (12, 26, 9)
    # MACD is ready when signal EMA is ready (9 points of MACD line)
    # MACD line is ready when slow EMA is ready (26 points)
    # Total points to be ready: 26 + 9 - 1 = 34
    
    # Generate candles that will cause a bullish crossover
    # Histogram starts negative then becomes positive
    
    # Prime it first with flat prices
    for i in range(35):
        candle = Candle(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=100.0,
            high=100.0,
            low=100.0,
            close=100.0,
            volume=10.0
        )
        strategy.on_candle(candle, portfolio)
    
    # Now prices go up fast to trigger a buy
    prices = [101.0, 102.0, 103.0, 105.0, 110.0, 120.0]
    orders = []
    for price in prices:
        candle = Candle(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=price,
            high=price,
            low=price,
            close=price,
            volume=10.0
        )
        orders.extend(strategy.on_candle(candle, portfolio))
    
    # We should have at least one BUY order
    assert any(order.side.value == "BUY" for order in orders)

def test_macd_strategy_sell_signal():
    strategy = MACDStrategy(symbol="BTCUSDT")
    portfolio = Portfolio(initial_capital=10000.0, cash=10000.0)
    
    # Prime and establish a position
    # Start with flat prices to make histogram near zero
    for i in range(35):
        candle = Candle(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=100.0,
            high=100.0,
            low=100.0,
            close=100.0,
            volume=10.0
        )
        strategy.on_candle(candle, portfolio)
    
    # Then increase price to trigger buy
    for i in range(10):
        candle = Candle(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=100.0 + i,
            high=100.0 + i,
            low=100.0 + i,
            close=100.0 + i,
            volume=10.0
        )
        orders = strategy.on_candle(candle, portfolio)
        for order in orders:
            if order.side == OrderSide.BUY:
                portfolio.update_position(order, candle.close, 0.0)
    # Now prices drop fast to trigger a sell
    prices = [130.0, 120.0, 110.0, 100.0, 90.0, 80.0, 70.0, 60.0, 50.0]
    orders = []
    for price in prices:
        candle = Candle(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=price,
            high=price,
            low=price,
            close=price,
            volume=10.0
        )
        orders.extend(strategy.on_candle(candle, portfolio))
    
    # We should have at least one SELL order
    assert any(order.side.value == "SELL" for order in orders)
