"""
Exchange rate service
----------------------
All logic for talking to the external currency exchange rate API lives
here, kept separate from `app.py` (the Flask routing layer) so the code
is easier to read, test, and swap out later if you want to use a
different provider.

Two providers are supported out of the box:

1. ExchangeRate-API (https://www.exchangerate-api.com/) - used when an
   API key is provided via the EXCHANGE_RATE_API_KEY environment
   variable. This is the recommended, more reliable option and has a
   generous free tier.

2. open.er-api.com - a free, keyless fallback endpoint. This is used
   automatically if no API key is configured, or if the primary
   provider request fails for any reason. It is great for getting the
   project running in under a minute, with no signup required.

A very small in-memory cache is included so that repeatedly converting
between the same currency pair within a short time window does not hit
the external API every single time.
"""

import os
import time
import logging
from typing import Dict, List, Optional

import requests

logger = logging.getLogger("currency-converter.exchange_service")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY", "").strip()

PRIMARY_BASE_URL = "https://v6.exchangerate-api.com/v6"
FALLBACK_BASE_URL = "https://open.er-api.com/v6/latest"

REQUEST_TIMEOUT_SECONDS = 10
CACHE_TTL_SECONDS = 60 * 10  # 10 minutes

# key = base currency code, value = {"rates": {...}, "fetched_at": epoch_seconds}
_rates_cache: Dict[str, Dict] = {}


class ExchangeRateError(Exception):
    """Raised when exchange rate data cannot be retrieved from any provider."""


# ---------------------------------------------------------------------------
# Currency list
# ---------------------------------------------------------------------------
# A curated list of widely used currencies with human friendly names. This
# is intentionally static (not fetched from the API) so the dropdown always
# loads instantly, even if the live-rate API is briefly unavailable.
SUPPORTED_CURRENCIES: List[Dict[str, str]] = [
    {"code": "USD", "name": "United States Dollar"},
    {"code": "EUR", "name": "Euro"},
    {"code": "GBP", "name": "British Pound Sterling"},
    {"code": "JPY", "name": "Japanese Yen"},
    {"code": "AUD", "name": "Australian Dollar"},
    {"code": "CAD", "name": "Canadian Dollar"},
    {"code": "CHF", "name": "Swiss Franc"},
    {"code": "CNY", "name": "Chinese Yuan"},
    {"code": "HKD", "name": "Hong Kong Dollar"},
    {"code": "NZD", "name": "New Zealand Dollar"},
    {"code": "SEK", "name": "Swedish Krona"},
    {"code": "NOK", "name": "Norwegian Krone"},
    {"code": "DKK", "name": "Danish Krone"},
    {"code": "SGD", "name": "Singapore Dollar"},
    {"code": "INR", "name": "Indian Rupee"},
    {"code": "PKR", "name": "Pakistani Rupee"},
    {"code": "BDT", "name": "Bangladeshi Taka"},
    {"code": "AED", "name": "UAE Dirham"},
    {"code": "SAR", "name": "Saudi Riyal"},
    {"code": "QAR", "name": "Qatari Riyal"},
    {"code": "ZAR", "name": "South African Rand"},
    {"code": "NGN", "name": "Nigerian Naira"},
    {"code": "EGP", "name": "Egyptian Pound"},
    {"code": "KES", "name": "Kenyan Shilling"},
    {"code": "BRL", "name": "Brazilian Real"},
    {"code": "MXN", "name": "Mexican Peso"},
    {"code": "ARS", "name": "Argentine Peso"},
    {"code": "CLP", "name": "Chilean Peso"},
    {"code": "COP", "name": "Colombian Peso"},
    {"code": "RUB", "name": "Russian Ruble"},
    {"code": "TRY", "name": "Turkish Lira"},
    {"code": "KRW", "name": "South Korean Won"},
    {"code": "IDR", "name": "Indonesian Rupiah"},
    {"code": "MYR", "name": "Malaysian Ringgit"},
    {"code": "THB", "name": "Thai Baht"},
    {"code": "VND", "name": "Vietnamese Dong"},
    {"code": "PHP", "name": "Philippine Peso"},
    {"code": "PLN", "name": "Polish Zloty"},
    {"code": "CZK", "name": "Czech Koruna"},
    {"code": "HUF", "name": "Hungarian Forint"},
    {"code": "ILS", "name": "Israeli New Shekel"},
]

