from app.engines.liquidity.LiquidityMapEngine import LiquidityMapEngine
import pytest


def test_liquidity_map_detects_levels_and_distances():
    result = LiquidityMapEngine.build(
        {
            "currentPrice": 1.3480,
            "pdh": 1.3500,
            "pdl": 1.3400,
            "pwh": 1.3600,
            "pwl": 1.3300,
            "h4Candles": [
                {"high": 1.3440, "low": 1.3390},
                {"high": 1.3460, "low": 1.3380},
                {"high": 1.3520, "low": 1.3340},
                {"high": 1.3470, "low": 1.3360},
                {"high": 1.3450, "low": 1.3370},
                {"high": 1.3490, "low": 1.3330},
                {"high": 1.3480, "low": 1.3350},
            ],
        }
    )

    assert result["pdh"]["level"] == 1.3500
    assert result["pdl"]["level"] == 1.3400
    assert result["pwh"]["level"] == 1.3600
    assert result["pwl"]["level"] == 1.3300
    assert result["h4SwingHigh"]["level"] == 1.3520
    assert result["h4SwingLow"]["level"] == 1.3340

    assert result["pdh"]["distance"] == pytest.approx(0.002, abs=1e-9)
    assert result["pdl"]["distance"] == pytest.approx(0.008, abs=1e-9)


def test_liquidity_map_marks_taken_levels():
    result = LiquidityMapEngine.build(
        {
            "currentPrice": 1.3290,
            "pdh": 1.3500,
            "pdl": 1.3400,
            "pwh": 1.3600,
            "pwl": 1.3300,
            "h4Candles": [
                {"high": 1.3500, "low": 1.3340},
                {"high": 1.3490, "low": 1.3330},
                {"high": 1.3510, "low": 1.3350},
                {"high": 1.3480, "low": 1.3320},
                {"high": 1.3470, "low": 1.3310},
            ],
        }
    )

    assert result["pdl"]["taken"] is True
    assert result["pwl"]["taken"] is True
    assert "PDL" in result["liquidityTaken"]["sellSideTaken"]
    assert "PWL" in result["liquidityTaken"]["sellSideTaken"]


def test_liquidity_map_computes_nearest_bsl_and_ssl():
    result = LiquidityMapEngine.build(
        {
            "currentPrice": 1.3450,
            "pdh": 1.3500,
            "pdl": 1.3400,
            "pwh": 1.3520,
            "pwl": 1.3380,
            "h4Candles": [
                {"high": 1.3430, "low": 1.3390},
                {"high": 1.3440, "low": 1.3385},
                {"high": 1.3490, "low": 1.3370},
                {"high": 1.3460, "low": 1.3380},
                {"high": 1.3455, "low": 1.3388},
                {"high": 1.3470, "low": 1.3365},
                {"high": 1.3462, "low": 1.3374},
            ],
        }
    )

    assert result["nearestBuySideLiquidity"]["name"] == "H4_SWING_HIGH"
    assert result["nearestSellSideLiquidity"]["name"] == "PDL"
