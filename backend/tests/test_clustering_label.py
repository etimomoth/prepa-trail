from __future__ import annotations

from datetime import datetime

from app.services.clustering import _label_from


def test_label_single_day() -> None:
    d = datetime(2025, 8, 1, 10, 0)
    assert _label_from("beach", d, d) == "beach · 2025-08-01"


def test_label_date_range() -> None:
    a = datetime(2025, 8, 1)
    b = datetime(2025, 8, 5)
    assert _label_from("mountain", a, b) == "mountain · 2025-08-01 → 2025-08-05"


def test_label_no_scene_uses_dates_only() -> None:
    a = datetime(2025, 8, 1)
    assert _label_from(None, a, a) == "2025-08-01"


def test_label_fallback() -> None:
    assert _label_from(None, None, None) == "unnamed"
