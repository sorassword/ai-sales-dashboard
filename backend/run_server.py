#!/usr/bin/env python
"""Direct server runner with better error handling."""
import sys
import os

# Ensure proper path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60, flush=True)
print("Starting AI Sales Dashboard Backend", flush=True)
print("=" * 60, flush=True)

try:
    print("\n[1/3] Importing modules...", flush=True)
    import uvicorn
    from app.main import app
    print("[1/3] ✓ Modules imported successfully", flush=True)

    print("\n[2/3] Creating Uvicorn config...", flush=True)
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
    print("[2/3] ✓ Config created", flush=True)

    print("\n[3/3] Creating and running server...", flush=True)
    server = uvicorn.Server(config)
    print("[3/3] Starting server loop...", flush=True)

    import asyncio
    asyncio.run(server.serve())

except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
