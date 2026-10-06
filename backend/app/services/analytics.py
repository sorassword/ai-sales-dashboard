"""
Aggregation logic. Routes stay thin; all the number-crunching lives here so it's
easy to unit-test and to swap for real queries later.

Everything is parameterised by `period` ∈ {week, month, quarter}. The base
dataset (`DATA`) represents a *month*; week / quarter values are derived from it
via deterministic, seed-jittered multipliers (see `mock_generator.period_factor`)
so the same period always yields the same numbers.
"""

from __future__ import annotations

import hashlib
import math
import random
from datetime import timedelta

from app.data.mock_generator import (
    DATA,
    QUESTION_DETAILS,
    TODAY,
    build_employee_insight,
    build_monthly_insights,
    build_store_insight,
    build_trends,
    monthly_series,
    period_config,
    period_factor,
    slugify,
)

# Monthly bot-time target for the demo (CHANGE 3). Scaled per period.
BOT_HOURS_TARGET_MONTH = 130.0

# How far back each period looks for time-stamped records (badges, quizzes).
PERIOD_WINDOW_DAYS = {"week": 7, "month": 30, "quarter": 90}

# Roster size — used for badge earn-rate. 4 stores × 10 tracked sellers = 40.
TOTAL_EMPLOYEES = len(DATA.employees)


# --------------------------------------------------------------------------- #
# Points formula (CHANGE 1) — single, transparent, deterministic source
# --------------------------------------------------------------------------- #
def _floor(x: float) -> int:
    """floor() with a tiny epsilon to absorb float artefacts (e.g. 78.4*10)."""
    return math.floor(x + 1e-9)


def calculate_points(
    revenue: float,
    bot_minutes: int,
    quiz_pct: float,
    streak_days: int,
) -> dict:
    """The one and only points formula. Returns a points_breakdown dict.

        points = floor(revenue / 100)
               + bot_minutes * 2
               + floor(quiz_pct * 10)
               + streak_days * 5

    The four `from_*` parts always sum to `total` exactly. Deterministic:
    same inputs always yield the same output.
    """
    from_revenue = _floor(revenue / 100)
    from_bot = int(bot_minutes) * 2
    from_quiz = _floor(quiz_pct * 10)
    from_streak = int(streak_days) * 5
    total = from_revenue + from_bot + from_quiz + from_streak
    return {
        "from_revenue": from_revenue,
        "from_bot": from_bot,
        "from_quiz": from_quiz,
        "from_streak": from_streak,
        "total": total,
    }


# Avatar palette (CHANGE 3) — 8 pleasant colors, deliberately no red/green so
# they never clash with the alert (critical/ok) colors elsewhere in the UI.
AVATAR_PALETTE = [
    "#6366F1", "#8B5CF6", "#EC4899", "#F59E0B",
    "#14B8A6", "#3B82F6", "#A78BFA", "#F97316",
]


def _avatar_color(name: str) -> str:
    """Deterministic hex color per employee name (stable across processes)."""
    h = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)
    return AVATAR_PALETTE[h % len(AVATAR_PALETTE)]


def _euro_de(value: float) -> str:
    """German thousands formatting: 18950 → '18.950'."""
    return f"{int(round(value)):,}".replace(",", ".")


def _window_start(period: str):
    """First day (inclusive) of the period window, anchored at the demo TODAY."""
    return TODAY - timedelta(days=PERIOD_WINDOW_DAYS.get(period, 30))


def get_period_multiplier(period: str) -> dict:
    """
    CHANGE 1 helper — return {multiplier, datapoints, label_type} for a period.
    Unknown periods fall back to "month".
    """
    return period_config(period)


def _pct_delta(value: float, ref: float) -> float:
    if not ref:
        return 0.0
    return round((value - ref) / ref * 100, 1)


def _benchmark_label(pct_of_target: float) -> str:
    if pct_of_target < 85:
        return "Unter Ziel"
    if pct_of_target <= 100:
        return "Auf Kurs"
    return "Übertroffen"


