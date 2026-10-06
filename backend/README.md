# Backend — Dashboard API (Mock)

FastAPI service that serves realistic **fake** data for the dashboard demo.
No database required: everything is generated deterministically in
`app/data/mock_generator.py`.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API base:  http://localhost:8000/api
- Live docs:  http://localhost:8000/docs

## Structure

| Path | Purpose |
|------|---------|
| `app/main.py` | App entrypoint, CORS, router mounting |
| `app/config.py` | Environment config |
| `app/models/schemas.py` | Pydantic schemas = the API contract |
| `app/data/mock_generator.py` | Deterministic fake-data factory |
| `app/services/analytics.py` | Aggregation + correlation logic |
| `app/api/routes_overview.py` | KPIs, trends, correlation, digest |
| `app/api/routes_data.py` | Employees, stores, gamification, readiness |

## Going from mock → real

Replace `mock_generator.py` with a loader (DB/CSV/API) that returns objects of
the same shape. Routes and frontend stay untouched. Later, add the chatbot as a
new router (`app/api/routes_chat.py`) and mount it in `main.py`.
