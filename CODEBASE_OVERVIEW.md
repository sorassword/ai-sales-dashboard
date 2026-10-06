# Codebase Overview

Dieses Repo ist eine Demo fuer ein **AI Sales Assistant Dashboard**. Es besteht aus einem FastAPI-Backend und einem SvelteKit-Frontend. Das Backend liefert deterministische Mock-Daten als JSON-API. Das Frontend rendert daraus ein Management-/Mitarbeiter-Dashboard mit KPIs, Trends, Store-Auswertung, Gamification und Readiness.

Die zentrale Demo-Annahme ist: **Bot-Nutzung korreliert mit Umsatz**. Die Mock-Daten sind so generiert, dass dieser Zusammenhang sichtbar wird.

## Top-Level-Struktur

```text
ai-sales-dashboard/
├── README.md
├── CODEBASE_OVERVIEW.md
├── backend/
│   ├── README.md
│   ├── requirements.txt
│   └── app/
└── frontend/
    ├── package.json
    ├── package-lock.json
    ├── vite.config.ts
    ├── svelte.config.js
    ├── tsconfig.json
    └── src/
```

## Backend

Technologien:

- Python
- FastAPI
- Pydantic
- Uvicorn
- Keine Datenbank
- Deterministische Mock-Daten

### Wichtige Dateien

```text
backend/app/main.py
```

FastAPI-Entrypoint. Erstellt die App, setzt CORS, mountet Router und definiert Meta-Endpunkte.

Wichtige Routen:

```text
GET /                 API-Info
GET /api/health       Healthcheck
GET /docs             Swagger UI
```

```text
backend/app/config.py
```

Konfiguration, insbesondere CORS-Origins.

```text
backend/app/models/schemas.py
```

Pydantic-Schemas. Das ist der zentrale API-Vertrag. Wenn Backend-Felder geaendert werden, muss `frontend/src/lib/types.ts` synchron angepasst werden.

```text
backend/app/data/mock_generator.py
```

Erzeugt alle Fake-Daten deterministisch. Das ist die zentrale Stelle, wenn echte Daten spaeter angebunden werden sollen.

```text
backend/app/services/analytics.py
```

Berechnet Aggregationen, KPIs, Trends und Korrelationen aus den Mock-Daten.

```text
backend/app/api/routes_overview.py
```

Overview-Endpunkte, z. B. KPIs, Trends, Korrelation und Digest.

```text
backend/app/api/routes_data.py
```

Daten-Endpunkte fuer Employees, Stores, Gamification und Readiness.

### Typische Backend-Endpoints

```text
/api/overview/kpis
/api/overview/trends/revenue
/api/overview/trends/bot_minutes
/api/overview/correlation
/api/overview/digest
/api/employees
/api/employees/metrics
/api/stores
/api/stores/metrics
/api/gamification/leaderboard
/api/gamification/badges
/api/gamification/quizzes
/api/readiness
```

### Backend starten

```bash
cd backend
.venv/bin/uvicorn app.main:app --port 8000
```

In einer normalen lokalen Umgebung geht auch:

```bash
uvicorn app.main:app --reload --port 8000
```

## Frontend

Technologien:

- SvelteKit
- Svelte 5
- TypeScript
- Vite
- Tailwind CSS v4
- lucide-svelte fuer Icons
- Handgebaute SVG-Charts, keine Chart-Library

### Wichtige Dateien

```text
frontend/src/lib/api/client.ts
```

Typisierter API-Client. Nutzt:

```ts
PUBLIC_API_URL || 'http://localhost:8000'
```

Alle Frontend-Datenzugriffe laufen ueber dieses Objekt:

```ts
api.kpis()
api.trend()
api.correlation()
api.digest()
api.employees()
api.employeeMetrics()
api.stores()
api.storeMetrics()
api.leaderboard()
api.badges()
api.quizzes()
api.readiness()
```

```text
frontend/src/lib/types.ts
```

TypeScript-Spiegel der Backend-Pydantic-Schemas. Muss mit `backend/app/models/schemas.py` konsistent bleiben.

```text
frontend/src/routes/
```