def kpi_summary(period: str = "month") -> dict:
    metrics = list(DATA.metrics.values())

    # Base (monthly) aggregates, then scaled to the requested period.
    base_revenue = sum(m["revenue"] for m in metrics)
    base_bot_minutes = sum(m["bot_minutes"] for m in metrics)
    avg_learning = sum(m["learning_score"] for m in metrics) / len(metrics)

    total_revenue = base_revenue * period_factor(period, "revenue")
    bot_minutes = int(base_bot_minutes * period_factor(period, "bot_minutes"))

    # Active users scale with engagement but never exceed the tracked roster.
    base_active = sum(1 for m in metrics if m["bot_minutes"] > 0)
    active_users = min(len(metrics), max(1, round(base_active * period_factor(period, "active_users"))))

    bot_hours = bot_minutes / 60 or 1

    # Previous-period reference comes from the period's own trend series.
    trends = build_trends(period)
    rev_series = trends["revenue"]
    bot_series = trends["bot_minutes"]
    learn_series = trends["learning_score"]

    # --- CHANGE 3: bot-time benchmark ------------------------------------- #
    bot_hours_target = round(BOT_HOURS_TARGET_MONTH * get_period_multiplier(period)["multiplier"], 1)
    bot_hours_pct = round(bot_hours / bot_hours_target * 100, 1) if bot_hours_target else 0.0

    return {
        "period": period,
        "total_revenue": round(total_revenue, -1),
        "revenue_delta_pct": _pct_delta(rev_series[-1]["value"], rev_series[-2]["value"]),
        "bot_minutes": bot_minutes,
        "bot_minutes_delta_pct": _pct_delta(bot_series[-1]["value"], bot_series[-2]["value"]),
        "avg_learning_score": round(avg_learning, 1),
        "learning_score_delta_pct": _pct_delta(learn_series[-1]["value"], learn_series[-2]["value"]),
        "active_users": active_users,
        "active_users_delta_pct": 8.4,
        "revenue_per_bot_hour": round(total_revenue / bot_hours, 2),
        "bot_hours": round(bot_hours, 1),
        "bot_hours_target": bot_hours_target,
        "bot_hours_pct_of_target": bot_hours_pct,
        "bot_hours_per_employee": round(bot_hours / active_users, 2),
        "bot_hours_benchmark_label": _benchmark_label(bot_hours_pct),
    }


def store_metrics(period: str = "month") -> list[dict]:
    rev_f = period_factor(period, "revenue")
    bot_f = period_factor(period, "bot_minutes")
    total_rev = sum(m["revenue"] for m in DATA.metrics.values()) * rev_f
    total_bot = sum(m["bot_minutes"] for m in DATA.metrics.values()) * bot_f

    rows = []
    for store in DATA.stores:
        members = [m for m in DATA.metrics.values() if m["employee"]["store_id"] == store["id"]]
        rev = sum(m["revenue"] for m in members) * rev_f
        bot = sum(m["bot_minutes"] for m in members) * bot_f
        avg_learning = sum(m["learning_score"] for m in members) / len(members)
        rows.append({
            "period": period,
            "store": store,
            "revenue": round(rev, -1),
            "bot_minutes": int(bot),
            "chat_share_pct": round(bot / total_bot * 100, 1) if total_bot else 0,
            "revenue_share_pct": round(rev / total_rev * 100, 1) if total_rev else 0,
            "readiness_score": round(min(99, avg_learning + 12), 1),
        })
    rows.sort(key=lambda r: r["revenue"], reverse=True)
    return rows


