from __future__ import annotations


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
