"""
travel_data.py
--------------
A curated, offline dataset of practical travel-cost context per currency.

All monetary figures are stored in the *local* currency of that country
(i.e. the currency the amount is denominated in), so they can be converted
into whichever source currency the user is holding using the live exchange
rate fetched elsewhere in the app.

This is intentionally a static, hand-curated dataset (no API dependency)
so the travel-context feature works fully offline. Figures are rough,
2024-era approximations meant to give travelers a general feel for costs,
not precise or guaranteed pricing.
"""

from __future__ import annotations

from typing import Dict, Optional, TypedDict


class BudgetLevels(TypedDict):
    """Rough daily all-in budget estimate, in local currency units."""
    backpacker: float
    mid_range: float
    luxury: float


class TravelContext(TypedDict):
    """Practical travel-cost context for a single currency/country."""
    country: str
    coffee: float          # price of a regular coffee, local currency
    meal: float            # mid-range restaurant meal for one, local currency
    hotel: float           # budget hotel, one night, local currency
    tipping: str            # one-line tipping-culture note
    budget: BudgetLevels    # daily budget estimate, local currency


TRAVEL_DATA: Dict[str, TravelContext] = {
    "USD": {
        "country": "United States",
        "coffee": 5.0, "meal": 22.0, "hotel": 110.0,
        "tipping": "Tipping is expected: 15-20% at restaurants, $1-2 per drink at bars.",
        "budget": {"backpacker": 80, "mid_range": 180, "luxury": 400},
    },
    "EUR": {
        "country": "Eurozone",
        "coffee": 3.2, "meal": 16.0, "hotel": 75.0,
        "tipping": "Not obligatory; rounding up or 5-10% for good service is appreciated.",
        "budget": {"backpacker": 55, "mid_range": 120, "luxury": 280},
    },
    "GBP": {
        "country": "United Kingdom",
        "coffee": 3.0, "meal": 18.0, "hotel": 85.0,
        "tipping": "10-12.5% at restaurants if no service charge is included; not expected in pubs.",
        "budget": {"backpacker": 60, "mid_range": 130, "luxury": 300},
    },
    "JPY": {
        "country": "Japan",
        "coffee": 450, "meal": 1500, "hotel": 8000,
        "tipping": "Tipping is not customary and can even cause confusion; excellent service is the norm.",
        "budget": {"backpacker": 7000, "mid_range": 16000, "luxury": 40000},
    },
    "AUD": {
        "country": "Australia",
        "coffee": 5.0, "meal": 28.0, "hotel": 120.0,
        "tipping": "Not expected; a small tip for exceptional service is a nice bonus, not required.",
        "budget": {"backpacker": 90, "mid_range": 190, "luxury": 420},
    },
    "CAD": {
        "country": "Canada",
        "coffee": 4.0, "meal": 25.0, "hotel": 130.0,
        "tipping": "15-20% at restaurants is standard practice, similar to the US.",
        "budget": {"backpacker": 85, "mid_range": 180, "luxury": 400},
    },
    "CHF": {
        "country": "Switzerland",
        "coffee": 4.5, "meal": 28.0, "hotel": 140.0,
        "tipping": "Service is included by law; rounding up is polite but not required.",
        "budget": {"backpacker": 100, "mid_range": 220, "luxury": 480},
    },
    "CNY": {
        "country": "China",
        "coffee": 28, "meal": 80, "hotel": 350,
        "tipping": "Tipping is not customary and can sometimes be refused or seen as odd.",
        "budget": {"backpacker": 350, "mid_range": 800, "luxury": 2000},
    },
    "INR": {
        "country": "India",
        "coffee": 150, "meal": 500, "hotel": 1800,
        "tipping": "10% at restaurants if no service charge; small notes for porters/drivers appreciated.",
        "budget": {"backpacker": 1800, "mid_range": 4500, "luxury": 12000},
    },
    "THB": {
        "country": "Thailand",
        "coffee": 90, "meal": 250, "hotel": 900,
        "tipping": "Not obligatory; rounding up or leaving small change is a nice gesture.",
        "budget": {"backpacker": 1200, "mid_range": 3000, "luxury": 8000},
    },
    "MXN": {
        "country": "Mexico",
        "coffee": 55, "meal": 250, "hotel": 900,
        "tipping": "10-15% at restaurants is standard and expected.",
        "budget": {"backpacker": 700, "mid_range": 1800, "luxury": 4500},
    },
    "BRL": {
        "country": "Brazil",
        "coffee": 8, "meal": 45, "hotel": 220,
        "tipping": "10% is often included on the bill; if not, it's customary to add it.",
        "budget": {"backpacker": 180, "mid_range": 420, "luxury": 1000},
    },
    "ZAR": {
        "country": "South Africa",
        "coffee": 35, "meal": 180, "hotel": 850,
        "tipping": "10-15% at restaurants is customary and appreciated by service staff.",
        "budget": {"backpacker": 600, "mid_range": 1400, "luxury": 3500},
    },
    "SGD": {
        "country": "Singapore",
        "coffee": 5.5, "meal": 25.0, "hotel": 160.0,
        "tipping": "Not customary; a service charge is usually already included in the bill.",
        "budget": {"backpacker": 90, "mid_range": 200, "luxury": 450},
    },
    "NZD": {
        "country": "New Zealand",
        "coffee": 5.5, "meal": 30.0, "hotel": 130.0,
        "tipping": "Not expected; wages already include service, though tips for great service are welcome.",
        "budget": {"backpacker": 90, "mid_range": 190, "luxury": 420},
    },
    "TRY": {
        "country": "Turkey",
        "coffee": 60, "meal": 300, "hotel": 1400,
        "tipping": "5-10% at restaurants is customary; round up for taxis.",
        "budget": {"backpacker": 900, "mid_range": 2200, "luxury": 6000},
    },
    "AED": {
        "country": "United Arab Emirates",
        "coffee": 18, "meal": 90, "hotel": 400,
        "tipping": "10-15% is appreciated though often not included; check your bill first.",
        "budget": {"backpacker": 300, "mid_range": 700, "luxury": 2000},
    },
    "IDR": {
        "country": "Indonesia",
        "coffee": 35000, "meal": 100000, "hotel": 400000,
        "tipping": "Not required; rounding up or small change for good service is appreciated.",
        "budget": {"backpacker": 450000, "mid_range": 1100000, "luxury": 3000000},
    },
    "VND": {
        "country": "Vietnam",
        "coffee": 30000, "meal": 120000, "hotel": 500000,
        "tipping": "Not traditionally expected, though appreciated at tourist-oriented spots.",
        "budget": {"backpacker": 500000, "mid_range": 1300000, "luxury": 3500000},
    },
    "KRW": {
        "country": "South Korea",
        "coffee": 4800, "meal": 15000, "hotel": 90000,
        "tipping": "Not customary; tipping can occasionally be seen as unusual.",
        "budget": {"backpacker": 70000, "mid_range": 160000, "luxury": 400000},
    },
    "EGP": {
        "country": "Egypt",
        "coffee": 45, "meal": 250, "hotel": 900,
        "tipping": "Baksheesh (small tips) is expected widely, for many small services, not just meals.",
        "budget": {"backpacker": 800, "mid_range": 2000, "luxury": 5500},
    },
    "MAD": {
        "country": "Morocco",
        "coffee": 15, "meal": 120, "hotel": 450,
        "tipping": "5-10% at restaurants; small change for porters and guides is customary.",
        "budget": {"backpacker": 400, "mid_range": 950, "luxury": 2500},
    },
    "PHP": {
        "country": "Philippines",
        "coffee": 130, "meal": 350, "hotel": 1500,
        "tipping": "Not mandatory; 10% is appreciated where a service charge isn't already added.",
        "budget": {"backpacker": 1800, "mid_range": 4000, "luxury": 10000},
    },
    "MYR": {
        "country": "Malaysia",
        "coffee": 10, "meal": 35, "hotel": 160,
        "tipping": "Not customary; a service charge is usually already included in restaurant bills.",
        "budget": {"backpacker": 150, "mid_range": 350, "luxury": 900},
    },
    "PLN": {
        "country": "Poland",
        "coffee": 14, "meal": 60, "hotel": 250,
        "tipping": "10% at restaurants is common practice for good service.",
        "budget": {"backpacker": 180, "mid_range": 420, "luxury": 1000},
    },
    "CZK": {
        "country": "Czech Republic",
        "coffee": 65, "meal": 250, "hotel": 1800,
        "tipping": "Round up the bill or add roughly 10% at restaurants.",
        "budget": {"backpacker": 1200, "mid_range": 2800, "luxury": 6500},
    },
    "HUF": {
        "country": "Hungary",
        "coffee": 900, "meal": 4500, "hotel": 25000,
        "tipping": "10% at restaurants is standard; check if service is already included.",
        "budget": {"backpacker": 16000, "mid_range": 38000, "luxury": 90000},
    },
    "SEK": {
        "country": "Sweden",
        "coffee": 40, "meal": 180, "hotel": 950,
        "tipping": "Not expected; rounding up is common but tipping culture is minimal.",
        "budget": {"backpacker": 650, "mid_range": 1400, "luxury": 3200},
    },
    "NOK": {
        "country": "Norway",
        "coffee": 55, "meal": 220, "hotel": 1100,
        "tipping": "Not expected; a small tip for excellent service is welcome but optional.",
        "budget": {"backpacker": 750, "mid_range": 1600, "luxury": 3600},
    },
    "DKK": {
        "country": "Denmark",
        "coffee": 40, "meal": 200, "hotel": 1000,
        "tipping": "Not expected; service is typically included in the price.",
        "budget": {"backpacker": 700, "mid_range": 1500, "luxury": 3400},
    },
    "ILS": {
        "country": "Israel",
        "coffee": 15, "meal": 90, "hotel": 450,
        "tipping": "12-15% at restaurants is standard and generally expected.",
        "budget": {"backpacker": 350, "mid_range": 800, "luxury": 2200},
    },
    "ARS": {
        "country": "Argentina",
        "coffee": 2000, "meal": 12000, "hotel": 45000,
        "tipping": "10% at restaurants is customary; cash tips are preferred.",
        "budget": {"backpacker": 35000, "mid_range": 80000, "luxury": 200000},
    },
    "CLP": {
        "country": "Chile",
        "coffee": 2200, "meal": 9000, "hotel": 45000,
        "tipping": "10% is customary and often added automatically to the bill; confirm before adding more.",
        "budget": {"backpacker": 30000, "mid_range": 70000, "luxury": 180000},
    },
    "COP": {
        "country": "Colombia",
        "coffee": 6000, "meal": 30000, "hotel": 130000,
        "tipping": "10% is often included ('propina voluntaria'); confirm before adding extra.",
        "budget": {"backpacker": 90000, "mid_range": 220000, "luxury": 600000},
    },
    "PKR": {
        "country": "Pakistan",
        "coffee": 350, "meal": 1200, "hotel": 6000,
        "tipping": "Small tips ('chai pani') for service staff and drivers are customary.",
        "budget": {"backpacker": 5000, "mid_range": 12000, "luxury": 30000},
    },
    "BDT": {
        "country": "Bangladesh",
        "coffee": 200, "meal": 600, "hotel": 2500,
        "tipping": "Not mandatory; small tips for good service are appreciated in cities.",
        "budget": {"backpacker": 2500, "mid_range": 6000, "luxury": 16000},
    },
    "LKR": {
        "country": "Sri Lanka",
        "coffee": 400, "meal": 1500, "hotel": 6000,
        "tipping": "10% is appreciated where not already included in the bill.",
        "budget": {"backpacker": 6000, "mid_range": 14000, "luxury": 35000},
    },
    "NPR": {
        "country": "Nepal",
        "coffee": 250, "meal": 800, "hotel": 3000,
        "tipping": "Tips for trekking guides and porters are customary and often expected.",
        "budget": {"backpacker": 3000, "mid_range": 7000, "luxury": 18000},
    },
    "KES": {
        "country": "Kenya",
        "coffee": 300, "meal": 1200, "hotel": 5000,
        "tipping": "10% at restaurants; tips for safari guides are customary and expected.",
        "budget": {"backpacker": 4000, "mid_range": 9000, "luxury": 25000},
    },
    "NGN": {
        "country": "Nigeria",
        "coffee": 2500, "meal": 8000, "hotel": 35000,
        "tipping": "Not mandatory, but small tips are appreciated for good service.",
        "budget": {"backpacker": 25000, "mid_range": 60000, "luxury": 150000},
    },
    "HKD": {
        "country": "Hong Kong",
        "coffee": 38, "meal": 150, "hotel": 900,
        "tipping": "A 10% service charge is usually already added; extra tipping is optional.",
        "budget": {"backpacker": 500, "mid_range": 1100, "luxury": 2800},
    },
    "TWD": {
        "country": "Taiwan",
        "coffee": 130, "meal": 400, "hotel": 2200,
        "tipping": "Not customary; service charges are usually already included in the bill.",
        "budget": {"backpacker": 1500, "mid_range": 3200, "luxury": 8000},
    },
    "SAR": {
        "country": "Saudi Arabia",
        "coffee": 18, "meal": 80, "hotel": 380,
        "tipping": "10% is appreciated, especially where service is not already included.",
        "budget": {"backpacker": 280, "mid_range": 650, "luxury": 1800},
    },
    "QAR": {
        "country": "Qatar",
        "coffee": 18, "meal": 90, "hotel": 420,
        "tipping": "10-15% is appreciated where a service charge is not already included.",
        "budget": {"backpacker": 320, "mid_range": 750, "luxury": 2000},
    },
    "KWD": {
        "country": "Kuwait",
        "coffee": 1.5, "meal": 8.0, "hotel": 35.0,
        "tipping": "10% is appreciated; check the bill for an already-included service charge.",
        "budget": {"backpacker": 25, "mid_range": 55, "luxury": 150},
    },
    "JOD": {
        "country": "Jordan",
        "coffee": 2.0, "meal": 10.0, "hotel": 45.0,
        "tipping": "10% at restaurants; small tips for guides and drivers are customary.",
        "budget": {"backpacker": 35, "mid_range": 80, "luxury": 220},
    },
    "ISK": {
        "country": "Iceland",
        "coffee": 700, "meal": 3500, "hotel": 18000,
        "tipping": "Not expected; service is included in prices by default.",
        "budget": {"backpacker": 12000, "mid_range": 26000, "luxury": 60000},
    },
    "RON": {
        "country": "Romania",
        "coffee": 12, "meal": 60, "hotel": 250,
        "tipping": "10% at restaurants is common for good service.",
        "budget": {"backpacker": 180, "mid_range": 420, "luxury": 1000},
    },
    "BGN": {
        "country": "Bulgaria",
        "coffee": 4.5, "meal": 25, "hotel": 100,
        "tipping": "10% at restaurants is customary for good service.",
        "budget": {"backpacker": 80, "mid_range": 180, "luxury": 420},
    },
}

# Fallback context used when a currency has no curated entry yet.
_DEFAULT_CONTEXT: TravelContext = {
    "country": "Unknown",
    "coffee": 0.0, "meal": 0.0, "hotel": 0.0,
    "tipping": "No tipping-culture data available yet for this currency.",
    "budget": {"backpacker": 0, "mid_range": 0, "luxury": 0},
}


def get_travel_context(currency_code: str) -> Optional[TravelContext]:
    """Look up the curated travel context for a given currency code.

    Args:
        currency_code: A 3-letter ISO currency code, e.g. "JPY".

    Returns:
        The TravelContext dict for that currency, or None if there is no
        curated data available for it at all.
    """
    return TRAVEL_DATA.get(currency_code.upper())


def has_travel_context(currency_code: str) -> bool:
    """Check whether curated travel context exists for a currency code."""
    return currency_code.upper() in TRAVEL_DATA
