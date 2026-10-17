from app.services.recommendations import generate_recommendations
def normalize_score(score):
    """
    Convert Lighthouse's 0-1 score into a 0-100 score.
    """
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        return None

    return max(0, min(100, round(score * 100)))


def get_audit(audits, audit_id):
    """
    Safely get a Lighthouse audit.
    Returns an empty dictionary if the audit does not exist.
    """
    if not isinstance(audits, dict):
        return {}
    audit = audits.get(audit_id, {})
    return audit if isinstance(audit, dict) else {}


def get_audit_value(audits, audit_id):
    """
    Get the numeric value from a Lighthouse audit.
    """
    audit = get_audit(audits, audit_id)

    value = audit.get("numericValue")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    return value


def get_audit_display_value(audits, audit_id):
    """
    Get the human-readable display value from a Lighthouse audit.
    """
    audit = get_audit(audits, audit_id)

    value = audit.get("displayValue")
    return value if isinstance(value, str) else None


def get_category_score(categories, category_id):
    category = categories.get(category_id, {})
    if not isinstance(category, dict):
        return None
    return category.get("score")


def get_metric_status(metric, value):
    """
    Determine the WebPulse status for a Core Web Vital.
    """

    if value is None:
        return None

    if metric == "lcp":
        if value <= 2500:
            return "good"
        elif value <= 4000:
            return "needs-improvement"
        return "poor"

    if metric == "inp":
        if value <= 200:
            return "good"
        elif value <= 500:
            return "needs-improvement"
        return "poor"

    if metric == "cls":
        if value <= 0.1:
            return "good"
        elif value <= 0.25:
            return "needs-improvement"
        return "poor"

    return None


def normalize_metric(audits, audit_id, unit=None, status_metric=None):
    value = get_audit_value(audits, audit_id)
    display_value = get_audit_display_value(
        audits,
        audit_id,
    )

    if status_metric:
        status = get_metric_status(
            status_metric,
            value,
        )
    elif value is not None or display_value:
        status = "measured"
    else:
        status = None

    return {
        "value": value,
        "unit": unit,
        "status": status,
        "displayValue": display_value,
    }


def normalize_pagespeed_result(url: str, data: dict):
    """
    Convert the raw Google PageSpeed response into
    the WebPulse API response structure.
    """

    if not isinstance(data, dict):
        data = {}
    lighthouse = data.get("lighthouseResult", {})
    if not isinstance(lighthouse, dict):
        lighthouse = {}

    categories = lighthouse.get("categories", {})
    audits = lighthouse.get("audits", {})
    if not isinstance(categories, dict):
        categories = {}
    if not isinstance(audits, dict):
        audits = {}

    return {
        "url": url,

        "scores": {
            "performance": normalize_score(
                get_category_score(categories, "performance")
            ),
            "seo": normalize_score(
                get_category_score(categories, "seo")
            ),
            "accessibility": normalize_score(
                get_category_score(categories, "accessibility")
            ),
            "bestPractices": normalize_score(
                get_category_score(categories, "best-practices")
            ),
        },

        "coreWebVitals": {
            "lcp": normalize_metric(
                audits,
                "largest-contentful-paint",
                unit="ms",
                status_metric="lcp",
            ),

            "inp": normalize_metric(
                audits,
                "interaction-to-next-paint",
                unit="ms",
                status_metric="inp",
            ),

            "cls": normalize_metric(
                audits,
                "cumulative-layout-shift",
                unit="",
                status_metric="cls",
            ),
        },

        "metrics": {
            "fcp": normalize_metric(
                audits,
                "first-contentful-paint",
                unit="ms",
            ),

            "tbt": normalize_metric(
                audits,
                "total-blocking-time",
                unit="ms",
            ),

            "speedIndex": normalize_metric(
                audits,
                "speed-index",
                unit="ms",
            ),

            "ttfb": normalize_metric(
                audits,
                "server-response-time",
                unit="ms",
            ),
        },

        "recommendations": generate_recommendations(audits, url),
    }
