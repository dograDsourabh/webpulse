import unittest
from unittest.mock import AsyncMock, patch

import httpx

from app.main import app
from app.services.pagespeed import PageSpeedConfigurationError


class AuditApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        )

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_success_returns_normalized_audit(self):
        provider_result = {
            "lighthouseResult": {
                "categories": {
                    "performance": {"score": 0.82},
                    "seo": {"score": 1},
                    "accessibility": {"score": 0.9},
                    "best-practices": {"score": 1},
                },
                "audits": {
                    "largest-contentful-paint": {"numericValue": 2600, "displayValue": "2.6 s"},
                    "interaction-to-next-paint": {"numericValue": 100, "displayValue": "100 ms"},
                    "cumulative-layout-shift": {"numericValue": 0.02, "displayValue": "0.02"},
                    "document-title": {"score": 0},
                },
            }
        }
        with patch("app.api.routes.audit.run_pagespeed", new=AsyncMock(return_value=provider_result)) as run:
            response = await self.client.post("/api/audit", json={"url": "https://example.com"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["scores"]["performance"], 82)
        self.assertEqual(response.json()["data"]["recommendations"][0]["id"], "missing-title")
        run.assert_awaited_once_with("https://example.com/")

    async def test_provider_timeout_returns_actionable_error_without_internals(self):
        timeout = httpx.ReadTimeout("provider timed out")
        with patch("app.api.routes.audit.run_pagespeed", new=AsyncMock(side_effect=timeout)):
            response = await self.client.post("/api/audit", json={"url": "https://example.com"})

        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json()["detail"]["code"], "pagespeed_timeout")
        self.assertIn("Try again", response.json()["detail"]["message"])
        self.assertNotIn("provider timed out", response.text)

    async def test_missing_api_key_is_reported_as_configuration_error(self):
        with patch(
            "app.api.routes.audit.run_pagespeed",
            new=AsyncMock(side_effect=PageSpeedConfigurationError()),
        ):
            response = await self.client.post("/api/audit", json={"url": "https://example.com"})

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"]["code"], "pagespeed_not_configured")

    async def test_provider_rate_limit_returns_retryable_error(self):
        request = httpx.Request("GET", "https://pagespeed.example/result")
        response_error = httpx.HTTPStatusError(
            "provider limited request",
            request=request,
            response=httpx.Response(429, request=request),
        )
        with patch("app.api.routes.audit.run_pagespeed", new=AsyncMock(side_effect=response_error)):
            response = await self.client.post("/api/audit", json={"url": "https://example.com"})

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"]["code"], "pagespeed_rate_limited")
        self.assertIn("Try again shortly", response.json()["detail"]["message"])

    async def test_rejects_local_and_credential_bearing_targets(self):
        for url in ("http://localhost", "http://127.0.0.1", "https://user:password@example.com"):
            with self.subTest(url=url):
                response = await self.client.post("/api/audit", json={"url": url})
                self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
