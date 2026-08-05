from app.analytics.models import AnalyticsSummary
from app.analytics.models import ConfluenceStats
from app.analytics.models import ConfluenceFrequency
from app.analytics.models import PlaybookStats
from app.analytics.models import RecommendationStats
from app.analytics.models import RiskStats
from app.analytics.models import SessionStats
from app.analytics.models import SymbolStats
from app.analytics.models import TimeframeStats
from app.analytics.router import get_analytics_service
from app.analytics.service import AnalyticsService

# Legacy aliases retained for compatibility with older imports.
PerformanceReport = AnalyticsSummary
SessionAnalytics = SessionStats
TimeframeAnalytics = TimeframeStats
SetupAnalytics = PlaybookStats
RecommendationAnalytics = RecommendationStats
BehaviourAnalytics = RecommendationStats
ConfluenceAnalytics = ConfluenceStats