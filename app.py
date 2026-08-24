"""
app.py
-------
Entry point for the AI Currency Assistant Flask application.

Run with:
    python app.py

The app exposes:
- GET  /                       -> renders the single-page frontend
- GET  /api/currencies         -> list of supported currency codes/names
- POST /api/convert            -> convert amount + AI explanation
- POST /api/historical         -> historical rate series
- POST /api/trend              -> AI-generated trend summary
- POST /api/travel-tips        -> AI travel money recommendations
- POST /api/investment-tips    -> AI investment-education suggestions
- POST /api/compare            -> compare multiple currencies vs USD
- POST /api/chat               -> free-form AI chat about currencies
"""

from flask import Flask, render_template, request
from config import Config
from services.currency_service import CurrencyService, CurrencyServiceError
from services.ai_service import AIService, AIServiceError
from utils.helpers import error_response, success_response, validate_currency_code

app = Flask(__name__)
app.config.from_object(Config)

currency_service = CurrencyService()

# The AI service touches the network/SDKs on init (to validate keys),
# so we lazily create it and surface a friendly error if keys are missing
# instead of crashing the whole app at import time.
_ai_service = None


def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# ----------------------------------------------------------------------
# Frontend
# ----------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ----------------------------------------------------------------------
# Currency data endpoints
# ----------------------------------------------------------------------
@app.route("/api/currencies", methods=["GET"])
def get_currencies():
    try:
        currencies = currency_service.get_supported_currencies()
        return success_response(currencies)
    except CurrencyServiceError as exc:
        return error_response(str(exc), 502)


@app.route("/api/convert", methods=["POST"])
def convert_currency():
    payload = request.get_json(silent=True) or {}
    base = payload.get("base", "").upper().strip()
    target = payload.get("target", "").upper().strip()
    amount = payload.get("amount")
    include_explanation = payload.get("include_explanation", True)

    if not validate_currency_code(base) or not validate_currency_code(target):
        return error_response("Please provide valid 3-letter currency codes.")

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return error_response("Amount must be a positive number.")

    try:
        result = currency_service.convert(base, target, amount)
    except CurrencyServiceError as exc:
        return error_response(str(exc), 502)

    explanation = None
    if include_explanation:
        try:
            explanation = get_ai_service().explain_exchange_rate(
                base, target, result["rate"], amount, result["converted_amount"]
            )
        except AIServiceError as exc:
            # Conversion itself still succeeded - just note the AI failure.
            explanation = f"(AI explanation unavailable: {exc})"

    result["explanation"] = explanation
    return success_response(result)


@app.route("/api/historical", methods=["POST"])
def historical_rates():
    payload = request.get_json(silent=True) or {}
    base = payload.get("base", "").upper().strip()
    target = payload.get("target", "").upper().strip()
    days = int(payload.get("days", 30))

    if not validate_currency_code(base) or not validate_currency_code(target):
        return error_response("Please provide valid 3-letter currency codes.")

    days = max(7, min(days, 365))  # clamp to a sane range

    try:
        history = currency_service.get_historical_rates(base, target, days)
        return success_response({"base": base, "target": target, "history": history})
    except CurrencyServiceError as exc:
        return error_response(str(exc), 502)


# ----------------------------------------------------------------------
# AI-powered endpoints
# ----------------------------------------------------------------------
@app.route("/api/trend", methods=["POST"])
def trend_summary():
    payload = request.get_json(silent=True) or {}
    base = payload.get("base", "").upper().strip()
    target = payload.get("target", "").upper().strip()
    days = int(payload.get("days", 30))

    if not validate_currency_code(base) or not validate_currency_code(target):
        return error_response("Please provide valid 3-letter currency codes.")

    try:
        history = currency_service.get_historical_rates(base, target, days)
        summary = get_ai_service().summarize_trend(base, target, history)
        return success_response({"summary": summary, "history": history})
    except CurrencyServiceError as exc:
        return error_response(str(exc), 502)
    except AIServiceError as exc:
        return error_response(str(exc), 502)


@app.route("/api/travel-tips", methods=["POST"])
def travel_tips():
    payload = request.get_json(silent=True) or {}
    base = payload.get("base", "").upper().strip()
    target = payload.get("target", "").upper().strip()

    if not validate_currency_code(base) or not validate_currency_code(target):
        return error_response("Please provide valid 3-letter currency codes.")

    try:
        rate = currency_service.get_live_rate(base, target)
        tips = get_ai_service().travel_recommendation(base, target, rate)
        return success_response({"tips": tips, "rate": rate})
    except CurrencyServiceError as exc:
        return error_response(str(exc), 502)
    except AIServiceError as exc:
        return error_response(str(exc), 502)


@app.route("/api/investment-tips", methods=["POST"])
def investment_tips():
    payload = request.get_json(silent=True) or {}
    base = payload.get("base", "").upper().strip()
    target = payload.get("target", "").upper().strip()
    days = int(payload.get("days", 30))

    if not validate_currency_code(base) or not validate_currency_code(target):
        return error_response("Please provide valid 3-letter currency codes.")

    try:
        history = currency_service.get_historical_rates(base, target, days)
        suggestion = get_ai_service().investment_suggestion(base, target, history)
        return success_response({"suggestion": suggestion})
    except CurrencyServiceError as exc:
        return error_response(str(exc), 502)
    except AIServiceError as exc:
        return error_response(str(exc), 502)


@app.route("/api/compare", methods=["POST"])
def compare_currencies():
    payload = request.get_json(silent=True) or {}
    codes = payload.get("currencies", [])
    codes = [c.upper().strip() for c in codes if validate_currency_code(c)]

    if len(codes) < 2:
        return error_response("Provide at least 2 valid currency codes to compare.")

    try:
        rates = {code: currency_service.get_live_rate("USD", code) for code in codes}
        comparison = get_ai_service().compare_currencies(codes, rates)
        return success_response({"rates": rates, "comparison": comparison})
    except CurrencyServiceError as exc:
        return error_response(str(exc), 502)
    except AIServiceError as exc:
        return error_response(str(exc), 502)


@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    history = payload.get("history", [])  # [{role, content}, ...]

    if not message:
        return error_response("Message cannot be empty.")

    # Basic sanitation: only keep well-formed role/content pairs.
    clean_history = [
        {"role": h.get("role"), "content": h.get("content")}
        for h in history
        if h.get("role") in ("user", "assistant") and h.get("content")
    ][-10:]  # keep the last 10 turns to bound prompt size

    try:
        reply = get_ai_service().chat_reply(clean_history, message)
        return success_response({"reply": reply})
    except AIServiceError as exc:
        return error_response(str(exc), 502)


# ----------------------------------------------------------------------
# Error handlers
# ----------------------------------------------------------------------
@app.errorhandler(404)
def not_found(_e):
    return error_response("Endpoint not found.", 404)


@app.errorhandler(500)
def server_error(_e):
    return error_response("Internal server error.", 500)


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=8000)
