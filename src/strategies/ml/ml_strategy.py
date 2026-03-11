from typing import List, Optional
import joblib
import pandas as pd
import numpy as np
from ..base import AbstractStrategy
from ..indicators import SimpleMovingAverage, RSI
from ..models import Candle, Order, OrderSide, Portfolio


class MLStrategy(AbstractStrategy):
    """
    A strategy that uses a pre-trained ML model (e.g. XGBoost) 
    to predict price direction for each candle.
    """

    def __init__(
        self,
        symbol: str,
        model_path: str,
        position_size: float = 1.0,
    ):
        self._symbol = symbol
        self._model_path = model_path
        self._position_size = position_size
        
        # Load pre-trained model
        self.model = joblib.load(self._model_path)
        
        # Iterative indicators for feature engineering
        self.sma_20 = SimpleMovingAverage(period=20)
        self.sma_50 = SimpleMovingAverage(period=50)
        self.rsi_14 = RSI(period=14)
        
        self._prev_close: Optional[float] = None
        self._returns_history: List[float] = []

    @property
    def name(self) -> str:
        return f"ML_XGBoost_{self._symbol}"

    def on_init(self) -> None:
        self.sma_20 = SimpleMovingAverage(period=20)
        self.sma_50 = SimpleMovingAverage(period=50)
        self.rsi_14 = RSI(period=14)
        self._prev_close = None
        self._returns_history = []

    def on_candle(self, candle: Candle, portfolio: Portfolio) -> List[Order]:
        orders: List[Order] = []
        if candle.symbol != self._symbol:
            return orders

        # 1. Update Indicators
        s20 = self.sma_20.update(candle.close)
        s50 = self.sma_50.update(candle.close)
        r14 = self.rsi_14.update(candle.close)
        
        # Calculate Returns & track history for Volatility
        current_return = 0.0
        if self._prev_close is not None:
            current_return = (candle.close / self._prev_close) - 1
            self._returns_history.append(current_return)
            if len(self._returns_history) > 20:
                self._returns_history.pop(0)

        # 2. Check Readiness
        if not (self.sma_50.is_ready and self.rsi_14.is_ready and len(self._returns_history) >= 20):
            self._prev_close = candle.close
            return orders

        # 3. Build Feature Vector (MUST match training order/calculation)
        volatility = np.std(self._returns_history)
        close_to_sma_20 = (candle.close / s20 - 1) if s20 else 0
        
        # features = ["returns", "sma_20", "sma_50", "volatility_20", "rsi_14", "close_to_sma_20"]
        X = pd.DataFrame([{
            "returns": current_return,
            "sma_20": s20,
            "sma_50": s50,
            "volatility_20": volatility,
            "rsi_14": r14,
            "close_to_sma_20": close_to_sma_20
        }])

        # 4. Predict
        prediction = self.model.predict(X)[0]
        
        # 5. Execute based on Prediction
        position = portfolio.get_position(self._symbol)
        
        if prediction == 1:  # Predict Up -> Go Long
            if not position or position.side != OrderSide.BUY:
                orders.append(self._create_market_order(self._symbol, OrderSide.BUY, self._position_size))
        else:  # Predict Down -> Exit
            if position and position.side == OrderSide.BUY:
                orders.append(self._create_market_order(self._symbol, OrderSide.SELL, self._position_size))

        self._prev_close = candle.close
        return orders
