# trading-strategies

Shared strategy library — used by both the backtest engine and the live trading bot.

## Tech Stack
- **Python 3.12+** with `numpy`, `scikit-learn`, `gRPC`
- Uses `uv` for package management

## Strategies
- **Rule-based:** SMA crossover, RSI mean reversion, breakout, grid
- **ML-based:** LSTM signal, XGBoost classifier (added in Stage 2)

## Usage
```python
from strategies.rule_based.sma_cross import SmaCrossStrategy

strategy = SmaCrossStrategy(symbol="BTC/USDT", fast_period=10, slow_period=30)
orders = strategy.on_candle(candle, portfolio)
```
