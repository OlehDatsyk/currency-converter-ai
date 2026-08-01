"""
config.py
---------
Centralised application configuration.

All secrets (API keys) are loaded from environment variables using
python-dotenv, so nothing sensitive is ever hard-coded in the source
code. See .env.example for the list of variables you need to set.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file (if present) into the environment.
# This MUST run before the Config class reads any os.environ values.
load_dotenv()


class Config:
    """Base configuration shared by the whole application."""

    # --- Flask ---------------------------------------------------------
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

    # --- AI Provider -----------------------------------------------------
    # "openai" or "claude" - lets you switch providers without touching code.
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "openai").lower()

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

    # --- Currency Exchange Rate API ------------------------------------
    # https://www.exchangerate-api.com/  (free tier available)
    EXCHANGE_RATE_API_KEY = os.environ.get("EXCHANGE_RATE_API_KEY", "")
    EXCHANGE_RATE_BASE_URL = "https://v6.exchangerate-api.com/v6"

    # Fallback, no-key-required historical/frankfurter API used for
    # trend + historical comparisons if you don't want to manage a
    # second key. See services/currency_service.py for details.
    FRANKFURTER_BASE_URL = "https://api.frankfurter.app"

    # --- Misc ------------------------------------------------------------
    REQUEST_TIMEOUT = 10  # seconds, for outgoing HTTP requests
