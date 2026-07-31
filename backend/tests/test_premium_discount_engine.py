from app.engines.premium_discount.PremiumDiscountEngine import PremiumDiscountEngine


def test_premium_discount_engine_all_rules_pass_bullish_discount():
    result = PremiumDiscountEngine.evaluate(
        {
            "currentPrice": 1.3410,
            "rangeHigh": 1.3500,
            "rangeLow": 1.3400,
            "bias": "BULLISH",
        }
    )

    assert result["valid"] is True
    assert result["zone"] == "DISCOUNT"
    assert result["biasAligned"] is True
    assert result["passedRules"] == ["PD-001", "PD-002", "PD-003", "PD-004", "PD-005"]
    assert result["failedRules"] == []


def test_premium_discount_engine_fails_when_range_invalid():
    result = PremiumDiscountEngine.evaluate(
        {
            "currentPrice": 1.3450,
            "rangeHigh": 1.3400,
            "rangeLow": 1.3500,
            "bias": "BEARISH",
        }
    )

    assert result["valid"] is False
    assert result["zone"] == "UNKNOWN"
    assert "PD-001" in result["failedRules"]
    assert "PD-003" in result["failedRules"]
    assert "PD-004" in result["failedRules"]
    assert "PD-005" in result["failedRules"]


def test_premium_discount_engine_fails_when_price_outside_range():
    result = PremiumDiscountEngine.evaluate(
        {
            "currentPrice": 1.3550,
            "rangeHigh": 1.3500,
            "rangeLow": 1.3400,
            "bias": "BEARISH",
        }
    )

    assert result["valid"] is False
    assert "PD-002" in result["failedRules"]


def test_premium_discount_engine_bias_alignment_rules():
    bearish_misaligned = PremiumDiscountEngine.evaluate(
        {
            "currentPrice": 1.3410,
            "rangeHigh": 1.3500,
            "rangeLow": 1.3400,
            "bias": "BEARISH",
        }
    )

    neutral_aligned = PremiumDiscountEngine.evaluate(
        {
            "currentPrice": 1.3490,
            "rangeHigh": 1.3500,
            "rangeLow": 1.3400,
            "bias": "NEUTRAL",
        }
    )

    assert bearish_misaligned["zone"] == "DISCOUNT"
    assert "PD-005" in bearish_misaligned["failedRules"]

    assert neutral_aligned["biasAligned"] is True
    assert "PD-005" in neutral_aligned["passedRules"]
