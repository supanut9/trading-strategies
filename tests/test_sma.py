from strategies.indicators.moving_avg import SimpleMovingAverage


def test_simple_moving_average() -> None:
    sma = SimpleMovingAverage(period=3)

    # Not enough data yet
    assert sma.update(10.0) is None
    assert sma.update(20.0) is None

    # 3rd candle -> Average of (10 + 20 + 30) / 3 = 20
    assert sma.update(30.0) == 20.0

    # 4th candle -> (20 + 30 + 40) / 3 = 30
    assert sma.update(40.0) == 30.0
