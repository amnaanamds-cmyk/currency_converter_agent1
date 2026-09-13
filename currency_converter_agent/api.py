"""
api.py
------
Handles all live exchange-rate retrieval, local JSON caching, and currency
list lookups for the Currency Converter Agent.

Primary source : Frankfurter API   (https://api.frankfurter.app)
Fallback source: open.er-api.com   (https://open.er-api.com)  -- free, no key

Both endpoints require no API key, which keeps the app "pip install and run"
simple. If both are unreachable, the last successful rate is read from a
local JSON cache file so the app keeps working offline (with a warning
surfaced to the UI layer).
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

import requests

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

FRANKFURTER_LATEST_URL = "https://api.frankfurter.app/latest"
FRANKFURTER_CURRENCIES_URL = "https://api.frankfurter.app/currencies"
FALLBACK_LATEST_URL = "https://open.er-api.com/v6/latest/{base}"

REQUEST_TIMEOUT_SECONDS = 6

def _app_base_dir() -> str:
    """Return the directory the app should treat as "home" for cache files.

    When run as a normal script, this is the folder containing this file.
    When bundled into a PyInstaller .exe, `__file__` points inside a
    temporary extraction folder, so we use the folder containing the
    executable instead, so the cache persists next to the app.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CACHE_DIR = os.path.join(_app_base_dir(), "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "rate_cache.json")

# A reasonably complete static fallback list of currency codes -> display
# names, used only if BOTH the Frankfurter currency-list endpoint and the
# cache are unavailable (e.g. first run with no internet at all).
STATIC_CURRENCY_NAMES: Dict[str, str] = {
    "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound",
    "JPY": "Japanese Yen", "AUD": "Australian Dollar", "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc", "CNY": "Chinese Yuan", "INR": "Indian Rupee",
    "THB": "Thai Baht", "MXN": "Mexican Peso", "BRL": "Brazilian Real",
    "ZAR": "South African Rand", "SGD": "Singapore Dollar",
    "NZD": "New Zealand Dollar", "TRY": "Turkish Lira", "AED": "UAE Dirham",
    "IDR": "Indonesian Rupiah", "VND": "Vietnamese Dong", "KRW": "South Korean Won",
    "EGP": "Egyptian Pound", "MAD": "Moroccan Dirham", "PHP": "Philippine Peso",
    "MYR": "Malaysian Ringgit", "PLN": "Polish Zloty", "CZK": "Czech Koruna",
    "HUF": "Hungarian Forint", "SEK": "Swedish Krona", "NOK": "Norwegian Krone",
    "DKK": "Danish Krone", "ILS": "Israeli Shekel", "ARS": "Argentine Peso",
    "CLP": "Chilean Peso", "COP": "Colombian Peso", "PKR": "Pakistani Rupee",
    "BDT": "Bangladeshi Taka", "LKR": "Sri Lankan Rupee", "NPR": "Nepalese Rupee",
    "KES": "Kenyan Shilling", "NGN": "Nigerian Naira", "HKD": "Hong Kong Dollar",
    "TWD": "New Taiwan Dollar", "SAR": "Saudi Riyal", "QAR": "Qatari Riyal",
    "KWD": "Kuwaiti Dinar", "JOD": "Jordanian Dinar", "ISK": "Icelandic Krona",
    "RON": "Romanian Leu", "BGN": "Bulgarian Lev", "HRK": "Croatian Kuna",
    "RUB": "Russian Ruble", "UAH": "Ukrainian Hryvnia",
}


class CurrencyAPIError(Exception):
    """Raised when live rates cannot be retrieved from any source."""


@dataclass
class RateResult:
    """Container describing the outcome of a rate lookup."""
    base: str
    target: str
    rate: float
    timestamp: str          # ISO-formatted string of when the rate was obtained
    source: str              # "frankfurter" | "fallback" | "cache"
    is_cached: bool = False  # True if this came from the offline cache


# --------------------------------------------------------------------------- #
# Cache helpers
# --------------------------------------------------------------------------- #

def _ensure_cache_dir() -> None:
    """Create the cache directory if it does not already exist."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def _load_cache() -> Dict[str, dict]:
    """Load the full rate cache from disk.

    Returns:
        A dict mapping "BASE_TARGET" -> {"rate", "timestamp", "source"}.
        Returns an empty dict if the cache file does not exist or is corrupt.
    """
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: Dict[str, dict]) -> None:
    """Persist the full rate cache to disk, ignoring write failures."""
    _ensure_cache_dir()
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except OSError:
        # Caching is a convenience feature; failing to write should not
        # crash the app.
        pass


def _cache_key(base: str, target: str) -> str:
    return f"{base.upper()}_{target.upper()}"


def cache_rate(base: str, target: str, rate: float, source: str) -> None:
    """Store a freshly-fetched rate in the local JSON cache.

    Args:
        base: Source currency code (e.g. "USD").
        target: Target currency code (e.g. "EUR").
        rate: Units of target currency per 1 unit of base currency.
        source: Which API produced this rate ("frankfurter" or "fallback").
    """
    cache = _load_cache()
    cache[_cache_key(base, target)] = {
        "rate": rate,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source": source,
    }
    _save_cache(cache)


def get_cached_rate(base: str, target: str) -> Optional[RateResult]:
    """Retrieve a previously cached rate for a currency pair, if any.

    Args:
        base: Source currency code.
        target: Target currency code.

    Returns:
        A RateResult with is_cached=True, or None if nothing is cached
        for this pair.
    """
    cache = _load_cache()
    entry = cache.get(_cache_key(base, target))
    if not entry:
        return None
    return RateResult(
        base=base.upper(),
        target=target.upper(),
        rate=float(entry["rate"]),
        timestamp=entry.get("timestamp", "unknown"),
        source=entry.get("source", "cache"),
        is_cached=True,
    )


# --------------------------------------------------------------------------- #
# Live rate fetching
# --------------------------------------------------------------------------- #

def _fetch_from_frankfurter(base: str, target: str) -> float:
    """Fetch a single exchange rate from the Frankfurter API.

    Args:
        base: Source currency code.
        target: Target currency code.

    Returns:
        The exchange rate (units of target per 1 unit of base).

    Raises:
        CurrencyAPIError: If the request fails or the pair is unsupported.
    """
    params = {"from": base.upper(), "to": target.upper()}
    try:
        resp = requests.get(FRANKFURTER_LATEST_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()
        rate = data.get("rates", {}).get(target.upper())
        if rate is None:
            raise CurrencyAPIError(f"Frankfurter did not return a rate for {base}->{target}.")
        return float(rate)
    except requests.RequestException as exc:
        raise CurrencyAPIError(f"Frankfurter request failed: {exc}") from exc
    except (ValueError, KeyError) as exc:
        raise CurrencyAPIError(f"Frankfurter returned an unexpected response: {exc}") from exc


def _fetch_from_fallback(base: str, target: str) -> float:
    """Fetch a single exchange rate from the open.er-api.com fallback API.

    Args:
        base: Source currency code.
        target: Target currency code.

    Returns:
        The exchange rate (units of target per 1 unit of base).

    Raises:
        CurrencyAPIError: If the request fails or the pair is unsupported.
    """
    url = FALLBACK_LATEST_URL.format(base=base.upper())
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()
        if data.get("result") != "success":
            raise CurrencyAPIError("Fallback API returned an unsuccessful result.")
        rate = data.get("rates", {}).get(target.upper())
        if rate is None:
            raise CurrencyAPIError(f"Fallback API did not return a rate for {base}->{target}.")
        return float(rate)
    except requests.RequestException as exc:
        raise CurrencyAPIError(f"Fallback request failed: {exc}") from exc
    except (ValueError, KeyError) as exc:
        raise CurrencyAPIError(f"Fallback API returned an unexpected response: {exc}") from exc


def get_exchange_rate(base: str, target: str) -> RateResult:
    """Get the current exchange rate for base -> target.

    Tries Frankfurter first, then the fallback API, then finally the local
    cache. Successful live fetches are written back into the cache.

    Args:
        base: Source currency code, e.g. "USD".
        target: Target currency code, e.g. "EUR".

    Returns:
        A RateResult describing the rate and where it came from.

    Raises:
        CurrencyAPIError: If no live source succeeds AND nothing is cached
            for this currency pair.
    """
    base, target = base.upper(), target.upper()

    if base == target:
        return RateResult(base=base, target=target, rate=1.0,
                           timestamp=datetime.now().isoformat(timespec="seconds"),
                           source="identity", is_cached=False)

    # 1. Try Frankfurter
    try:
        rate = _fetch_from_frankfurter(base, target)
        cache_rate(base, target, rate, "frankfurter")
        return RateResult(base=base, target=target, rate=rate,
                           timestamp=datetime.now().isoformat(timespec="seconds"),
                           source="frankfurter", is_cached=False)
    except CurrencyAPIError:
        pass

    # 2. Try fallback API
    try:
        rate = _fetch_from_fallback(base, target)
        cache_rate(base, target, rate, "fallback")
        return RateResult(base=base, target=target, rate=rate,
                           timestamp=datetime.now().isoformat(timespec="seconds"),
                           source="fallback", is_cached=False)
    except CurrencyAPIError:
        pass

    # 3. Fall back to cache
    cached = get_cached_rate(base, target)
    if cached is not None:
        return cached

    raise CurrencyAPIError(
        f"Could not reach any exchange-rate service and no cached rate "
        f"exists for {base}->{target}. Check your internet connection."
    )


def convert_amount(amount: float, base: str, target: str) -> RateResult:
    """Convert an amount from base to target currency using live rates.

    Args:
        amount: The numeric amount to convert (must be >= 0).
        base: Source currency code.
        target: Target currency code.

    Returns:
        A RateResult (the .rate field holds the per-unit rate; multiply by
        `amount` yourself, or use the convenience `converted_amount` below).

    Raises:
        ValueError: If amount is negative.
        CurrencyAPIError: If no rate could be obtained.
    """
    if amount < 0:
        raise ValueError("Amount must be zero or positive.")
    return get_exchange_rate(base, target)


def converted_amount(amount: float, rate_result: RateResult) -> float:
    """Apply a RateResult's rate to an amount.

    Args:
        amount: The numeric amount in the base currency.
        rate_result: A RateResult previously obtained from get_exchange_rate.

    Returns:
        The converted amount in the target currency.
    """
    return amount * rate_result.rate


# --------------------------------------------------------------------------- #
# Supported currency list
# --------------------------------------------------------------------------- #

def get_supported_currencies() -> Dict[str, str]:
    """Get a mapping of currency code -> human-readable name.

    Tries the Frankfurter currency-list endpoint first (most current and
    matches what the conversion endpoint actually supports). Falls back to
    a bundled static list if the network is unavailable.

    Returns:
        Dict like {"USD": "United States Dollar", "EUR": "Euro", ...}.
    """
    try:
        resp = requests.get(FRANKFURTER_CURRENCIES_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and data:
            return data
    except (requests.RequestException, ValueError):
        pass

    return dict(STATIC_CURRENCY_NAMES)
