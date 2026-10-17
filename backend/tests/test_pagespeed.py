import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.services.pagespeed import PageSpeedConfigurationError, run_pagespeed


class PageSpeedServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_sends_page_url_and_key_to_provider_and_returns_lighthouse_data(self):
        payload = {"lighthouseResult": {"audits": {}}}
        response = Mock()
        response.json.return_value = payload
        response.raise_for_status.return_value = None

        client = AsyncMock()
        client.get.return_value = response
        client.__aenter__.return_value = client

        with (
            patch("app.services.pagespeed.settings.pagespeed_api_key", "test-key"),
            patch("app.services.pagespeed.httpx.AsyncClient", return_value=client),
        ):
            result = await run_pagespeed("https://example.com/")

        self.assertEqual(result, payload)
        client.get.assert_awaited_once()
        args, kwargs = client.get.await_args
        self.assertEqual(args[0], "https://www.googleapis.com/pagespeedonline/v5/runPagespeed")
        self.assertEqual(kwargs["params"]["url"], "https://example.com/")
        self.assertEqual(kwargs["params"]["key"], "test-key")
        self.assertEqual(kwargs["params"]["strategy"], "mobile")

    async def test_missing_key_fails_before_network_access(self):
        with (
            patch("app.services.pagespeed.settings.pagespeed_api_key", ""),
            patch("app.services.pagespeed.httpx.AsyncClient") as client,
        ):
            with self.assertRaises(PageSpeedConfigurationError):
                await run_pagespeed("https://example.com/")
        client.assert_not_called()

    async def test_rejects_response_without_lighthouse_result(self):
        response = Mock()
        response.json.return_value = {"error": {"message": "unavailable"}}
        response.raise_for_status.return_value = None
        client = AsyncMock()
        client.get.return_value = response
        client.__aenter__.return_value = client

        with (
            patch("app.services.pagespeed.settings.pagespeed_api_key", "test-key"),
            patch("app.services.pagespeed.httpx.AsyncClient", return_value=client),
        ):
            with self.assertRaisesRegex(ValueError, "did not contain Lighthouse"):
                await run_pagespeed("https://example.com/")


if __name__ == "__main__":
    unittest.main()
