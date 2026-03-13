from strategies.indicators.bollinger_bands import BollingerBands

def test_bollinger_bands():
    # Use small period for testing
    bb = BollingerBands(period=3, std_dev=2.0)
    
    # 1. Warm up
    assert bb.update(100.0) is None
    assert bb.update(100.0) is None
    
    # 2. 3rd value -> Middle should be 100, Std should be 0
    bands = bb.update(100.0)
    assert bands is not None
    upper, middle, lower = bands
    assert middle == 100.0
    assert upper == 100.0
    assert lower == 100.0
    
    # 3. Increase volatility
    # Prices: [100, 100, 130] -> Mean = 110, Std = sqrt((10^2 + 10^2 + 20^2)/3) = sqrt(600/3) = sqrt(200) approx 14.14
    bands = bb.update(130.0)
    assert bands is not None
    upper, middle, lower = bands
    assert middle == 110.0
    assert upper > 110.0
    assert lower < 110.0
