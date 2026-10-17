import httpx

from app.core.config import settings


PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


class PageSpeedConfigurationError(Exception):
    """Raised when the PageSpeed API key is not configured."""


async def run_pagespeed(url: str):
    if not settings.pagespeed_api_key:
        raise PageSpeedConfigurationError

    params = {
        "url": url,
        "key": settings.pagespeed_api_key,
        "strategy": "mobile",
        "category": [
            "performance",
            "seo",
            "accessibility",
            "best-practices",
        ],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(
            PAGESPEED_API_URL,
            params=params,
        )

    response.raise_for_status()

    data = response.json()
    if not isinstance(data, dict) or not isinstance(data.get("lighthouseResult"), dict):
        raise ValueError("PageSpeed response did not contain Lighthouse results.")
    return data