def correlation_insight(period: str = "month") -> dict:
    rev_f = period_factor(period, "revenue")
    bot_f = period_factor(period, "bot_minutes")
    points = []
    xs, ys = [], []
    for m in DATA.metrics.values():
        bot_minutes = int(m["bot_minutes"] * bot_f)
        revenue = round(m["revenue"] * rev_f, -1)
        points.append({
            "employee_id": m["employee"]["id"],
            "name": m["employee"]["name"],
            "bot_minutes": bot_minutes,
            "revenue": revenue,
            "learning_score": m["learning_score"],
        })
        xs.append(bot_minutes)
        ys.append(revenue)

    r = _pearson(xs, ys)
    if r >= 0.6:
        headline = f"Starke Korrelation (r = {r}): Mehr Bot-Nutzung geht klar mit höherem Umsatz einher."
    elif r >= 0.3:
        headline = f"Moderate Korrelation (r = {r}) zwischen Bot-Nutzung und Umsatz."
    else:
        headline = f"Schwache Korrelation (r = {r})."
    return {"period": period, "points": points, "pearson_r": r, "headline": headline}


def _pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return round(cov / (sx * sy), 2)


def employee_metrics(period: str = "month") -> list[dict]:
    rev_f = period_factor(period, "revenue")
    bot_f = period_factor(period, "bot_minutes")
    rows = []
    for m in DATA.metrics.values():
        rows.append({
            **m,
            "period": period,
            "revenue": round(m["revenue"] * rev_f, -1),
            "bot_minutes": int(m["bot_minutes"] * bot_f),
            "bot_interactions": int(m["bot_interactions"] * bot_f),
        })
    rows.sort(key=lambda m: m["revenue"], reverse=True)
    return rows


def leaderboard(period: str = "month") -> list[dict]:
    rev_f = period_factor(period, "revenue")
    bot_f = period_factor(period, "bot_minutes")

    rows = []
    for row in DATA.leaderboard:
        revenue = round(row["revenue"] * rev_f, -1)
        bot_minutes = int(row["bot_minutes"] * bot_f)
        quiz_pct = DATA.metrics[row["employee"]["id"]]["quiz_accuracy"]
        # CHANGE 1 — single transparent formula. Computed from the *scaled*
        # figures so points, revenue and bot-minutes stay internally consistent
        # within the period (for month, rev_f/bot_f are 1.0).
        breakdown = calculate_points(revenue, bot_minutes, quiz_pct, row["streak_days"])
        rows.append({
            **row,
            "period": period,
            "revenue": revenue,
            "bot_minutes": bot_minutes,
            "points": breakdown["total"],
            "points_breakdown": breakdown,
        })

    rows.sort(key=lambda r: r["points"], reverse=True)
    for rank, r in enumerate(rows, start=1):
        r["rank"] = rank
    return rows


def badges(period: str = "month") -> list[dict]:
    """Badges earned within the period window (CHANGE 1)."""
    start = _window_start(period)
    return [b for b in DATA.badges if b["earned_on"] >= start]


def quiz_results(period: str = "month") -> list[dict]:
    """Quiz results taken within the period window (CHANGE 1)."""
    start = _window_start(period)
    return [q for q in DATA.quiz_results if q["taken_on"] >= start]


def readiness(period: str = "month") -> dict:
    """
    CHANGE 2 — readiness list plus a management alert summary.

    Readiness scores are launch-preparation percentages, not volume metrics, so
    they don't scale with the period; only the response is wrapped/annotated.
    """
    items = [dict(r) for r in DATA.readiness]
    critical_count = sum(1 for i in items if i["alert_level"] == "critical")
    warning_count = sum(1 for i in items if i["alert_level"] == "warning")

    from app.data.mock_generator import TODAY

    nxt = min(items, key=lambda i: i["launch_date"])
    next_launch = {
        "name": nxt["collection"],
        "date": nxt["launch_date"].isoformat(),
        "days_until": (nxt["launch_date"] - TODAY).days,
        "alert_level": nxt["alert_level"],
    }

    return {
        "items": items,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "next_launch": next_launch,
        "period": period,
    }


def digest(period: str = "month") -> dict:
    return {**DATA.digest, "period": period}