_SUPPORTED_CODES = {c["code"] for c in SUPPORTED_CURRENCIES}


def get_supported_currencies() -> List[Dict[str, str]]:
    """Return the static list of supported currencies for the dropdowns."""
    return SUPPORTED_CURRENCIES


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _get_cached_rates(base_currency: str) -> Optional[Dict[str, float]]:
    entry = _rates_cache.get(base_currency)
    if not entry:
        return None
    if time.time() - entry["fetched_at"] > CACHE_TTL_SECONDS:
        return None
    return entry["rates"]


def _store_cache(base_currency: str, rates: Dict[str, float]) -> None:
    _rates_cache[base_currency] = {"rates": rates, "fetched_at": time.time()}


def _fetch_from_primary(base_currency: str) -> Dict[str, float]:
    """Fetch live rates from ExchangeRate-API (requires an API key)."""
    if not API_KEY:
        raise ExchangeRateError("No API key configured for primary provider.")

    url = f"{PRIMARY_BASE_URL}/{API_KEY}/latest/{base_currency}"
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()

    if data.get("result") != "success":
        error_type = data.get("error-type", "unknown_error")
        raise ExchangeRateError(f"Primary provider error: {error_type}")

    return data["conversion_rates"]


def _fetch_from_fallback(base_currency: str) -> Dict[str, float]:
    """Fetch live rates from the free, keyless open.er-api.com endpoint."""
    url = f"{FALLBACK_BASE_URL}/{base_currency}"
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()

    if data.get("result") != "success":
        raise ExchangeRateError("Fallback provider did not return a successful result.")

    return data["rates"]


def _get_rates(base_currency: str) -> Dict[str, float]:
    """
    Get exchange rates for a base currency, using the cache first, then the
    primary provider (if an API key is configured), then falling back to
    the free provider automatically.
    """
    cached = _get_cached_rates(base_currency)
    if cached is not None:
        logger.info("Using cached rates for base=%s", base_currency)
        return cached

    # Try primary provider first if a key is configured.
    if API_KEY:
        try:
            rates = _fetch_from_primary(base_currency)
            _store_cache(base_currency, rates)
            logger.info("Fetched live rates from primary provider for base=%s", base_currency)
            return rates
        except Exception as exc:  # noqa: BLE001
            logger.warning("Primary provider failed (%s). Falling back...", exc)

    # Fallback (also used automatically when no API key is set at all).
    try:
        rates = _fetch_from_fallback(base_currency)
        _store_cache(base_currency, rates)
        logger.info("Fetched live rates from fallback provider for base=%s", base_currency)
        return rates
    except Exception as exc:  # noqa: BLE001
        logger.error("Fallback provider also failed: %s", exc)
        raise ExchangeRateError(
            "Unable to fetch live exchange rates right now. Please try again shortly."
        ) from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def convert_currency(from_currency: str, to_currency: str, amount: float) -> Dict:
    """
    Convert `amount` from `from_currency` to `to_currency`.

    Returns a dict with the conversion result and the rate used.
    Raises ExchangeRateError if rates cannot be retrieved or the currency
    codes are not recognised.
    """
    if from_currency not in _SUPPORTED_CODES:
        raise ExchangeRateError(f"Unsupported currency code: {from_currency}")
    if to_currency not in _SUPPORTED_CODES:
        raise ExchangeRateError(f"Unsupported currency code: {to_currency}")

    if from_currency == to_currency:
        return {
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
            "rate": 1.0,
            "result": round(amount, 4),
        }

    rates = _get_rates(from_currency)

    if to_currency not in rates:
        raise ExchangeRateError(
            f"Exchange rate for {to_currency} is currently unavailable."
        )

    rate = rates[to_currency]
    result = amount * rate

    return {
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "rate": round(rate, 6),
        "result": round(result, 4),
    }
