#!/bin/zsh
# Start both backend (FastAPI) and frontend (SvelteKit) for local development.
# Usage: ./start.sh

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$BACKEND/.venv"

# ── Kill any leftover processes on our ports ──────────────────────────────────
echo "Stopping any existing servers..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :5173 | xargs kill -9 2>/dev/null || true

# ── Recreate venv if broken ───────────────────────────────────────────────────
if ! "$VENV/bin/python" -c "import fastapi" 2>/dev/null; then
  echo "Setting up Python environment (first run or broken venv)..."
  cd "$BACKEND"
  rm -rf .venv
  python3 -m venv .venv
  "$VENV/bin/pip" install --upgrade pip -q
  "$VENV/bin/pip" install -r requirements.txt -q
  echo "✓ Python environment ready"
fi

# ── Start backend ─────────────────────────────────────────────────────────────
echo "Starting backend on http://localhost:8000 ..."
cd "$BACKEND"
"$VENV/bin/python" -m uvicorn app.main:app --port 8000 --reload > /tmp/salesdash-backend.log 2>&1 &
BACKEND_PID=$!

# Wait until the backend responds (max 15 s)
for i in $(seq 1 15); do
  if curl -s http://localhost:8000/api/health | grep -q "ok"; then
    echo "✓ Backend is up (PID $BACKEND_PID)"
    break
  fi
  sleep 1
done

# ── Start frontend ────────────────────────────────────────────────────────────
echo "Starting frontend on http://localhost:5173 ..."
cd "$FRONTEND"
npm run dev > /tmp/salesdash-frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait until Vite reports its URL (max 15 s)
for i in $(seq 1 15); do
  if grep -q "Local:" /tmp/salesdash-frontend.log 2>/dev/null; then
    FRONTEND_URL=$(grep "Local:" /tmp/salesdash-frontend.log | awk '{print $NF}')
    echo "✓ Frontend is up (PID $FRONTEND_PID)"
    break
  fi
  sleep 1
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
echo "  Dashboard:  ${FRONTEND_URL:-http://localhost:5173}"
echo "  API docs:   http://localhost:8000/docs"
echo "══════════════════════════════════════════"
echo "Logs: /tmp/salesdash-backend.log  /tmp/salesdash-frontend.log"
echo "Press Ctrl+C to stop both servers."
echo ""

# Keep script alive; Ctrl+C kills both children
trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
