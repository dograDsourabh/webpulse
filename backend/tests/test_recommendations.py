import inspect
import unittest

from app.services.normalizer import get_metric_status, normalize_pagespeed_result, normalize_score
from app.services.recommendations import (
    RECOMMENDATION_RULES,
    check_console_errors,
    check_image_alt,
    check_missing_title,
    check_unused_javascript,
    generate_recommendations,
)


class RecommendationTests(unittest.TestCase):
    def test_every_rule_uses_the_shared_two_argument_interface(self):
        for rule in RECOMMENDATION_RULES:
            with self.subTest(rule=rule.__name__):
                self.assertEqual(len(inspect.signature(rule).parameters), 2)
                self.assertIsNone(rule({}, "https://example.com/"))

    def test_recommendations_have_the_complete_contract(self):
        audits = {
            "uses-optimized-images": {"score": 0, "details": {"items": []}},
            "render-blocking-resources": {"score": 0, "details": {"items": []}},
            "unused-javascript": {"score": 0, "details": {"items": []}},
            "document-title": {"score": 0},
            "meta-description": {"score": 0},
            "image-alt": {"score": 0, "details": {"items": []}},
            "label": {"score": 0, "details": {"items": []}},
            "html-has-lang": {"score": 0},
            "color-contrast": {"score": 0, "details": {"items": []}},
            "deprecations": {"score": 0, "details": {"items": []}},
            "is-on-https": {"score": 0},
            "errors-in-console": {"score": 0, "details": {"items": []}},
            "heading-order": {"score": 0, "details": {"items": []}},
        }
        recommendations = generate_recommendations(audits, "https://example.com/")
        self.assertEqual(len(recommendations), len(RECOMMENDATION_RULES))

        contract = {
            "id", "category", "priority", "title", "summary", "evidence",
            "where", "whyItMatters", "recommendedActions", "example", "estimatedImpact",
        }
        for recommendation in recommendations:
            with self.subTest(recommendation=recommendation["id"]):
                self.assertEqual(set(recommendation), contract)
                self.assertIsInstance(recommendation["evidence"], dict)
                self.assertIsInstance(recommendation["where"], dict)
                self.assertIsInstance(recommendation["recommendedActions"], list)
                self.assertTrue(recommendation["whyItMatters"])

    def test_missing_title_requires_a_numeric_failing_score(self):
        self.assertIsNone(check_missing_title({"document-title": {"score": None}}))
        self.assertIsNone(check_missing_title({"document-title": {"score": 0.9}}))
        self.assertEqual(
            check_missing_title({"document-title": {"score": 0}})["id"],
            "missing-title",
        )

    def test_unused_javascript_aggregates_resources_and_hides_url_secrets(self):
        audits = {
            "unused-javascript": {
                "score": 0.2,
                "details": {
                    "items": [
                        {"url": "https://user:pass@cdn.example/app.js?token=one#part", "totalBytes": 100, "wastedBytes": 50},
                        {"url": "https://cdn.example/app.js?token=two", "totalBytes": 200, "wastedBytes": 75},
                        {"url": "https://example.com/site.js?key=secret", "totalBytes": 100, "wastedBytes": 20},
                    ],
                    "overallSavingsBytes": 145,
                    "overallSavingsMs": 0,
                },
            }
        }
        recommendation = check_unused_javascript(audits, "https://example.com/")
        resources = recommendation["evidence"]["affectedResources"]

        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0]["url"], "https://cdn.example/app.js")
        self.assertEqual(resources[0]["totalBytes"], 300)
        self.assertEqual(resources[0]["wastedBytes"], 125)
        self.assertTrue(resources[0]["isThirdParty"])
        self.assertFalse(resources[1]["isThirdParty"])
        self.assertIsNone(recommendation["estimatedImpact"]["potentialSavingsMs"])
        self.assertNotIn("token", str(recommendation))
        self.assertNotIn("pass", str(recommendation))

    def test_console_error_evidence_is_sanitized_and_capped(self):
        items = [
            {
                "description": "Failed https://cdn.example/app.js?token=secret#debug",
                "source": "Script https://cdn.example/app.js?key=secret",
                "sourceLocation": {
                    "url": "https://user:pass@cdn.example/app.js?token=secret#debug",
                    "line": 12,
                    "column": 3,
                },
            }
        ] * 12
        recommendation = check_console_errors(
            {"errors-in-console": {"score": 0, "details": {"items": items}}},
            "https://example.com/",
        )
        evidence = recommendation["evidence"]

        self.assertEqual(evidence["totalErrors"], 12)
        self.assertEqual(len(evidence["errors"]), 10)
        self.assertEqual(evidence["errors"][0]["url"], "https://cdn.example/app.js")
        self.assertEqual(evidence["errors"][0]["message"], "Failed https://cdn.example/app.js")
        self.assertNotIn("secret", str(evidence))
        self.assertNotIn("user:pass", str(evidence))

    def test_image_alt_handles_multiple_elements_and_empty_details(self):
        recommendation = check_image_alt({
            "image-alt": {
                "score": 0,
                "details": {"items": [
                    {"node": {"snippet": "<img>", "selector": "img.a"}},
                    {"node": {"snippet": "<img>", "selector": "img.b"}},
                ]},
            }
        })
        self.assertEqual(len(recommendation["evidence"]["affectedElements"]), 2)
        self.assertEqual(recommendation["evidence"]["affectedElements"][1]["selector"], "img.b")
        self.assertIsNotNone(check_image_alt({"image-alt": {"score": 0, "details": {"items": []}}}))

    def test_normalizer_handles_missing_and_malformed_provider_fields(self):
        normalized = normalize_pagespeed_result("https://example.com/", {"lighthouseResult": {"categories": {"performance": "invalid"}, "audits": []}})
        self.assertIsNone(normalized["scores"]["performance"])
        self.assertEqual(normalized["recommendations"], [])
        self.assertIsNone(normalize_score(None))
        self.assertIsNone(normalize_score(True))
        self.assertEqual(normalize_score(1.4), 100)

    def test_core_web_vital_thresholds(self):
        self.assertEqual(get_metric_status("lcp", 2500), "good")
        self.assertEqual(get_metric_status("lcp", 2501), "needs-improvement")
        self.assertEqual(get_metric_status("lcp", 4001), "poor")
        self.assertEqual(get_metric_status("inp", 200), "good")
        self.assertEqual(get_metric_status("inp", 501), "poor")
        self.assertEqual(get_metric_status("cls", 0.1), "good")
        self.assertEqual(get_metric_status("cls", 0.251), "poor")
        self.assertIsNone(get_metric_status("lcp", None))


if __name__ == "__main__":
    unittest.main()
