"""
services/currency_service.py
-----------------------------
Everything related to fetching currency data lives here:
- live conversion rates
- historical rates (for trend / comparison charts)
- a small in-memory cache to avoid hammering the external API

Keeping this logic in its own module (instead of app.py) keeps the
Flask routes thin and makes the code easy to test and reuse.
"""

import time
import requests
from config import Config


class CurrencyServiceError(Exception):
    """Raised when the external currency API fails or returns bad data."""
    pass


class CurrencyService:
    """Wraps calls to ExchangeRate-API (live rates) and Frankfurter (history)."""

    def __init__(self):
        self.api_key = Config.EXCHANGE_RATE_API_KEY
        self.base_url = Config.EXCHANGE_RATE_BASE_URL
        self.frankfurter_url = Config.FRANKFURTER_BASE_URL
        self.timeout = Config.REQUEST_TIMEOUT

        # Very small cache: {cache_key: (timestamp, data)}
        self._cache = {}
        self._cache_ttl_seconds = 60 * 10  # 10 minutes

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_cached(self, key):
        entry = self._cache.get(key)
        if not entry:
            return None
        timestamp, data = entry
        if time.time() - timestamp > self._cache_ttl_seconds:
            del self._cache[key]
            return None
        return data

    def _set_cached(self, key, data):
        self._cache[key] = (time.time(), data)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_supported_currencies(self):
        """
        Returns a dict of {currency_code: currency_name}.
        Uses Frankfurter (no API key required) since it exposes a very
        simple currency list endpoint.
        """
        cache_key = "supported_currencies"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            response = requests.get(
                f"{self.frankfurter_url}/currencies", timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            self._set_cached(cache_key, data)
            return data
        except requests.RequestException as exc:
            raise CurrencyServiceError(f"Could not fetch currency list: {exc}")

    def get_live_rate(self, base_currency, target_currency):
        """
        Fetches the live conversion rate from `base_currency` to
        `target_currency` using ExchangeRate-API (requires API key).

        Falls back to Frankfurter (no key needed) if no API key has
        been configured, so the app still works out-of-the-box for
        quick testing.
        """
        base_currency = base_currency.upper()
        target_currency = target_currency.upper()
        cache_key = f"rate:{base_currency}:{target_currency}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if self.api_key:
            url = f"{self.base_url}/{self.api_key}/pair/{base_currency}/{target_currency}"
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                if data.get("result") != "success":
                    raise CurrencyServiceError(
                        data.get("error-type", "Unknown error from ExchangeRate-API")
                    )
                rate = data["conversion_rate"]
                self._set_cached(cache_key, rate)
                return rate
            except requests.RequestException as exc:
                raise CurrencyServiceError(f"ExchangeRate-API request failed: {exc}")

        # --- Fallback: Frankfurter (free, no key) ---
        try:
            response = requests.get(
                f"{self.frankfurter_url}/latest",
                params={"from": base_currency, "to": target_currency},
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            rate = data["rates"][target_currency]
            self._set_cached(cache_key, rate)
            return rate
        except (requests.RequestException, KeyError) as exc:
            raise CurrencyServiceError(f"Fallback currency API failed: {exc}")

    def convert(self, base_currency, target_currency, amount):
        """Converts `amount` of `base_currency` into `target_currency`."""
        rate = self.get_live_rate(base_currency, target_currency)
        converted_amount = round(float(amount) * rate, 4)
        return {
            "base_currency": base_currency.upper(),
            "target_currency": target_currency.upper(),
            "amount": amount,
            "rate": rate,
            "converted_amount": converted_amount,
        }

    def get_historical_rates(self, base_currency, target_currency, days=30):
        """
        Returns a list of {date, rate} for the last `days` days using
        the free Frankfurter historical time-series endpoint.
        """
        base_currency = base_currency.upper()
        target_currency = target_currency.upper()
        cache_key = f"history:{base_currency}:{target_currency}:{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        from datetime import date, timedelta

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        try:
            response = requests.get(
                f"{self.frankfurter_url}/{start_date.isoformat()}..{end_date.isoformat()}",
                params={"from": base_currency, "to": target_currency},
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            rates = data.get("rates", {})
            series = [
                {"date": day, "rate": values.get(target_currency)}
                for day, values in sorted(rates.items())
                if values.get(target_currency) is not None
            ]
            self._set_cached(cache_key, series)
            return series
        except requests.RequestException as exc:
            raise CurrencyServiceError(f"Could not fetch historical rates: {exc}")
