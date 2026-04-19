from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


async def reverse_geocode(lat: float, lon: float) -> str | None:
    """Optional Nominatim reverse geocoding. No-op if not configured."""
    if not settings.nominatim_url:
        return None
    url = f"{settings.nominatim_url.rstrip('/')}/reverse"
    params = {"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 10}
    headers = {"User-Agent": "photos-ai/0.1 (local)"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            data = r.json()
        address = data.get("address", {})
        return (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("county")
        )
    except Exception as e:
        log.debug("reverse_geocode failed: %s", e)
        return None
