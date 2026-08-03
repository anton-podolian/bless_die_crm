from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo


def parse_price(raw: str) -> float | None:
    """Parse a user-provided price string into a non-negative float, or None if invalid."""
    text = raw.strip().replace(",", ".").replace(" ", "").replace("$", "")
    if not text:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if value < 0:
        return None
    return round(value, 2)


def is_non_empty(raw: str) -> bool:
    return bool(raw and raw.strip())


def parse_kyiv_datetime(raw: str) -> datetime | None:
    """Parse a Kyiv date/time and return an aware UTC datetime."""
    text = raw.strip()
    for date_format in ("%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            parsed = datetime.strptime(text, date_format)
        except ValueError:
            continue
        if date_format == "%d.%m.%Y":
            parsed = parsed.replace(hour=12)
        return parsed.replace(tzinfo=ZoneInfo("Europe/Kyiv")).astimezone(UTC)
    return None