def trends(metric: str, period: str = "month") -> list[dict]:
    return build_trends(period).get(metric, [])


# --------------------------------------------------------------------------- #
# Store detail (CHANGE 2)
# --------------------------------------------------------------------------- #
def _store_bot_hours(store_id: str, bot_f: float) -> float:
    members = [m for m in DATA.metrics.values() if m["employee"]["store_id"] == store_id]
    return sum(m["bot_minutes"] for m in members) * bot_f / 60


def store_detail(store_id: str, period: str = "month") -> dict | None:
    store = next((s for s in DATA.stores if s["id"] == store_id), None)
    if store is None:
        return None

    rev_f = period_factor(period, "revenue")
    bot_f = period_factor(period, "bot_minutes")

    members = [m for m in DATA.metrics.values() if m["employee"]["store_id"] == store_id]
    emp_count = len(members)

    total_rev = sum(m["revenue"] for m in DATA.metrics.values()) * rev_f
    store_rev = sum(m["revenue"] for m in members) * rev_f
    store_bot_hours = sum(m["bot_minutes"] for m in members) * bot_f / 60
    avg_learn = sum(m["learning_score"] for m in members) / emp_count

    # Revenue trend: chain delta + a deterministic per-store offset.
    rev_series = build_trends(period)["revenue"]
    base_delta = _pct_delta(rev_series[-1]["value"], rev_series[-2]["value"])
    offset = random.Random(f"storetrend:{store_id}:{period}").uniform(-2.5, 2.5)
    revenue_trend = round(base_delta + offset, 1)

    # Store bot usage vs the average store (period factor cancels out → stable).
    per_store_bot = [_store_bot_hours(s["id"], bot_f) for s in DATA.stores]
    avg_store_bot = sum(per_store_bot) / len(per_store_bot)
    bot_vs_avg_pct = (
        round((store_bot_hours - avg_store_bot) / avg_store_bot * 100, 1) if avg_store_bot else 0.0
    )
    streak_count = sum(1 for m in members if m["streak_days"] > 20)

    # Readiness (chain-wide; not store-scoped in the mock data).
    avg_readiness = round(sum(i["readiness_score"] for i in DATA.readiness) / len(DATA.readiness), 1)
    nxt = min(DATA.readiness, key=lambda i: i["launch_date"])
    next_collection = {
        "name": nxt["collection"],
        "launch_date": nxt["launch_date"].isoformat(),
        "readiness_score": nxt["readiness_score"],
        "alert_level": nxt["alert_level"],
    }

    rank_by_id = {r["employee"]["id"]: r["rank"] for r in leaderboard(period)}

    employees = []
    for m in members:
        emp = m["employee"]
        employees.append({
            "id": slugify(emp["name"]),
            "name": emp["name"],
            "role": emp["role"],
            "revenue": round(m["revenue"] * rev_f, -1),
            "bot_hours": round(m["bot_minutes"] * bot_f / 60, 2),
            "learn_score": m["learning_score"],
            "quiz_pct": m["quiz_accuracy"],
            "streak_days": m["streak_days"],
            "badge_count": m["badges"],
            "rank": rank_by_id[emp["id"]],
        })
    employees.sort(key=lambda e: e["revenue"], reverse=True)

    insight = build_store_insight(
        store["name"], bot_vs_avg_pct, streak_count, nxt["collection"], nxt["alert_level"]
    )

    return {
        "store_id": store["id"],
        "name": store["name"],
        "city": store["city"],
        "employee_count": emp_count,
        "period": period,
        "revenue": round(store_rev, -1),
        "revenue_share_pct": round(store_rev / total_rev * 100, 1) if total_rev else 0.0,
        "revenue_per_employee": round(store_rev / emp_count, 2),
        "revenue_trend": revenue_trend,
        "bot_hours": round(store_bot_hours, 1),
        "bot_hours_per_employee": round(store_bot_hours / emp_count, 2),
        "avg_learn_score": round(avg_learn, 1),
        "readiness_score": avg_readiness,
        "next_collection": next_collection,
        "employees": employees,
        "insight": insight,
    }


