from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.scanner.models import OpportunityStage
from app.scanner.schemas import OpportunitySnapshotSchema
from app.scanner import router as scanner_router_module


def test_scanner_opportunities_endpoint(monkeypatch):
    monkeypatch.setattr(scanner_router_module._scheduler, "start", lambda: None)
    monkeypatch.setattr(scanner_router_module._scheduler, "stop", lambda: None)

    sample = OpportunitySnapshotSchema(
        symbol="EURUSD",
        timeframe="M5",
        bias="BULLISH",
        structure="BULLISH|BOS=1|CHOCH=1|MSS=1",
        liquidity_target="BUY_SIDE_LIQUIDITY",
        stage=OpportunityStage.ENTRY_READY,
        institutional_score=80.0,
        execution_quality=75.0,
        last_update=datetime.now(timezone.utc),
        health="GREEN",
        decision_summary="Context BUY for EURUSD",
    )

    monkeypatch.setattr(scanner_router_module._service, "list_opportunities", lambda: [sample])

    client = TestClient(app)
    response = client.get("/api/v1/scanner/opportunities")

    assert response.status_code == 200
    payload = response.json()
    assert "opportunities" in payload
    assert len(payload["opportunities"]) == 1
    assert payload["opportunities"][0]["symbol"] == "EURUSD"
    assert payload["opportunities"][0]["stage"] == "ENTRY_READY"
