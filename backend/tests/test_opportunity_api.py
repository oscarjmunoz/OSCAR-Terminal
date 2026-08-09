from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.opportunity.models import EstimatedEta
from app.opportunity.models import OpportunityPriority
from app.opportunity.models import OpportunityStage
from app.opportunity.models import RecommendedAction
from app.opportunity.schemas import MarketSummarySchema
from app.opportunity.schemas import OpportunityQueueResponse
from app.opportunity.schemas import OpportunityResultSchema
from app.opportunity import router as opportunity_router_module


client = TestClient(app)


def test_opportunity_queue_endpoint(monkeypatch):
    payload = OpportunityQueueResponse(
        market_summary=MarketSummarySchema(
            total_assets=4,
            ignored=1,
            watching=1,
            preparing=1,
            ready=1,
            active=0,
            last_scan=datetime.now(timezone.utc),
        ),
        opportunity_queue=[
            OpportunityResultSchema(
                symbol="EURUSD",
                timeframe="M5",
                bias="BULLISH",
                structure="BULLISH|BOS=1|CHOCH=1|MSS=1",
                liquidity_target="BUY_SIDE_LIQUIDITY",
                current_stage=OpportunityStage.EXECUTION_WINDOW,
                opportunity_score=81.0,
                institutional_score=78.0,
                execution_quality=76.0,
                priority=OpportunityPriority.HIGH,
                estimated_eta=EstimatedEta.NOW,
                decision_summary="Institutional snapshot",
                recommended_action=RecommendedAction.READY,
                last_update=datetime.now(timezone.utc),
            )
        ],
    )

    monkeypatch.setattr(opportunity_router_module._service, "get_queue", lambda: payload)

    response = client.get("/api/v1/opportunity/queue")

    assert response.status_code == 200
    body = response.json()
    assert body["market_summary"]["total_assets"] == 4
    assert len(body["opportunity_queue"]) == 1
    assert body["opportunity_queue"][0]["recommended_action"] == "READY"
