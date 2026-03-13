from datetime import datetime
from strategies.rule_based.rsi_strategy import RSIStrategy
from strategies.models import Candle, Portfolio, OrderSide

def test_rsi_strategy():
    strategy = RSIStrategy(symbol="BTC/USDT", period=2, oversold=30, overbought=70)
    portfolio = Portfolio(initial_capital=100000.0, cash=100000.0)
    
    # 1. Warm up RSI
    c1 = Candle(symbol="BTC/USDT", timestamp=datetime.now(), open=100, high=110, low=90, close=100, volume=1)
    c2 = Candle(symbol="BTC/USDT", timestamp=datetime.now(), open=100, high=110, low=90, close=110, volume=1)
    
    orders = strategy.on_candle(c1, portfolio)
    assert len(orders) == 0
    
    orders = strategy.on_candle(c2, portfolio)
    assert len(orders) == 0
    
    # 3. Trigger Oversold (Price drops sharply)
    c3 = Candle(symbol="BTC/USDT", timestamp=datetime.now(), open=110, high=110, low=50, close=50, volume=1)
    orders = strategy.on_candle(c3, portfolio)
    
    # RSI(2) will be very low
    assert len(orders) == 1
    assert orders[0].side == OrderSide.BUY
    
    # Mock portfolio update (BUY)
    order = orders[0]
    portfolio.update_position(order, fill_price=50.0, commission=0.0)
    
    # 4. Trigger Overbought (Price jumps sharply)
    c4 = Candle(symbol="BTC/USDT", timestamp=datetime.now(), open=50, high=200, low=50, close=200, volume=1)
    orders = strategy.on_candle(c4, portfolio)
    
    assert len(orders) == 1
    assert orders[0].side == OrderSide.SELL