# --------------------------------------------------------------------------- #
# Employee detail (CHANGE 3)
# --------------------------------------------------------------------------- #
def employee_detail(employee_id: str, period: str = "month") -> dict | None:
    emp_id = DATA.employee_by_slug.get(employee_id)
    if emp_id is None:
        return None

    rev_f = period_factor(period, "revenue")
    bot_f = period_factor(period, "bot_minutes")

    m = DATA.metrics[emp_id]
    emp = m["employee"]

    revenue = round(m["revenue"] * rev_f, -1)
    bot_hours = round(m["bot_minutes"] * bot_f / 60, 2)

    row = next(r for r in leaderboard(period) if r["employee"]["id"] == emp_id)

    # Store averages (vs which we report the deltas).
    members = [mm for mm in DATA.metrics.values() if mm["employee"]["store_id"] == emp["store_id"]]
    store_avg_rev = sum(mm["revenue"] for mm in members) / len(members) * rev_f
    store_avg_bot_h = sum(mm["bot_minutes"] for mm in members) / len(members) * bot_f / 60
    revenue_vs_store_avg = round((revenue - store_avg_rev) / store_avg_rev * 100, 1) if store_avg_rev else 0.0
    bot_hours_vs_store_avg = round((bot_hours - store_avg_bot_h) / store_avg_bot_h * 100, 1) if store_avg_bot_h else 0.0

    # Badges, with a deterministic earned date spread across the last 90 days.
    emp_badges = []
    has_legendary = False
    legendary_name = None
    for b in DATA.badges:
        if b["employee_id"] != emp_id:
            continue
        bd = b["badge"]
        days_ago = random.Random(f"earned:{emp_id}:{bd['id']}").randint(0, 90)
        emp_badges.append({
            "name": bd["name"],
            "rarity": bd["rarity"],
            "icon_key": bd["icon_key"],
            "earned_date": (TODAY - timedelta(days=days_ago)).isoformat(),
        })
        if bd["rarity"] == "legendary":
            has_legendary = True
            legendary_name = bd["name"]
    emp_badges.sort(key=lambda x: x["earned_date"], reverse=True)

    # Per-employee trends: the chain series scaled by this employee's share.
    chain = build_trends(period)
    chain_total_rev = sum(mm["revenue"] for mm in DATA.metrics.values())
    chain_total_bot = sum(mm["bot_minutes"] for mm in DATA.metrics.values())
    rev_share = m["revenue"] / chain_total_rev if chain_total_rev else 0
    bot_share = m["bot_minutes"] / chain_total_bot if chain_total_bot else 0
    revenue_trend = [{**p, "value": round(p["value"] * rev_share, -1)} for p in chain["revenue"]]
    bot_trend = [{**p, "value": round(p["value"] * bot_share, 1)} for p in chain["bot_minutes"]]

    # Does this employee hold the longest streak in their store?
    max_store_streak = max(mm["streak_days"] for mm in members)
    longest_in_store = m["streak_days"] == max_store_streak and m["streak_days"] > 0

    insight = build_employee_insight(
        emp["name"],
        revenue_vs_store_avg,
        m["streak_days"],
        emp["store_name"].replace("Modehaus ", ""),
        longest_in_store,
        has_legendary,
        legendary_name,
    )

    return {
        "employee_id": employee_id,
        "name": emp["name"],
        "initials": emp["initials"],
        "role": emp["role"],
        "store_name": emp["store_name"],
        "period": period,
        "revenue": revenue,
        "bot_hours": bot_hours,
        "learn_score": m["learning_score"],
        "quiz_pct": m["quiz_accuracy"],
        "streak_days": m["streak_days"],
        "rank": row["rank"],
        "points": row["points"],
        "points_breakdown": row["points_breakdown"],   # CHANGE 1
        "revenue_vs_store_avg": revenue_vs_store_avg,
        "bot_hours_vs_store_avg": bot_hours_vs_store_avg,
        "badges": emp_badges,
        "bot_trend": bot_trend,
        "revenue_trend": revenue_trend,
        "insight": insight,
    }


