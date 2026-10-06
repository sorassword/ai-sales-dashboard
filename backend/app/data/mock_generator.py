"""
Deterministic mock-data factory for the demo.

Everything is generated from a fixed seed so the dashboard looks identical on
every machine and on every reload — important for a sales demo. The numbers are
*internally consistent*: revenue is modelled as a function of bot usage and
learning score (+ noise), so the "bot usage drives revenue" story you tell on
stage actually shows up in the scatter plot and the ROI KPI.

When you later swap in real data, replace this module with a DB/CSV loader that
returns the same objects — nothing else in the app needs to change.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

# Fixed seed → reproducible demo. Change it to reshuffle the whole dataset.
RNG = random.Random(2026)

# "today" for the demo — keeps readiness alerts deterministic.
TODAY = date(2026, 6, 3)

# --------------------------------------------------------------------------- #
# Period handling (CHANGE 1)
# --------------------------------------------------------------------------- #
# week ≈ 25 % of a month, quarter ≈ 3× a month. Trend point counts differ too.
PERIOD_CONFIG: dict[str, dict] = {
    "week":    {"multiplier": 0.25, "datapoints": 7,  "label_type": "daily"},
    "month":   {"multiplier": 1.0,  "datapoints": 6,  "label_type": "monthly"},
    "quarter": {"multiplier": 3.0,  "datapoints": 12, "label_type": "monthly"},
}

MONTH_ABBR = {
    1: "Jan", 2: "Feb", 3: "Mär", 4: "Apr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dez",
}
DAY_LABELS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def period_config(period: str) -> dict:
    """Return the multiplier / datapoint config for a period (default: month)."""
    return PERIOD_CONFIG.get(period, PERIOD_CONFIG["month"])


def period_factor(period: str, key: str) -> float:
    """
    Deterministic scaling factor for a period and a named metric.

    Returns the base multiplier with a ±5 % seed-based jitter so scaled numbers
    don't look like exact multiples. `month` is left untouched (factor 1.0) so it
    reproduces the original "current behaviour". Same (period, key) → same factor.
    """
    cfg = period_config(period)
    base = cfg["multiplier"]
    if period == "month":
        return base
    rng = random.Random(f"{period}:{key}")
    return base * (1 + rng.uniform(-0.05, 0.05))

# --------------------------------------------------------------------------- #
# Static reference data
# --------------------------------------------------------------------------- #
STORES = [
    {"id": "krefeld", "name": "Modehaus Krefeld", "city": "Krefeld", "headcount": 22},
    {"id": "duesseldorf", "name": "Modehaus Düsseldorf", "city": "Düsseldorf", "headcount": 28},
    {"id": "koeln", "name": "Modehaus Köln", "city": "Köln", "headcount": 24},
    {"id": "essen", "name": "Modehaus Essen", "city": "Essen", "headcount": 18},
]

_FIRST_NAMES = [
    "Lukas", "Mara", "Jonas", "Sophie", "Elias", "Lena", "Finn", "Hannah",
    "Noah", "Emma", "Ben", "Mia", "Paul", "Lea", "Leon", "Anna", "Tom",
    "Clara", "Max", "Nele", "David", "Marie", "Tim", "Julia", "Yusuf",
    "Aylin", "Marco", "Pia", "Jan", "Frieda",
]
_LAST_NAMES = [
    "Becker", "Schmitz", "Wagner", "Hoffmann", "Schäfer", "Koch", "Bauer",
    "Richter", "Klein", "Wolf", "Neumann", "Schwarz", "Krüger", "Hofmann",
    "Lange", "Werner", "Krause", "Lehmann", "Köhler", "Maier",
]

# CHANGE 4 — new naming system, with rarity + icon_key for the frontend.
# `tier` is kept (legacy field) and mapped from rarity for backward compat.
BADGE_DEFS = [
    {"id": "zehntausender", "name": "Zehntausender", "description": "Erste 10.000 € in einem Monat", "icon": "Euro", "tier": "bronze", "rarity": "common", "icon_key": "euro"},
    {"id": "umsatzmaschine", "name": "Umsatzmaschine", "description": "Top 10 % Umsatz im Laden", "icon": "Trophy", "tier": "silver", "rarity": "rare", "icon_key": "trophy"},
    {"id": "unaufhaltsam", "name": "Unaufhaltsam", "description": "30-Tage-Streak", "icon": "Flame", "tier": "gold", "rarity": "legendary", "icon_key": "fire"},
    {"id": "kollektion_nerd", "name": "Kollektion-Nerd", "description": "50 Kollektions-Anfragen an den Bot", "icon": "Brain", "tier": "bronze", "rarity": "common", "icon_key": "brain"},
    {"id": "cross_sell_koenig", "name": "Cross-Sell-König", "description": "10 vollständige Outfit-Empfehlungen", "icon": "Crown", "tier": "silver", "rarity": "rare", "icon_key": "crown"},
    {"id": "outfit_architekt", "name": "Outfit-Architekt", "description": "10 komplette Looks verkauft", "icon": "Star", "tier": "silver", "rarity": "rare", "icon_key": "star"},
    {"id": "erster_im_laden", "name": "Erster im Laden", "description": "Bot-Nutzung vor 8 Uhr", "icon": "Clock", "tier": "bronze", "rarity": "common", "icon_key": "clock"},
    {"id": "saisonprofi", "name": "Saisonprofi", "description": "Readiness-Score > 90 vor Launch", "icon": "Zap", "tier": "gold", "rarity": "legendary", "icon_key": "lightning"},
]

QUIZ_TOPICS = [
    "Boss FW26 Outerwear", "Gant SS26 Coastal Heritage", "Ralph Lauren Purple Label",
    "Tommy Hilfiger Aktion", "Cross-Selling Komplett-Looks", "Margen & UVPs",
    "Modern Tailoring", "Kaschmir-Pflege",
]

COLLECTIONS = [
    {"collection": "Ralph Lauren Purple Label FW26", "offset": 12},
    {"collection": "Boss Herbst/Winter — Modern Tailoring", "offset": 26},
    {"collection": "Gant SS26 — Coastal Heritage", "offset": 40},
    {"collection": "Tommy Hilfiger Frühjahrs-Aktion", "offset": 6},
]


def _initials(name: str) -> str:
    parts = name.split()
    return (parts[0][0] + parts[-1][0]).upper()


# --------------------------------------------------------------------------- #
# Slugs & deterministic insight/detail helpers (CHANGE 2 / 3 / 4)
# --------------------------------------------------------------------------- #
_UMLAUTS = str.maketrans(
    {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"}
)


def slugify(name: str) -> str:
    """'Jan Hoffmann' → 'jan-hoffmann', 'Modehaus Düsseldorf' → 'modehaus-duesseldorf'."""
    s = name.translate(_UMLAUTS).lower()
    out = [ch if ch.isalnum() else "-" for ch in s]
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def _de(value: float, decimals: int = 1) -> str:
    """German decimal formatting: 2.1 → '2,1'."""
    return f"{value:.{decimals}f}".replace(".", ",")


def build_store_insight(
    store_name: str,
    bot_vs_avg_pct: float,
    streak_count: int,
    next_name: str,
    next_alert: str,
) -> str:
    """Deterministic store insight string from already-computed values."""
    direction = "über" if bot_vs_avg_pct >= 0 else "unter"
    s1 = (
        f"{store_name} liegt {_de(abs(bot_vs_avg_pct))}% {direction} dem "
        f"Filialdurchschnitt bei der Bot-Nutzung."
    )
    if streak_count == 0:
        s2 = "Aktuell hält niemand einen Streak von über 20 Tagen."
    elif streak_count == 1:
        s2 = "1 Mitarbeiter:in hat einen Streak von über 20 Tagen."
    else:
        s2 = f"{streak_count} Mitarbeiter:innen haben einen Streak von über 20 Tagen."
    alert_word = {
        "critical": "kritisch im Rückstand",
        "warning": "in Verzug",
        "ok": "im Plan",
    }.get(next_alert, "im Plan")
    s3 = f"Nächster Launch „{next_name}“ ist {alert_word}."
    return f"{s1} {s2} {s3}"


def build_employee_insight(
    name: str,
    revenue_vs_store_avg: float,
    streak_days: int,
    store_city: str,
    longest_in_store: bool,
    has_legendary: bool,
    legendary_name: str | None,
) -> str:
    """Deterministic employee insight string from already-computed values."""
    first = name.split()[0]
    direction = "über" if revenue_vs_store_avg >= 0 else "unter"
    parts = [
        f"{name} liegt {_de(abs(revenue_vs_store_avg))}% {direction} dem "
        f"Filial-Durchschnitt beim Umsatz."
    ]
    if streak_days > 14:
        if longest_in_store:
            parts.append(
                f"Mit {streak_days} Tagen hält {first} den längsten aktiven Streak in {store_city}."
            )
        else:
            parts.append(f"{first} ist mit einem {streak_days}-Tage-Streak sehr konstant.")
    if has_legendary and legendary_name:
        parts.append(f"Highlight: das legendäre Badge „{legendary_name}“.")
    return " ".join(parts)


def monthly_series(metric: str, n: int) -> list[dict]:
    """
    n monthly TrendPoints for `metric`, ending at the demo's latest month.
    Used for the 24-month "extended" revenue view and the 6-month insights.
    Deterministic via a per-(metric, n) seed.
    """
    rng = random.Random(f"extended:{metric}:{n}")
    out: list[dict] = []
    for i, (m, label) in enumerate(_month_seq(n)):
        if metric == "bot_minutes":
            val: float = int(4_200 * (1 + i * 0.11) + rng.gauss(0, 120))
        elif metric == "learning_score":
            val = round(min(95, 68 + i * 3.2 + rng.gauss(0, 1.5)), 1)
        else:  # revenue
            val = round(920_000 * (1 + i * 0.045) + rng.gauss(0, 18_000), -2)
        out.append({"month": m, "label": label, "period": "month", "value": val})
    return out


# Deterministic per-month commentary for the revenue drilldown.
MONTHLY_COMMENTS = {
    "Dez": "Weihnachtsgeschäft trägt den Umsatz.",
    "Jan": "Ruhiger Jahresstart, Fokus auf Schulungen.",
    "Feb": "Boss-Kollektion-Launch beflügelt den Verkauf.",
    "Mär": "Frühjahrsware kommt an, Bot-Nutzung steigt.",
    "Apr": "Stabiler Monat mit starker Beratungsquote.",
    "Mai": "Gant SS26 sorgt für Aufschwung.",
}


def build_monthly_insights() -> list[dict]:
    """Always 6 entries for the last 6 months (revenue + a comment)."""
    out = []
    for p in monthly_series("revenue", 6):
        out.append(
            {
                "label": p["label"],
                "value": p["value"],
                "comment": MONTHLY_COMMENTS.get(p["label"], "Solider Monat im Plan."),
            }
        )
    return out


# Deterministic enrichment for digest top-questions (which stores, sample query).
QUESTION_DETAILS = {
    "Boss FW26 Outerwear": {
        "top_stores": ["Modehaus Düsseldorf", "Modehaus Köln"],
        "example_query": "Welches Innenfutter hat der Boss-Wollmantel FW26?",
    },
    "Cross-Selling Komplett-Looks": {
        "top_stores": ["Modehaus Köln", "Modehaus Essen"],
        "example_query": "Welche Schuhe passen zum grauen Modern-Fit-Anzug?",
    },
    "Gant SS26 UVPs": {
        "top_stores": ["Modehaus Krefeld", "Modehaus Düsseldorf"],
        "example_query": "Was ist die UVP der Gant SS26 Leinenhemden?",
    },
    "Ralph Lauren Purple Label": {
        "top_stores": ["Modehaus Düsseldorf", "Modehaus Köln"],
        "example_query": "Worin unterscheidet sich Purple Label von der Polo-Linie?",
    },
    "Margen-starke Teile": {
        "top_stores": ["Modehaus Essen", "Modehaus Krefeld"],
        "example_query": "Welche Strickwaren haben aktuell die beste Marge?",
    },
}


# --------------------------------------------------------------------------- #
# Generated dataset (built once at import)
# --------------------------------------------------------------------------- #
def _build_employees() -> list[dict]:
    employees: list[dict] = []
    used: set[str] = set()
    eid = 0
    for store in STORES:
        # ~10 tracked sellers per store for the demo (not the full headcount)
        for _ in range(10):
            while True:
                name = f"{RNG.choice(_FIRST_NAMES)} {RNG.choice(_LAST_NAMES)}"
                if name not in used:
                    used.add(name)
                    break
            eid += 1
            role = RNG.choices(
                ["Verkäufer", "Teamleitung", "Azubi"], weights=[8, 1, 2]
            )[0]
            employees.append({
                "id": f"emp-{eid:03d}",
                "name": name,
                "initials": _initials(name),
                "store_id": store["id"],
                "store_name": store["name"],
                "role": role,
                "avatar_hue": RNG.randint(0, 359),
            })
    return employees


def _build_employee_metrics(employees: list[dict]) -> dict[str, dict]:
    """Per-employee aggregates with revenue modelled from bot usage + learning."""
    metrics: dict[str, dict] = {}
    for emp in employees:
        bot_minutes = max(15, int(RNG.gauss(190, 80)))          # ~3 h/month avg
        learning_score = min(100, max(40, RNG.gauss(74, 14)))
        interactions = int(bot_minutes * RNG.uniform(0.7, 1.3))

        # Core model: revenue correlates with engagement (this is the demo thesis)
        base = 22_000
        revenue = (
            base
            + bot_minutes * 75                 # each bot minute ~ €75 lift
            + learning_score * 220             # knowledge lift
            + RNG.gauss(0, 6_000)              # honest noise
        )
        revenue = max(8_000, revenue)

        metrics[emp["id"]] = {
            "employee": emp,
            "revenue": round(revenue, -1),
            "bot_minutes": bot_minutes,
            "bot_interactions": interactions,
            "learning_score": round(learning_score, 1),
            "quiz_accuracy": round(min(100, learning_score + RNG.gauss(4, 8)), 1),
            "streak_days": RNG.choices([0, 3, 7, 12, 21, 30, 45], weights=[2, 3, 4, 3, 2, 2, 1])[0],
            "badges": 0,  # filled in after badge generation
        }
    return metrics


def _month_seq(n: int, end: date = date(2026, 5, 1)) -> list[tuple[str, str]]:
    """Return n (`YYYY-MM`, `Abk`) tuples ending at `end`, oldest first."""
    out: list[tuple[str, str]] = []
    for i in range(n - 1, -1, -1):
        year, month = end.year, end.month - i
        while month <= 0:
            month += 12
            year -= 1
        out.append((f"{year}-{month:02d}", MONTH_ABBR[month]))
    return out


def build_trends(period: str = "month") -> dict[str, list[dict]]:
    """
    Chain-wide time series for the headline charts, shaped by `period`:
      - week    → 7 daily points
      - month   → 6 monthly points (the original behaviour)
      - quarter → 12 monthly points
    Deterministic: a per-period RNG seed means same period → same series.
    """
    cfg = period_config(period)
    n = cfg["datapoints"]
    rng = random.Random(f"trends:{period}")
    revenue, bot, learning = [], [], []

    if cfg["label_type"] == "daily":
        # Daily scale ≈ a month divided over ~30 days.
        rev_base, bot_base, learn_base = 31_000, 150, 80
        for i in range(n):
            d = TODAY - timedelta(days=(n - 1 - i))
            m, label = d.isoformat(), DAY_LABELS[d.weekday()]
            growth = 1 + i * 0.02
            revenue.append({"month": m, "label": label, "period": period,
                            "value": round(rev_base * growth + rng.gauss(0, 1_500), -2)})
            bot.append({"month": m, "label": label, "period": period,
                        "value": int(bot_base * (1 + i * 0.03) + rng.gauss(0, 8))})
            learning.append({"month": m, "label": label, "period": period,
                             "value": round(min(95, learn_base + i * 0.4 + rng.gauss(0, 1)), 1)})
    else:
        rev_base, bot_base, learn_base = 920_000, 4_200, 68
        for i, (m, label) in enumerate(_month_seq(n)):
            growth = 1 + i * 0.045
            revenue.append({"month": m, "label": label, "period": period,
                            "value": round(rev_base * growth + rng.gauss(0, 18_000), -2)})
            bot.append({"month": m, "label": label, "period": period,
                        "value": int(bot_base * (1 + i * 0.11) + rng.gauss(0, 120))})
            learning.append({"month": m, "label": label, "period": period,
                             "value": round(min(95, learn_base + i * 3.2 + rng.gauss(0, 1.5)), 1)})

    return {"revenue": revenue, "bot_minutes": bot, "learning_score": learning}


def _build_badges(metrics: dict[str, dict]) -> list[dict]:
    earned: list[dict] = []
    by_def = {b["id"]: b for b in BADGE_DEFS}
    ranked = sorted(metrics.values(), key=lambda m: m["revenue"], reverse=True)

    def add(badge_id: str, emp: dict, days_ago: int) -> None:
        earned.append({
            "badge": by_def[badge_id],
            "employee_id": emp["employee"]["id"],
            "employee_name": emp["employee"]["name"],
            "earned_on": date(2026, 5, 31) - timedelta(days=days_ago),
        })

    def grant(badge_id: str, emp: dict, prob: float) -> None:
        """
        Award a badge with an independent, per-(badge, employee) deterministic
        draw. Decoupling each decision from the shared RNG stream keeps the
        rarity distribution stable when thresholds are tuned (same seed → same
        output regardless of evaluation order).
        """
        rng = random.Random(f"badge:{badge_id}:{emp['employee']['id']}")
        if rng.random() < prob:
            add(badge_id, emp, rng.randint(1, 28))

    # Tuned so earned badges land near the target mix: ~60 % common, 30 % rare,
    # 10 % legendary (see assertion in the module self-check).
    top_cut = max(1, len(ranked) // 10)
    for m in ranked[:top_cut]:                       # rare: top 10 % revenue
        grant("umsatzmaschine", m, 1.0)

    for m in metrics.values():
        # --- common badges (~60 %) --------------------------------------- #
        if m["revenue"] >= 10_000:
            grant("zehntausender", m, 0.55)
        grant("kollektion_nerd", m, 0.40)
        grant("erster_im_laden", m, 0.25)
        # --- rare badges (~30 %) ----------------------------------------- #
        grant("cross_sell_koenig", m, 0.20)
        grant("outfit_architekt", m, 0.12)
        # --- legendary badges (~10 %) ------------------------------------ #
        if m["streak_days"] >= 30:
            grant("unaufhaltsam", m, 0.60)
        grant("saisonprofi", m, 0.06)

    # tally badge counts back onto employee metrics
    for e in earned:
        metrics[e["employee_id"]]["badges"] += 1
    return earned


def _build_leaderboard(metrics: dict[str, dict]) -> list[dict]:
    scored = []
    for m in metrics.values():
        points = int(
            m["revenue"] / 100
            + m["bot_minutes"] * 2
            + m["learning_score"] * 5
            + m["streak_days"] * 10
            + m["badges"] * 50
        )
        scored.append({**m, "points": points})
    scored.sort(key=lambda x: x["points"], reverse=True)

    rows = []
    for i, m in enumerate(scored, start=1):
        rows.append({
            "rank": i,
            "employee": m["employee"],
            "points": m["points"],
            "revenue": m["revenue"],
            "bot_minutes": m["bot_minutes"],
            "streak_days": m["streak_days"],
            "badges": m["badges"],
            "movement": RNG.choices([2, 1, 0, -1, -2], weights=[2, 3, 4, 3, 2])[0],
        })
    return rows


def _build_quiz_results(metrics: dict[str, dict]) -> list[dict]:
    results = []
    emp_list = list(metrics.values())
    for _ in range(40):
        m = RNG.choice(emp_list)
        results.append({
            "employee_id": m["employee"]["id"],
            "employee_name": m["employee"]["name"],
            "topic": RNG.choice(QUIZ_TOPICS),
            "accuracy": round(min(100, max(45, m["learning_score"] + RNG.gauss(0, 12))), 1),
            "questions": RNG.choice([5, 8, 10]),
            "taken_on": date(2026, 5, 31) - timedelta(days=RNG.randint(0, 27)),
        })
    results.sort(key=lambda r: r["taken_on"], reverse=True)
    return results


def classify_alert(score: float, days_until: int) -> str:
    """CHANGE 2 — management alert level for a readiness item."""
    if score < 65 and days_until <= 7:
        return "critical"
    if score < 75 or (days_until <= 14 and score < 80):
        return "warning"
    return "ok"


def _build_readiness() -> list[dict]:
    items = []
    for c in COLLECTIONS:
        total = 92  # tracked employees across the chain
        prepared = int(total * RNG.uniform(0.55, 0.97))
        score = round(prepared / total * 100, 1)
        status = "on_track" if score >= 85 else "at_risk" if score >= 65 else "behind"
        launch_date = date(2026, 5, 31) + timedelta(days=c["offset"])
        days_until = (launch_date - TODAY).days
        items.append({
            "collection": c["collection"],
            "launch_date": launch_date,
            "prepared_employees": prepared,
            "total_employees": total,
            "readiness_score": score,
            "status": status,
            "alert_level": classify_alert(score, days_until),
        })
    items.sort(key=lambda x: x["launch_date"])
    return items


def _build_digest(metrics: dict[str, dict]) -> dict:
    top_emp = max(metrics.values(), key=lambda m: m["bot_minutes"])
    return {
        "week_label": "KW 22 · 2026",
        "readiness_score": 94.0,
        "top_questions": [
            {"topic": "Boss FW26 Outerwear", "count": 142},
            {"topic": "Cross-Selling Komplett-Looks", "count": 118},
            {"topic": "Gant SS26 UVPs", "count": 97},
            {"topic": "Ralph Lauren Purple Label", "count": 73},
            {"topic": "Margen-starke Teile", "count": 61},
        ],
        "new_badges": 11,
        "most_active_employee": top_emp["employee"]["name"],
    }


# --------------------------------------------------------------------------- #
# Public dataset object — import this everywhere
# --------------------------------------------------------------------------- #
class Dataset:
    def __init__(self) -> None:
        self.stores = STORES
        self.badge_defs = BADGE_DEFS
        self.employees = _build_employees()
        # name-slug → employee id, for the /employees/{slug} detail endpoint
        self.employee_by_slug = {slugify(e["name"]): e["id"] for e in self.employees}
        self.metrics = _build_employee_metrics(self.employees)
        self.trends = build_trends("month")
        self.badges = _build_badges(self.metrics)          # mutates metrics' badge counts
        self.leaderboard = _build_leaderboard(self.metrics)
        self.quiz_results = _build_quiz_results(self.metrics)
        self.readiness = _build_readiness()
        self.digest = _build_digest(self.metrics)


DATA = Dataset()