SvelteKit-Routen. Jede Seite hat typischerweise:

```text
+page.ts       laedt Daten vom Backend
+page.svelte   rendert UI
```

Seiten:

```text
frontend/src/routes/+page.svelte
```

Overview/Dashboard-Hauptseite.

```text
frontend/src/routes/employees/+page.svelte
```

Mitarbeiter-Auswertung.

```text
frontend/src/routes/stores/+page.svelte
```

Filialvergleich.

```text
frontend/src/routes/gamification/+page.svelte
```

Leaderboard, Badges, Quiz-Ergebnisse.

```text
frontend/src/routes/readiness/+page.svelte
```

Seasonal Readiness.

```text
frontend/src/routes/+layout.svelte
```

Gemeinsames App-Layout.

```text
frontend/src/routes/+error.svelte
```

Fehlerseite. Sie unterscheidet zwischen API-Verbindungsfehlern und anderen App-Fehlern.

## Komponenten

```text
frontend/src/lib/components/Sidebar.svelte
frontend/src/lib/components/Topbar.svelte
```

Navigation/Layout.

```text
frontend/src/lib/components/Leaderboard.svelte
frontend/src/lib/components/BadgeWall.svelte
```

Gamification-Komponenten.

```text
frontend/src/lib/components/ui/
```

Kleinere UI-Bausteine:

```text
Avatar.svelte
Card.svelte
KpiCard.svelte
```

```text
frontend/src/lib/components/charts/
```

Handgebaute SVG-Charts:

```text
BarList.svelte
LineChart.svelte
ScatterChart.svelte
```

## Datenfluss

1. Backend erzeugt Mock-Daten in `mock_generator.py`.
2. `analytics.py` berechnet daraus KPIs, Trends, Korrelationen usw.
3. FastAPI-Router liefern JSON unter `/api/...`.
4. Frontend-`+page.ts` lädt Daten ueber `src/lib/api/client.ts`.
5. `+page.svelte` rendert die Daten mit Komponenten und Charts.

Beispiel Overview:

```text
frontend/src/routes/+page.ts
```

laedt parallel:

```ts
api.kpis(fetch)
api.trend('revenue', fetch)
api.trend('bot_minutes', fetch)
api.correlation(fetch)
api.digest(fetch)
api.leaderboard(fetch)
api.badges(fetch)
api.storeMetrics(fetch)
```

und gibt alles an:

```text
frontend/src/routes/+page.svelte
```

weiter.

## Styling

```text
frontend/src/app.css
```

Zentrale Styles und Design Tokens. Das Design ist editorial/retail-orientiert mit Papier-/Ink-/Akzentfarben. Tailwind v4 wird ueber Vite genutzt.

## Lokales Setup

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Aufrufen:

```text
http://localhost:5173
```

Backend erwartet unter:

```text
http://localhost:8000
```

## Hinweise fuer Aenderungen

- Neue Backend-Felder immer doppelt pflegen:
  - `backend/app/models/schemas.py`
  - `frontend/src/lib/types.ts`
- Neue API:
  1. Schema ergaenzen
  2. Mock-Daten oder Analytics ergaenzen
  3. Route in `backend/app/api/` ergaenzen
  4. Methode in `frontend/src/lib/api/client.ts` ergaenzen
  5. In passender `+page.ts` laden
  6. In `+page.svelte` rendern
- Echte Daten spaeter am besten einfuehren, indem `mock_generator.py` durch Loader fuer DB/CSV/API ersetzt wird, solange die Pydantic-Shapes gleich bleiben.
- Das Backend hat keine Dashboard-Seite. `http://localhost:8000/` ist nur API-Info. Das eigentliche UI laeuft auf `http://localhost:5173/`.

## Aktuelle Auffaelligkeiten

`svelte-check` findet keine Fehler, aber zwei Warnungen:

1. In `frontend/src/routes/+page.svelte` wird `data` initial destrukturiert; Svelte warnt, dass dadurch nur der Initialwert erfasst wird.
2. `tsconfig.json` referenziert Node-Typen, aber `@types/node` ist nicht installiert.

Beides blockiert den Run nicht.