# --------------------------------------------------------------------------- #
# Chart drilldowns (CHANGE 4)
# --------------------------------------------------------------------------- #
# Deterministic palette key per store (frontend maps these to chart colors).
STORE_COLOR_KEYS = {
    "duesseldorf": "brass",
    "koeln": "ink",
    "krefeld": "positive",
    "essen": "signal",
}


def revenue_trend_detail(period: str = "month") -> dict:
    return {
        "period": period,
        "points": trends("revenue", period),
        "extended_points": monthly_series("revenue", 24),
        "monthly_insights": build_monthly_insights(),
    }


def bot_trend_detail(period: str = "month") -> dict:
    bot_f = period_factor(period, "bot_minutes")
    total_bot_hours = sum(m["bot_minutes"] for m in DATA.metrics.values()) * bot_f / 60

    by_store = []
    for s in DATA.stores:
        bh = _store_bot_hours(s["id"], bot_f)
        by_store.append({
            "store_name": s["name"],
            "bot_hours": round(bh, 1),
            "pct_of_total": round(bh / total_bot_hours * 100, 1) if total_bot_hours else 0.0,
            "color_key": STORE_COLOR_KEYS.get(s["id"], "ink"),
        })
    by_store.sort(key=lambda x: x["bot_hours"], reverse=True)

    return {
        "period": period,
        "points": trends("bot_minutes", period),
        "by_store": by_store,
    }


def correlation_detail(period: str = "month") -> dict:
    rev_f = period_factor(period, "revenue")
    bot_f = period_factor(period, "bot_minutes")

    rows = []
    xs, ys = [], []
    for m in DATA.metrics.values():
        bot_minutes = round(m["bot_minutes"] * bot_f, 1)
        revenue = round(m["revenue"] * rev_f, -1)
        rows.append({
            "name": m["employee"]["name"],
            "store": m["employee"]["store_name"],
            "bot_minutes": bot_minutes,
            "revenue": revenue,
        })
        xs.append(bot_minutes)
        ys.append(revenue)

    r = _pearson(xs, ys)

    # Linear fit → flag residual outliers (>2σ from the regression line).
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    denom = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom if denom else 0
    intercept = my - slope * mx
    resid = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
    resid_std = math.sqrt(sum(e * e for e in resid) / n) if n else 0
    for row, e in zip(rows, resid):
        row["is_outlier"] = bool(resid_std and abs(e) > 2 * resid_std)

    # Note: "variance explained" is strictly r², but the demo spec pairs the
    # percentage with r directly (73 % ↔ r = 0.73), so we mirror that here.
    insight = (
        f"{round(r * 100)}% der Umsatzvarianz lässt sich mit der Bot-Nutzung "
        f"erklären (r = {r})."
    )
    return {"period": period, "correlation_r": r, "employees": rows, "insight": insight}


def digest_detail(period: str = "month") -> dict:
    top_questions = []
    for q in DATA.digest["top_questions"]:
        extra = QUESTION_DETAILS.get(q["topic"], {"top_stores": [], "example_query": ""})
        top_questions.append({
            "topic": q["topic"],
            "count": q["count"],
            "top_stores": extra["top_stores"],
            "example_query": extra["example_query"],
        })

    avg_score = round(sum(i["readiness_score"] for i in DATA.readiness) / len(DATA.readiness), 1)
    critical_count = sum(1 for i in DATA.readiness if i["alert_level"] == "critical")
    launching_soon = sum(1 for i in DATA.readiness if (i["launch_date"] - TODAY).days <= 30)

    return {
        "period": period,
        "top_questions": top_questions,
        "readiness_summary": {
            "avg_score": avg_score,
            "critical_count": critical_count,
            "collections_launching_soon": launching_soon,
        },
    }


