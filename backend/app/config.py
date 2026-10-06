"""Central config. Reads from environment with sensible local defaults."""

import os


class Settings:
    # Where the SvelteKit dev server runs — allowed to call this API.
    cors_origins: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:4173",
    ).split(",")


settings = Settings()
