"""Overview endpoints — feed the main dashboard page."""

from fastapi import APIRouter, Query

from app.models.schemas import (
    BotTrendDetail,
    CorrelationDetail,
    CorrelationInsight,
    DigestDetail,
    KpiSummary,
    Period,
    RevenueTrendDetail,
    TrendPoint,
    WeeklyDigest,
)
from app.services import analytics

router = APIRouter(prefix="/api/overview", tags=["overview"])

# Shared query param: ?period=week|month|quarter (default month).
PeriodQuery = Query("month", description="Zeitraum: week | month | quarter")


@router.get("/kpis", response_model=KpiSummary)
def get_kpis(period: Period = PeriodQuery):
    return analytics.kpi_summary(period)


@router.get("/trends/{metric}", response_model=list[TrendPoint])
def get_trend(metric: str, period: Period = PeriodQuery):
    """metric ∈ {revenue, bot_minutes, learning_score}."""
    return analytics.trends(metric, period)


@router.get("/correlation", response_model=CorrelationInsight)
def get_correlation(period: Period = PeriodQuery):
    return analytics.correlation_insight(period)


@router.get("/digest", response_model=WeeklyDigest)
def get_digest(period: Period = PeriodQuery):
    return analytics.digest(period)


# ----- Chart drilldowns (CHANGE 4) --------------------------------------- #
@router.get("/trends/revenue/detail", response_model=RevenueTrendDetail)
def get_revenue_trend_detail(period: Period = PeriodQuery):
    return analytics.revenue_trend_detail(period)


@router.get("/trends/bot/detail", response_model=BotTrendDetail)
def get_bot_trend_detail(period: Period = PeriodQuery):
    return analytics.bot_trend_detail(period)


@router.get("/correlation/detail", response_model=CorrelationDetail)
def get_correlation_detail(period: Period = PeriodQuery):
    return analytics.correlation_detail(period)


@router.get("/digest/detail", response_model=DigestDetail)
def get_digest_detail(period: Period = PeriodQuery):
    return analytics.digest_detail(period)