# --------------------------------------------------------------------------- #
# Badge definitions (CHANGE 2)
# --------------------------------------------------------------------------- #
# Human-readable earn conditions, keyed by badge id. Texts are fixed copy.
BADGE_CONDITIONS: dict[str, dict[str, str]] = {
    "zehntausender": {
        "text": "Erziele in einem Monat mind. 10.000 € Umsatz",
        "detail": (
            "Wird automatisch vergeben, sobald ein Mitarbeiter in einem "
            "Kalendermonat die 10.000 €-Marke überschreitet. Basis: "
            "verifizierte Verkaufsdaten."
        ),
    },
    "umsatzmaschine": {
        "text": "Gehöre zum Top-10% der Filiale nach Umsatz",
        "detail": (
            "Wird am Monatsende vergeben an Mitarbeiter, die im oberen Dezil "
            "ihrer Filiale nach Nettoumsatz landen."
        ),
    },
    "unaufhaltsam": {
        "text": "Nutze den Assistenten 30 Tage in Folge",
        "detail": (
            "Ein Streak zählt, wenn der Bot an einem Tag mindestens einmal "
            "aktiv genutzt wurde. Der Streak bricht bei einem Tag Pause."
        ),
    },
    "kollektion_nerd": {
        "text": "Stelle 50 Kollektionsfragen an den Bot",
        "detail": (
            "Fragen zu Marken, Key Pieces, Trends oder Saisons zählen. "
            "Allgemeine Fragen oder Preisabfragen zählen nicht."
        ),
    },
    "cross_sell_koenig": {
        "text": "Empfehle 10 komplette Outfits erfolgreich",
        "detail": (
            "Zählt, wenn ein Verkauf mit mindestens 2 kombinierten Artikeln "
            "aus einer Bot-Empfehlung hervorgeht."
        ),
    },
    "outfit_architekt": {
        "text": "Verkaufe 10 komplette Looks in einem Monat",
        "detail": (
            "Ein kompletter Look besteht aus mindestens 3 Artikeln derselben "
            "Kollektion in einer Transaktion."
        ),
    },
    "erster_im_laden": {
        "text": "Nutze den Bot erstmals vor 8 Uhr morgens",
        "detail": (
            "Einmalig vergeben für die erste Bot-Nutzung eines Mitarbeiters "
            "vor 08:00 Uhr Lokalzeit."
        ),
    },
    "saisonprofi": {
        "text": "Erreiche einen Readiness-Score über 90 vor einem Kollektions-Launch",
        "detail": (
            "Gemessen 48 Stunden vor dem offiziellen Launch-Datum einer neuen "
            "Kollektion."
        ),
    },
}


def badge_definitions() -> dict:
    """All 8 badge definitions enriched with live earn statistics."""
    badges_out = []
    for bdef in DATA.badge_defs:
        earned = [b for b in DATA.badges if b["badge"]["id"] == bdef["id"]]
        earned_count = len(earned)

        if earned:
            last = max(earned, key=lambda b: b["earned_on"])
            last_by = last["employee_name"]
            last_date = last["earned_on"].isoformat()
        else:
            last_by = "—"
            last_date = ""

        cond = BADGE_CONDITIONS.get(bdef["id"], {"text": "", "detail": ""})
        badges_out.append({
            "name": bdef["name"],
            "rarity": bdef["rarity"],
            "icon_key": bdef["icon_key"],
            "condition_text": cond["text"],
            "condition_detail": cond["detail"],
            "earned_count": earned_count,
            "total_employees": TOTAL_EMPLOYEES,
            "earn_rate_pct": round(earned_count / TOTAL_EMPLOYEES * 100, 1) if TOTAL_EMPLOYEES else 0.0,
            "last_earned_by": last_by,
            "last_earned_date": last_date,
        })
    return {"badges": badges_out}


