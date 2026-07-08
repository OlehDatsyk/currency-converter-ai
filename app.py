"""
Currency Converter Web Application
------------------------------------
Main Flask application entry point.

This file wires together the web routes (pages the browser can visit)
and the API routes (JSON endpoints used by the JavaScript front-end via
the Fetch API / AJAX) with the business logic that lives in
`services/exchange_service.py`.

Run this file with:
    python app.py

See README.md for the full beginner-friendly setup guide.
"""

import os
import logging

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from services.exchange_service import (
    ExchangeRateError,
    convert_currency,
    get_supported_currencies,
)

# ---------------------------------------------------------------------------
# Load environment variables from a .env file (if present) BEFORE anything
# else needs them. See .env.example for the variables this project uses.
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Basic logging configuration. This prints helpful information to the VS
# Code terminal while the app is running, which makes debugging much easier
# for beginners.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("currency-converter")

# ---------------------------------------------------------------------------
# Flask application factory-style setup (kept simple/flat on purpose so it
# is easy to read for beginners, while still being production-friendly).
# ---------------------------------------------------------------------------
app = Flask(__name__)

# A secret key is required by Flask for things like flash messages/sessions.
# For local development a fallback value is fine; in production always set
# FLASK_SECRET_KEY via the .env file / real environment variables.
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-me")


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Render the single-page currency converter UI."""
    return render_template("index.html")


# ---------------------------------------------------------------------------
# API routes (consumed by static/js/script.js using fetch())
# ---------------------------------------------------------------------------
@app.route("/api/currencies", methods=["GET"])
def api_currencies():
    """
    Return the list of supported currencies as JSON.

    Response shape:
        {
            "success": true,
            "currencies": [
                {"code": "USD", "name": "United States Dollar"},
                {"code": "EUR", "name": "Euro"},
                ...
            ]
        }
    """
    try:
        currencies = get_supported_currencies()
        return jsonify({"success": True, "currencies": currencies})
    except Exception as exc:  # noqa: BLE001 - broad on purpose for a JSON API
        logger.exception("Failed to load currency list")
        return (
            jsonify({"success": False, "error": "Could not load currency list."}),
            500,
        )


@app.route("/api/convert", methods=["GET"])
def api_convert():
    """
    Convert an amount from one currency to another.

    Query parameters:
        from   - 3 letter currency code, e.g. USD
        to     - 3 letter currency code, e.g. EUR
        amount - positive number, e.g. 100

    Response shape (success):
        {
            "success": true,
            "from": "USD",
            "to": "EUR",
            "amount": 100.0,
            "rate": 0.92,
            "result": 92.0,
            "last_updated": "2026-07-08T12:00:00Z"
        }

    Response shape (error):
        {
            "success": false,
            "error": "Human readable message"
        }
    """
    from_currency = request.args.get("from", "").upper().strip()
    to_currency = request.args.get("to", "").upper().strip()
    amount_raw = request.args.get("amount", "").strip()

    # ---- Input validation -------------------------------------------------
    if not from_currency or not to_currency:
        return (
            jsonify({"success": False, "error": "Both 'from' and 'to' currencies are required."}),
            400,
        )

    if len(from_currency) != 3 or len(to_currency) != 3:
        return (
            jsonify({"success": False, "error": "Currency codes must be 3 letters, e.g. USD."}),
            400,
        )

    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        return (
            jsonify({"success": False, "error": "Amount must be a valid number."}),
            400,
        )

    if amount < 0:
        return (
            jsonify({"success": False, "error": "Amount cannot be negative."}),
            400,
        )

    # ---- Business logic -----------------------------------------------
    try:
        result = convert_currency(from_currency, to_currency, amount)
        return jsonify({"success": True, **result})
    except ExchangeRateError as exc:
        logger.warning("Conversion failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 502
    except Exception:  # noqa: BLE001
        logger.exception("Unexpected error during conversion")
        return (
            jsonify({"success": False, "error": "Something went wrong on the server."}),
            500,
        )


# ---------------------------------------------------------------------------
# Friendly JSON error handlers so the frontend always receives JSON, even
# for routes that don't exist or unexpected 500s.
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Endpoint not found."}), 404
    return render_template("index.html"), 200


@app.errorhandler(500)
def server_error(_error):
    return jsonify({"success": False, "error": "Internal server error."}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("1", "true", "yes")

    logger.info("Starting Currency Converter on http://127.0.0.1:%s", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
