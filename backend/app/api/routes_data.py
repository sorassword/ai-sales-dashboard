"""Employees, stores, gamification and readiness endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.data.mock_generator import DATA
from app.models.schemas import (
    ArenaResponse,
    BadgeDefinitionsResponse,
    EarnedBadge,
    Employee,
    EmployeeDetail,
    EmployeeMetric,
    LeaderboardRow,
    Period,
    QuizResult,
    ReadinessResponse,
    Store,
    StoreDetail,
    StoreMetric,
)
from app.services import analytics

router = APIRouter(prefix="/api", tags=["data"])

# Shared query param: ?period=week|month|quarter (default month).
PeriodQuery = Query("month", description="Zeitraum: week | month | quarter")


# ----- Employees --------------------------------------------------------- #
@router.get("/employees", response_model=list[Employee])
def list_employees():
    return DATA.employees


@router.get("/employees/metrics", response_model=list[EmployeeMetric])
def employee_metrics(period: Period = PeriodQuery):
    return analytics.employee_metrics(period)


@router.get("/employees/{employee_id}", response_model=EmployeeDetail)
def employee_detail(employee_id: str, period: Period = PeriodQuery):
    detail = analytics.employee_detail(employee_id, period)
    if detail is None:
        raise HTTPException(status_code=404, detail="Not found")
    return detail


# ----- Stores ------------------------------------------------------------ #
@router.get("/stores", response_model=list[Store])
def list_stores():
    return DATA.stores


@router.get("/stores/metrics", response_model=list[StoreMetric])
def store_metrics(period: Period = PeriodQuery):
    return analytics.store_metrics(period)


@router.get("/stores/{store_id}", response_model=StoreDetail)
def store_detail(store_id: str, period: Period = PeriodQuery):
    detail = analytics.store_detail(store_id, period)
    if detail is None:
        raise HTTPException(status_code=404, detail="Not found")
    return detail


# ----- Gamification ------------------------------------------------------ #
@router.get("/gamification/leaderboard", response_model=list[LeaderboardRow])
def leaderboard(period: Period = PeriodQuery):
    return analytics.leaderboard(period)


@router.get("/gamification/badges", response_model=list[EarnedBadge])
def earned_badges(period: Period = PeriodQuery):
    return analytics.badges(period)


@router.get("/gamification/quizzes", response_model=list[QuizResult])
def quiz_results(period: Period = PeriodQuery):
    return analytics.quiz_results(period)


@router.get("/gamification/badge-definitions", response_model=BadgeDefinitionsResponse)
def badge_definitions():
    """All 8 badges with earn conditions, earn rate and most recent earner."""
    return analytics.badge_definitions()


@router.get("/gamification/arena", response_model=ArenaResponse)
def arena(period: Period = PeriodQuery):
    """Podium (top 3) + full leaderboard with points_breakdown + weekly highlight."""
    return analytics.arena(period)


# ----- Readiness --------------------------------------------------------- #
@router.get("/readiness", response_model=ReadinessResponse)
def readiness(period: Period = PeriodQuery):
    return analytics.readiness(period)