# --------------------------------------------------------------------------- #
# Arena (CHANGE 3) — podium + full leaderboard with breakdown
# --------------------------------------------------------------------------- #
def _previous_period_ranks(period: str) -> dict[str, int]:
    """Simulate the *previous* period's ranking for rank_change.

    Uses period_factor * 0.9 plus a different deterministic per-employee seed
    offset, so the ordering shifts slightly vs the current period but stays
    fully reproducible. Returns {employee_id: previous_rank}.
    """
    rev_f = period_factor(period, "revenue") * 0.9
    bot_f = period_factor(period, "bot_minutes") * 0.9

    scored = []
    for row in DATA.leaderboard:
        emp_id = row["employee"]["id"]
        m = DATA.metrics[emp_id]
        jitter = 1 + random.Random(f"prev:{period}:{emp_id}").uniform(-0.05, 0.05)
        revenue = round(row["revenue"] * rev_f * jitter, -1)
        bot_minutes = int(row["bot_minutes"] * bot_f * jitter)
        pts = calculate_points(revenue, bot_minutes, m["quiz_accuracy"], row["streak_days"])["total"]
        scored.append((emp_id, pts))

    scored.sort(key=lambda x: x[1], reverse=True)
    return {emp_id: rank for rank, (emp_id, _) in enumerate(scored, start=1)}


def arena(period: str = "month") -> dict:
    """Podium (top 3) + full leaderboard with points_breakdown + weekly highlight."""
    lb = leaderboard(period)                      # authoritative current ranking
    prev_ranks = _previous_period_ranks(period)

    leaderboard_rows = []
    for row in lb:
        emp = row["employee"]
        prev_rank = prev_ranks.get(emp["id"], row["rank"])
        leaderboard_rows.append({
            "rank": row["rank"],
            "rank_change": prev_rank - row["rank"],   # positive = moved up
            "employee_id": slugify(emp["name"]),
            "name": emp["name"],
            "initials": emp["initials"],
            "store_name": emp["store_name"],
            "points": row["points"],
            "points_breakdown": row["points_breakdown"],
            "revenue": row["revenue"],
            "bot_hours": round(row["bot_minutes"] / 60, 1),
            "streak_days": row["streak_days"],
            "badge_count": row["badges"],
            "avatar_color": _avatar_color(emp["name"]),
        })

    # Podium: first 3 entries, with the full breakdown (no rank_change/bot_hours).
    podium = [
        {
            "rank": r["rank"],
            "employee_id": r["employee_id"],
            "name": r["name"],
            "initials": r["initials"],
            "store_name": r["store_name"],
            "points": r["points"],
            "points_breakdown": r["points_breakdown"],
            "revenue": r["revenue"],
            "streak_days": r["streak_days"],
            "badge_count": r["badge_count"],
            "avatar_color": r["avatar_color"],
        }
        for r in leaderboard_rows[:3]
    ]

    # Weekly highlight: highest revenue in the *week* period, regardless of the
    # requested period filter. Revenue ordering is factor-independent, so the
    # top earner is stable; we scale only the displayed figure to week size.
    week_rev_f = period_factor("week", "revenue")
    best = max(DATA.metrics.values(), key=lambda m: m["revenue"])
    best_emp = best["employee"]
    week_revenue = round(best["revenue"] * week_rev_f, -1)
    weekly_highlight = {
        "employee_id": slugify(best_emp["name"]),
        "name": best_emp["name"],
        "store_name": best_emp["store_name"],
        "highlight_reason": f"Höchster Umsatz diese Woche: {_euro_de(week_revenue)} €",
    }

    return {
        "period": period,
        "podium": podium,
        "leaderboard": leaderboard_rows,
        "weekly_highlight": weekly_highlight,
    }
