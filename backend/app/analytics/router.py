from fastapi import APIRouter
from fastapi import Depends

from app.analytics.models import AnalyticsSummary
from app.analytics.models import ConfluenceStats
from app.analytics.models import PlaybookStats
from app.analytics.models import RecommendationStats
from app.analytics.models import RiskStats
from app.analytics.models import SessionStats
from app.analytics.models import SymbolStats
from app.analytics.models import TimeframeStats
from app.analytics.service import AnalyticsService
from app.journal.router import get_journal_service
from app.journal.service import JournalService
from app.playbook.router import get_playbook_service
from app.playbook.service import PlaybookService

router = APIRouter(prefix="/analytics", tags=["Performance Analytics"])


def get_analytics_service(
    journal_service: JournalService = Depends(get_journal_service),
    playbook_service: PlaybookService = Depends(get_playbook_service),
) -> AnalyticsService:
    scoped_playbook_service = PlaybookService(repository=playbook_service._repository, journal_service=journal_service)
    return AnalyticsService(journal_service=journal_service, playbook_service=scoped_playbook_service)


@router.get("/summary", response_model=AnalyticsSummary)
async def summary(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getSummary()


@router.get("/sessions", response_model=list[SessionStats])
async def sessions(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getSessionStats()


@router.get("/timeframes", response_model=list[TimeframeStats])
async def timeframes(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getTimeframeStats()


@router.get("/symbols", response_model=list[SymbolStats])
async def symbols(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getSymbolStats()


@router.get("/playbook", response_model=list[PlaybookStats])
async def playbook(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getPlaybookStats()


@router.get("/recommendations", response_model=list[RecommendationStats])
async def recommendations(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getRecommendationStats()


@router.get("/confluences", response_model=ConfluenceStats)
async def confluences(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getConfluenceStats()


@router.get("/risk", response_model=RiskStats)
async def risk(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getRiskStats()


# Legacy aliases retained for backwards compatibility.
@router.get("/performance", response_model=AnalyticsSummary)
async def performance_legacy(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getSummary()


@router.get("/setups", response_model=list[PlaybookStats])
async def setups_legacy(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getPlaybookStats()


@router.get("/behaviour", response_model=list[RecommendationStats])
async def behaviour_legacy(service: AnalyticsService = Depends(get_analytics_service)):
    return service.getRecommendationStats()