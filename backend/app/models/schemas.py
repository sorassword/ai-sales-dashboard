"""
Pydantic schemas — the single source of truth for every shape the API returns.

These mirror the TypeScript types in `frontend/src/lib/types.ts`. When you change
something here, change it there too (or generate the TS types from the OpenAPI
schema later — see README "Typen synchron halten").
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel


# --------------------------------------------------------------------------- #
# Core entities
# --------------------------------------------------------------------------- #
class Store(BaseModel):
    id: str
    name: str          # e.g. "Modehaus Düsseldorf"
    city: str
    headcount: int


class Employee(BaseModel):
    id: str
    name: str
    initials: str
    store_id: str
    store_name: str
    role: Literal["Verkäufer", "Teamleitung", "Azubi"]
    avatar_hue: int    # 0-360, used to tint the avatar placeholder in the UI


# --------------------------------------------------------------------------- #
# Metrics — the heart of the dashboard
# --------------------------------------------------------------------------- #
Period = Literal["week", "month", "quarter"]


class TrendPoint(BaseModel):
    """A single point on a time series (one calendar day or month)."""
    month: str         # "2026-01" (monthly) or "2026-05-28" (daily)
    label: str         # "Jan" / "Mo"
    value: float
    period: Period = "month"


class KpiSummary(BaseModel):
    """Top-of-page headline numbers for the selected period."""
    period: Period = "month"
    total_revenue: float            # € net for the period
    revenue_delta_pct: float        # vs previous period
    bot_minutes: int                # total minutes employees spent in the bot
    bot_minutes_delta_pct: float
    avg_learning_score: float       # 0-100
    learning_score_delta_pct: float
    active_users: int               # employees who used the bot in the period
    active_users_delta_pct: float
    revenue_per_bot_hour: float     # € revenue / hour spent in bot — the ROI number
    # --- Bot-time benchmark (CHANGE 3) ------------------------------------- #
    bot_hours: float                # bot_minutes / 60
    bot_hours_target: float         # monthly target, scaled to the period
    bot_hours_pct_of_target: float  # (bot_hours / target) * 100
    bot_hours_per_employee: float   # bot_hours / active_users
    bot_hours_benchmark_label: Literal["Unter Ziel", "Auf Kurs", "Übertroffen"]


class EmployeeMetric(BaseModel):
    """Per-employee aggregate for the selected period."""
    period: Period = "month"
    employee: Employee
    revenue: float
    bot_minutes: int
    bot_interactions: int
    learning_score: float           # 0-100
    quiz_accuracy: float            # 0-100
    streak_days: int
    badges: int


class StoreMetric(BaseModel):
    period: Period = "month"
    store: Store
    revenue: float
    bot_minutes: int
    chat_share_pct: float           # share of the chain's total chat time
    revenue_share_pct: float        # share of the chain's total revenue
    readiness_score: float          # 0-100


class ScatterPoint(BaseModel):
    """One employee as a dot in the 'bot usage vs revenue' correlation chart."""
    employee_id: str
    name: str
    bot_minutes: int
    revenue: float
    learning_score: float


class CorrelationInsight(BaseModel):
    period: Period = "month"
    points: list[ScatterPoint]
    pearson_r: float                # correlation coefficient, for the headline
    headline: str                   # human-readable takeaway


# --------------------------------------------------------------------------- #
# Gamification
# --------------------------------------------------------------------------- #
class BadgeDef(BaseModel):
    id: str
    name: str
    description: str
    icon: str                       # lucide icon name used by the frontend
    tier: Literal["bronze", "silver", "gold"]
    rarity: Literal["common", "rare", "legendary"]   # CHANGE 4
    icon_key: Literal[
        "euro", "fire", "brain", "star",
        "lightning", "crown", "clock", "trophy",
    ]                                # frontend maps these to actual icons


class EarnedBadge(BaseModel):
    badge: BadgeDef
    employee_id: str
    employee_name: str
    earned_on: date


class PointsBreakdown(BaseModel):
    """Transparent breakdown of the points formula (CHANGE 1).

    Formula (see analytics.calculate_points):
        points = floor(revenue / 100)
               + bot_minutes * 2
               + floor(quiz_pct * 10)
               + streak_days * 5
    The four `from_*` parts always sum to `total` exactly.
    """
    from_revenue: int
    from_bot: int
    from_quiz: int
    from_streak: int
    total: int


class LeaderboardRow(BaseModel):
    period: Period = "month"
    rank: int
    employee: Employee
    points: int
    points_breakdown: PointsBreakdown   # CHANGE 1 — transparent scoring
    revenue: float
    bot_minutes: int
    streak_days: int
    badges: int
    movement: int                   # rank change vs last period (+up / -down)


class QuizResult(BaseModel):
    employee_id: str
    employee_name: str
    topic: str                      # e.g. "Boss FW26 Outerwear"
    accuracy: float                 # 0-100
    questions: int
    taken_on: date


# --------------------------------------------------------------------------- #
# Readiness & weekly digest (mirrors the "Seasonal Readiness Score")
# --------------------------------------------------------------------------- #
class ReadinessItem(BaseModel):
    collection: str                 # "Ralph Lauren Purple Label FW26"
    launch_date: date
    prepared_employees: int
    total_employees: int
    readiness_score: float          # 0-100
    status: Literal["on_track", "at_risk", "behind"]
    alert_level: Literal["critical", "warning", "ok"]   # CHANGE 2


class NextLaunch(BaseModel):
    name: str
    date: str                       # ISO date string
    days_until: int
    alert_level: Literal["critical", "warning", "ok"]


class ReadinessResponse(BaseModel):
    """Wraps the readiness list with a management-level alert summary."""
    items: list[ReadinessItem]
    critical_count: int
    warning_count: int
    next_launch: NextLaunch
    period: Period = "month"


class TopQuestion(BaseModel):
    topic: str
    count: int


class WeeklyDigest(BaseModel):
    period: Period = "month"
    week_label: str                 # "KW 22 · 2026"
    readiness_score: float          # 0-100
    top_questions: list[TopQuestion]
    new_badges: int
    most_active_employee: str


# --------------------------------------------------------------------------- #
# Store detail (CHANGE 2)
# --------------------------------------------------------------------------- #
class NextCollection(BaseModel):
    name: str
    launch_date: str                # ISO date string
    readiness_score: float
    alert_level: str                # "critical" | "warning" | "ok"


class StoreEmployeeRow(BaseModel):
    id: str                         # name slug, e.g. "jan-hoffmann"
    name: str
    role: str
    revenue: float
    bot_hours: float
    learn_score: float
    quiz_pct: float
    streak_days: int
    badge_count: int
    rank: int                       # overall leaderboard rank


class StoreDetail(BaseModel):
    store_id: str
    name: str
    city: str
    employee_count: int
    period: Period = "month"

    # Revenue
    revenue: float
    revenue_share_pct: float        # this store % of total chain revenue
    revenue_per_employee: float
    revenue_trend: float            # % change vs previous period

    # Bot usage
    bot_hours: float
    bot_hours_per_employee: float
    avg_learn_score: float

    # Readiness
    readiness_score: float          # avg readiness across collections
    next_collection: NextCollection

    employees: list[StoreEmployeeRow]
    insight: str


# --------------------------------------------------------------------------- #
# Employee detail (CHANGE 3)
# --------------------------------------------------------------------------- #
class EmployeeBadge(BaseModel):
    name: str
    rarity: Literal["common", "rare", "legendary"]
    icon_key: str
    earned_date: str                # ISO date string, deterministic


class EmployeeDetail(BaseModel):
    employee_id: str
    name: str
    initials: str
    role: str
    store_name: str
    period: Period = "month"

    # Core metrics
    revenue: float
    bot_hours: float
    learn_score: float
    quiz_pct: float
    streak_days: int
    rank: int
    points: int
    points_breakdown: PointsBreakdown   # CHANGE 1 — transparent scoring

    # vs store average (delta %, positive = above average)
    revenue_vs_store_avg: float
    bot_hours_vs_store_avg: float

    badges: list[EmployeeBadge]
    bot_trend: list[TrendPoint]
    revenue_trend: list[TrendPoint]
    insight: str


# --------------------------------------------------------------------------- #
# Chart drilldowns (CHANGE 4)
# --------------------------------------------------------------------------- #
class MonthlyInsight(BaseModel):
    label: str
    value: float
    comment: str


class RevenueTrendDetail(BaseModel):
    period: Period = "month"
    points: list[TrendPoint]
    extended_points: list[TrendPoint]   # always 24 monthly datapoints
    monthly_insights: list[MonthlyInsight]


class StoreBotBreakdown(BaseModel):
    store_name: str
    bot_hours: float
    pct_of_total: float
    color_key: str


class BotTrendDetail(BaseModel):
    period: Period = "month"
    points: list[TrendPoint]
    by_store: list[StoreBotBreakdown]


class CorrelationEmployee(BaseModel):
    name: str
    store: str
    bot_minutes: float
    revenue: float
    is_outlier: bool


class CorrelationDetail(BaseModel):
    period: Period = "month"
    correlation_r: float
    employees: list[CorrelationEmployee]
    insight: str


class DigestTopQuestion(BaseModel):
    topic: str
    count: int
    top_stores: list[str]
    example_query: str


class ReadinessSummary(BaseModel):
    avg_score: float
    critical_count: int
    collections_launching_soon: int


class DigestDetail(BaseModel):
    period: Period = "month"
    top_questions: list[DigestTopQuestion]
    readiness_summary: ReadinessSummary


# --------------------------------------------------------------------------- #
# Badge definitions (CHANGE 2) — GET /api/gamification/badge-definitions
# --------------------------------------------------------------------------- #
class BadgeDefinitionItem(BaseModel):
    name: str
    rarity: Literal["common", "rare", "legendary"]
    icon_key: str
    condition_text: str             # short, human-readable earn condition
    condition_detail: str           # longer explanation of how it's awarded
    earned_count: int               # how many employees currently hold it
    total_employees: int            # roster size (always 40 in the demo)
    earn_rate_pct: float            # earned_count / total_employees * 100
    last_earned_by: str             # name of the most recent earner
    last_earned_date: str           # ISO date string ("" if never earned)


class BadgeDefinitionsResponse(BaseModel):
    badges: list[BadgeDefinitionItem]


# --------------------------------------------------------------------------- #
# Arena (CHANGE 3) — GET /api/gamification/arena
# --------------------------------------------------------------------------- #
class ArenaPodiumEntry(BaseModel):
    rank: int                       # 1, 2, 3
    employee_id: str                # name slug, e.g. "jan-hoffmann"
    name: str
    initials: str
    store_name: str
    points: int
    points_breakdown: PointsBreakdown
    revenue: float
    streak_days: int
    badge_count: int
    avatar_color: str               # deterministic hex color per employee


class ArenaLeaderboardRow(BaseModel):
    rank: int
    rank_change: int                # vs previous period (positive = moved up)
    employee_id: str
    name: str
    initials: str
    store_name: str
    points: int
    points_breakdown: PointsBreakdown
    revenue: float
    bot_hours: float
    streak_days: int
    badge_count: int
    avatar_color: str


class ArenaWeeklyHighlight(BaseModel):
    employee_id: str
    name: str
    store_name: str
    highlight_reason: str           # e.g. "Höchster Umsatz diese Woche: 18.950 €"


class ArenaResponse(BaseModel):
    period: Period = "month"
    podium: list[ArenaPodiumEntry]          # always exactly top 3
    leaderboard: list[ArenaLeaderboardRow]  # all employees, rank 1-N
    weekly_highlight: ArenaWeeklyHighlight
