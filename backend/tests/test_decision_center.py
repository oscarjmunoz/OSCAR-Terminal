from datetime import datetime
from types import SimpleNamespace

from app.schemas.decision import DecisionContext
from app.schemas.decision import TradeSide
from app.schemas.decision_center import RecommendationType
from app.services.decision_center import DecisionCenter
from app.services import decision_center as decision_center_module


def _build_candle(index: int, open_price: float, close_price: float, high: float, low: float, volume: int):
    return SimpleNamespace(
        time=datetime(2026, 8, 3, 9, index % 60, 0),
        open=open_price,
        close=close_price,
        high=high,
        low=low,
        tick_volume=volume,
    )


def _mock_market_and_structure(monkeypatch):
    tick = SimpleNamespace(symbol="USDCHF.pro", bid=1.1000, ask=1.1002, spread=2.0)

    candles = []
    price = 1.1002
    for i in range(58):
        base = 1.0980 + (i * 0.00003)
        candles.append(_build_candle(i, base, base + 0.00010, base + 0.00020, base - 0.00010, 120 + i))

    # Create a bullish FVG around current price and a sweep on the final candle.
    candles.append(_build_candle(58, 1.0990, 1.0988, 1.0990, 1.0985, 260))
    candles.append(_build_candle(59, 1.0992, 1.0994, 1.0996, 1.0991, 280))
    candles.append(_build_candle(60, 1.1000, 1.1001, 1.1012, 1.1000, 450))

    structure = SimpleNamespace(
        trend="BULLISH",
        bos=True,
        choch=False,
        mss=True,
        last_high=1.1012,
        last_low=1.0985,
    )

    monkeypatch.setattr(decision_center_module.MarketService, "latest_tick", classmethod(lambda cls, symbol: tick))
    monkeypatch.setattr(decision_center_module.MarketService, "candles", classmethod(lambda cls, symbol, timeframe, count=120: candles))
    monkeypatch.setattr(
        decision_center_module.SmartMoneyService,
        "structure",
        staticmethod(lambda symbol, timeframe="M5", candles=300, left=3, right=3: structure),
    )

    return price


def test_decision_report_is_generated(monkeypatch):
    _mock_market_and_structure(monkeypatch)
    decision = DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.10, sl=1.0992, tp=1.1022)

    report = DecisionCenter.build_report(decision)

    assert report.context.symbol == "USDCHF.pro"
    assert report.market_bias.bias.value == "BULLISH"
    assert report.institutional_score.score >= 0
    assert report.risk_assessment.rr_expected > 0


def test_narrative_contains_professional_sections(monkeypatch):
    _mock_market_and_structure(monkeypatch)
    decision = DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.10, sl=1.0992, tp=1.1022)

    report = DecisionCenter.build_report(decision)

    assert "sesgo" in report.narrative.lower()
    assert "liquidez" in report.narrative.lower()
    assert "decision final corresponde al trader" in report.narrative.lower()


def test_checklist_contains_expected_items(monkeypatch):
    _mock_market_and_structure(monkeypatch)
    decision = DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.10, sl=1.0992, tp=1.1022)

    report = DecisionCenter.build_report(decision)
    labels = {item.label for item in report.execution_checklist}

    assert "Liquidity taken" in labels
    assert "BOS confirmed" in labels
    assert "FVG mitigated" in labels
    assert "Institutional zone" in labels
    assert "Risk valid" in labels
    assert "No contradictions" in labels


def test_recommendation_is_buy_when_confluence_is_strong(monkeypatch):
    _mock_market_and_structure(monkeypatch)
    decision = DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.10, sl=1.0992, tp=1.1032)

    report = DecisionCenter.build_report(decision)

    assert report.final_recommendation.recommendation == RecommendationType.BUY
    assert len(report.final_recommendation.explanation) > 20


def test_risk_assessment_calculates_rr_and_risk(monkeypatch):
    _mock_market_and_structure(monkeypatch)
    decision = DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.10, sl=1.0990, tp=1.1030)

    report = DecisionCenter.build_report(decision)

    assert report.risk_assessment.rr_expected >= 1.5
    assert report.risk_assessment.risk_percent > 0
    assert report.risk_assessment.risk in {"LOW", "MEDIUM", "HIGH"}


def test_confluences_include_detected_and_not_detected(monkeypatch):
    _mock_market_and_structure(monkeypatch)
    decision = DecisionContext(symbol="USDCHF.pro", side=TradeSide.BUY, volume=0.10, sl=1.0992, tp=1.1022)

    report = DecisionCenter.build_report(decision)

    detected_flags = [item.detected for item in report.confluences]
    assert any(detected_flags)
    assert any(not flag for flag in detected_flags)
    assert all(item.importance.value in {"HIGH", "MEDIUM", "LOW"} for item in report.confluences)
