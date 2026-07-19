"""Small-cell suppression markers and report-safe value formatting."""

from __future__ import annotations

from numbers import Integral
from typing import Any


def mark_suppressed_groups(payload: Any, threshold: int = 11) -> None:
    """Annotate nested records with an ``n`` count while preserving raw values."""
    if threshold < 1:
        raise ValueError("suppression threshold must be at least 1")

    if isinstance(payload, dict):
        n = payload.get("n")
        if isinstance(n, Integral):
            payload["suppressed_in_reports"] = int(n) < threshold
        for value in payload.values():
            mark_suppressed_groups(value, threshold)
    elif isinstance(payload, list):
        for value in payload:
            mark_suppressed_groups(value, threshold)


def report_value(record: dict[str, Any], key: str, threshold: int = 11) -> Any:
    """Return a display-safe value for a group record."""
    if record.get("suppressed_in_reports") is True:
        return f"suppressed (n<{threshold})"
    return record.get(key)
