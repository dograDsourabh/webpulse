"""Lighthouse audit rules and the shared WebPulse recommendation contract."""

import re
from urllib.parse import urlsplit, urlunsplit


MAX_EVIDENCE_ITEMS = 10


def _recommendation(
    *,
    id,
    category,
    priority,
    title,
    summary,
    evidence,
    where,
    why_it_matters,
    actions,
    example=None,
    impact=None,
):
    """Return the complete, stable shape consumed by the API and UI."""
    return {
        "id": id,
        "category": category,
        "priority": priority,
        "title": title,
        "summary": summary,
        "evidence": evidence or {},
        "where": where or {},
        "whyItMatters": why_it_matters,
        "recommendedActions": actions,
        "example": example,
        "estimatedImpact": impact,
    }


def _get_audit(audits, audit_id):
    if not isinstance(audits, dict):
        return None
    audit = audits.get(audit_id)
    return audit if isinstance(audit, dict) else None


def _get_details(audit):
    details = audit.get("details")
    return details if isinstance(details, dict) else {}


def _get_items(audit):
    items = _get_details(audit).get("items", [])
    return items if isinstance(items, list) else []


def _has_issue(audit):
    score = audit.get("score")
    return isinstance(score, (int, float)) and not isinstance(score, bool) and score < 0.9


def _positive(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0 else None


def _number_or_zero(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else 0


def sanitize_resource_url(url):
    """Remove URL credentials, query parameters, and fragments from evidence."""
    if not isinstance(url, str) or not url.strip():
        return None

    try:
        parsed = urlsplit(url.strip())
        hostname = parsed.hostname
        if parsed.scheme and hostname:
            host = f"[{hostname}]" if ":" in hostname else hostname
            port = parsed.port
            netloc = f"{host}:{port}" if port is not None else host
        else:
            netloc = ""
        return urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))
    except (TypeError, ValueError):
        return None


_URL_IN_TEXT = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def _sanitize_text(value):
    if not isinstance(value, str):
        return value

    def replace(match):
        raw_url = match.group(0)
        trailing = ""
        while raw_url and raw_url[-1] in ".,;:!?)":
            trailing = raw_url[-1] + trailing
            raw_url = raw_url[:-1]
        return (sanitize_resource_url(raw_url) or "[redacted URL]") + trailing

    return _URL_IN_TEXT.sub(replace, value)


def get_resource_host(url):
    sanitized = sanitize_resource_url(url)
    if not sanitized:
        return None
    try:
        return urlsplit(sanitized).hostname
    except ValueError:
        return None


def is_third_party_resource(resource_url, page_url):
    resource_host = get_resource_host(resource_url)
    page_host = get_resource_host(page_url)
    if not resource_host or not page_host:
        return None
    return resource_host.casefold() != page_host.casefold()


def _affected_node(item):
    node = item.get("node")
    if not isinstance(node, dict):
        return None
    evidence = {
        key: _sanitize_text(node.get(key))
        for key in ("snippet", "selector", "explanation")
        if node.get(key) is not None
    }
    return evidence or None


def check_large_images(audits, page_url=None):
    audit = _get_audit(audits, "uses-optimized-images")
    if not audit or not _has_issue(audit):
        return None

    items = _get_items(audit)
    resources = []
    for item in items[:MAX_EVIDENCE_ITEMS]:
        if not isinstance(item, dict):
            continue
        url = sanitize_resource_url(item.get("url"))
        if url:
            resources.append({
                "url": url,
                "totalBytes": item.get("totalBytes"),
                "wastedBytes": item.get("wastedBytes"),
                "wastedPercent": item.get("wastedPercent"),
            })

    details = _get_details(audit)
    savings_bytes = details.get("overallSavingsBytes")
    savings_ms = _positive(details.get("overallSavingsMs"))
    return _recommendation(
        id="large-images", category="performance", priority="HIGH",
        title="Optimize oversized images",
        summary="Some images may be larger than necessary and could slow page loading.",
        evidence={
            "auditId": "uses-optimized-images", "score": audit.get("score"),
            "displayValue": audit.get("displayValue"),
            "affectedResources": resources, "totalAffectedResources": len(items),
            "potentialSavingsBytes": savings_bytes, "potentialSavingsMs": savings_ms,
        },
        where={"type": "image-resources", "description": "Review the affected image resources listed in the evidence."},
        why_it_matters="Large image files require more data to download and can delay important page content, especially on slower networks and mobile devices.",
        actions=[
            "Resize images to their displayed dimensions.",
            "Convert suitable JPEG and PNG files to WebP or AVIF.",
            "Compress images and serve responsive sizes.",
        ],
        example={"language": "html", "code": '<img src="/images/hero.webp" width="1200" height="600" alt="Hero image">'},
        impact={"potentialSavingsBytes": savings_bytes, "potentialSavingsMs": savings_ms},
    )


def check_render_blocking_resources(audits, page_url=None):
    audit = _get_audit(audits, "render-blocking-resources")
    if not audit or not _has_issue(audit):
        return None

    items = _get_items(audit)
    resources = []
    for item in items[:MAX_EVIDENCE_ITEMS]:
        if not isinstance(item, dict):
            continue
        url = sanitize_resource_url(item.get("url"))
        if url:
            resources.append({"url": url, "totalBytes": item.get("totalBytes"), "wastedMs": item.get("wastedMs")})

    savings_ms = _positive(_get_details(audit).get("overallSavingsMs"))
    return _recommendation(
        id="render-blocking-resources", category="performance", priority="HIGH",
        title="Reduce render-blocking resources",
        summary="Some CSS or JavaScript resources may delay the initial page rendering.",
        evidence={
            "auditId": "render-blocking-resources", "score": audit.get("score"),
            "displayValue": audit.get("displayValue"), "affectedResources": resources,
            "totalAffectedResources": len(items), "potentialSavingsMs": savings_ms,
        },
        where={"type": "render-blocking-resources", "description": "Review the stylesheet and script resources listed in the evidence."},
        why_it_matters="Render-blocking resources can delay the first useful content. Reducing unnecessary blocking work can make the page appear sooner.",
        actions=[
            "Remove CSS and JavaScript that is not needed for the initial render.",
            "Inline small critical CSS where appropriate.",
            "Defer non-critical scripts and avoid unnecessary third-party resources during startup.",
        ],
        example={"language": "html", "code": '<script src="/js/non-critical.js" defer></script>'},
        impact={"potentialSavingsMs": savings_ms, "displayValue": audit.get("displayValue")},
    )


def check_unused_javascript(audits, page_url=None):
    audit = _get_audit(audits, "unused-javascript")
    if not audit or not _has_issue(audit):
        return None

    resources_by_url = {}
    items = _get_items(audit)
    for item in items:
        if not isinstance(item, dict):
            continue
        url = sanitize_resource_url(item.get("url"))
        if not url:
            continue
        resource = resources_by_url.setdefault(url, {
            "url": url,
            "host": get_resource_host(url),
            "isThirdParty": is_third_party_resource(url, page_url),
            "totalBytes": 0,
            "wastedBytes": 0,
            "occurrences": 0,
        })
        resource["totalBytes"] += _number_or_zero(item.get("totalBytes"))
        resource["wastedBytes"] += _number_or_zero(item.get("wastedBytes"))
        resource["occurrences"] += 1

    details = _get_details(audit)
    savings_bytes = details.get("overallSavingsBytes")
    savings_ms = _positive(details.get("overallSavingsMs"))
    return _recommendation(
        id="unused-javascript", category="performance", priority="MEDIUM",
        title="Reduce unused JavaScript",
        summary="The page loads JavaScript that may not be needed for the initial experience.",
        evidence={
            "auditId": "unused-javascript", "score": audit.get("score"),
            "displayValue": audit.get("displayValue"),
            "affectedResources": list(resources_by_url.values())[:MAX_EVIDENCE_ITEMS],
            "totalAffectedResources": len(resources_by_url),
            "potentialSavingsBytes": savings_bytes, "potentialSavingsMs": savings_ms,
        },
        where={"type": "javascript-resources", "description": "Review the JavaScript resources listed in the evidence."},
        why_it_matters="Unused JavaScript adds download, parse, and execution work. That can delay interactivity, especially on mobile devices.",
        actions=[
            "Remove code and dependencies that are no longer used.",
            "Load features only when visitors need them.",
            "Split large bundles and defer non-critical scripts.",
            "Review third-party scripts and conditionally load plugins where possible.",
        ],
        example={"language": "javascript", "code": "const feature = await import('./feature.js');\nfeature.init();"},
        impact={
            "description": "Potential savings reported by Lighthouse.",
            "potentialSavingsBytes": savings_bytes,
            "potentialSavingsMs": savings_ms,
            "displayValue": audit.get("displayValue"),
        },
    )


def check_missing_title(audits, page_url=None):
    audit = _get_audit(audits, "document-title")
    if not audit or not _has_issue(audit):
        return None
    return _recommendation(
        id="missing-title", category="seo", priority="HIGH",
        title="Add a descriptive page title",
        summary="The page does not have a descriptive HTML title.",
        evidence={"auditId": "document-title", "score": audit.get("score"), "displayValue": audit.get("displayValue")},
        where={"type": "html-head", "location": "<head>", "description": "Add a title element inside the page head."},
        why_it_matters="The page title helps visitors and search engines understand the page and is commonly shown in search results.",
        actions=["Add a unique title element.", "Keep it descriptive and relevant to the page content."],
        example={"language": "html", "code": "<title>Page topic | Site name</title>"},
    )


def check_missing_meta_description(audits, page_url=None):
    audit = _get_audit(audits, "meta-description")
    if not audit or not _has_issue(audit):
        return None
    return _recommendation(
        id="missing-meta-description", category="seo", priority="MEDIUM",
        title="Add a meta description",
        summary="This page does not have a meta description that summarizes its content.",
        evidence={"auditId": "meta-description", "score": audit.get("score"), "displayValue": audit.get("displayValue")},
        where={"type": "html-head", "location": "<head>", "description": "Add a meta description to the page head."},
        why_it_matters="A useful description helps search engines understand the page and may appear beneath its title in search results.",
        actions=["Write a concise, accurate summary of the page.", "Use a distinct description for each important page."],
        example={"language": "html", "code": '<meta name="description" content="A concise summary of this page">'},
    )


def check_image_alt(audits, page_url=None):
    audit = _get_audit(audits, "image-alt")
    if not audit or not _has_issue(audit):
        return None
    items = _get_items(audit)
    elements = [node for item in items if isinstance(item, dict) if (node := _affected_node(item))]
    return _recommendation(
        id="image-alt", category="accessibility", priority="HIGH",
        title="Add alternative text to images",
        summary="Some images may be missing alternative text.",
        evidence={"auditId": "image-alt", "score": audit.get("score"), "displayValue": audit.get("displayValue"), "affectedElements": elements[:MAX_EVIDENCE_ITEMS], "totalAffectedElements": len(items)},
        where={"type": "html-elements", "description": "Review the affected image elements listed in the evidence."},
        why_it_matters="Alternative text communicates informative image content to people who use screen readers or cannot see the image.",
        actions=["Add concise, meaningful alt text to informative images.", "Use an empty alt attribute for decorative images.", "Avoid repeating nearby text."],
        example={"language": "html", "code": '<img src="/images/team.jpg" alt="Our development team">'},
    )


def check_form_labels(audits, page_url=None):
    audit = _get_audit(audits, "label")
    if not audit or not _has_issue(audit):
        return None
    items = _get_items(audit)
    elements = [node for item in items if isinstance(item, dict) if (node := _affected_node(item))]
    return _recommendation(
        id="form-labels", category="accessibility", priority="HIGH",
        title="Add labels to form fields",
        summary="Some form controls may not have accessible labels.",
        evidence={"auditId": "label", "score": audit.get("score"), "displayValue": audit.get("displayValue"), "affectedElements": elements[:MAX_EVIDENCE_ITEMS], "totalAffectedElements": len(items)},
        where={"type": "form-elements", "description": "Review the affected form controls listed in the evidence."},
        why_it_matters="Clear labels help everyone understand form fields and are essential for screen reader users.",
        actions=["Give every form control an accessible name.", "Associate visible labels with their inputs.", "Use descriptive wording for the expected information."],
        example={"language": "html", "code": '<label for="email">Email address</label>\n<input id="email" name="email" type="email">'},
    )


def check_document_language(audits, page_url=None):
    audit = _get_audit(audits, "html-has-lang")
    if not audit or not _has_issue(audit):
        return None
    return _recommendation(
        id="document-language", category="accessibility", priority="MEDIUM",
        title="Define the document language",
        summary="The document does not declare its primary language.",
        evidence={"auditId": "html-has-lang", "score": audit.get("score"), "displayValue": audit.get("displayValue")},
        where={"type": "html-element", "location": "<html>", "description": "Set the lang attribute on the root HTML element."},
        why_it_matters="Assistive technologies use the declared language to pronounce and interpret page content correctly.",
        actions=["Set the HTML lang attribute.", "Use a language code that matches the page content."],
        example={"language": "html", "code": '<html lang="en">'},
    )


def check_color_contrast(audits, page_url=None):
    audit = _get_audit(audits, "color-contrast")
    if not audit or not _has_issue(audit):
        return None
    items = _get_items(audit)
    elements = [node for item in items if isinstance(item, dict) if (node := _affected_node(item))]
    return _recommendation(
        id="color-contrast", category="accessibility", priority="MEDIUM",
        title="Improve color contrast",
        summary="Some text or interface elements may not have enough contrast against their background.",
        evidence={"auditId": "color-contrast", "score": audit.get("score"), "displayValue": audit.get("displayValue"), "affectedElements": elements[:MAX_EVIDENCE_ITEMS], "totalAffectedElements": len(items)},
        where={"type": "html-elements", "description": "Review the affected elements listed in the evidence."},
        why_it_matters="Poor contrast can make content difficult to read, particularly for people with low vision or color-vision deficiencies.",
        actions=["Increase contrast between text and its background.", "Check text and interface colors against accessibility contrast thresholds.", "Review hover, focus, and disabled states too."],
        example={"language": "css", "code": ".button {\n  color: #fff;\n  background: #1e40af;\n}"},
    )


def check_deprecated_apis(audits, page_url=None):
    audit = _get_audit(audits, "deprecations")
    if not audit or not _has_issue(audit):
        return None
    items = _get_items(audit)
    details = _get_details(audit)
    return _recommendation(
        id="deprecated-apis", category="best-practices", priority="MEDIUM",
        title="Remove deprecated browser APIs",
        summary="The page uses browser APIs that are deprecated or no longer recommended.",
        evidence={"auditId": "deprecations", "score": audit.get("score"), "displayValue": audit.get("displayValue"), "affectedItems": [_sanitize_text(item.get("description")) for item in items[:MAX_EVIDENCE_ITEMS] if isinstance(item, dict) and item.get("description")], "totalAffectedItems": len(items)},
        where={"type": "javascript", "description": "Review the deprecated API details reported by Lighthouse."},
        why_it_matters="Deprecated APIs may be removed by browsers and can make a site less reliable and harder to maintain.",
        actions=["Identify which script or dependency uses each deprecated API.", "Replace it with a supported alternative and test affected browser behavior."],
    )


def check_https(audits, page_url=None):
    audit = _get_audit(audits, "is-on-https")
    if not audit or not _has_issue(audit):
        return None
    return _recommendation(
        id="https", category="best-practices", priority="HIGH",
        title="Serve the website over HTTPS",
        summary="This page is not being served securely over HTTPS.",
        evidence={"auditId": "is-on-https", "score": audit.get("score"), "displayValue": audit.get("displayValue")},
        where={"type": "website", "description": "Configure the site URL and server to use HTTPS."},
        why_it_matters="HTTPS protects the integrity and confidentiality of data exchanged between the website and its visitors.",
        actions=["Configure a valid TLS certificate.", "Redirect HTTP requests to HTTPS.", "Update internal links and resources to use HTTPS."],
        example={"language": "text", "code": "http://example.com → https://example.com"},
    )


def check_console_errors(audits, page_url=None):
    audit = _get_audit(audits, "errors-in-console")
    if not audit or not _has_issue(audit):
        return None
    items = _get_items(audit)
    errors = []
    for item in items[:MAX_EVIDENCE_ITEMS]:
        if not isinstance(item, dict):
            continue
        source_location = item.get("sourceLocation")
        if not isinstance(source_location, dict):
            source_location = {}
        errors.append({
            "message": _sanitize_text(item.get("description")),
            "source": _sanitize_text(item.get("source")),
            "url": sanitize_resource_url(source_location.get("url")),
            "line": source_location.get("line"),
            "column": source_location.get("column"),
        })
    return _recommendation(
        id="console-errors", category="best-practices", priority="MEDIUM",
        title="Fix browser console errors",
        summary="JavaScript or browser errors were detected and may indicate broken functionality or failed resources.",
        evidence={"auditId": "errors-in-console", "score": audit.get("score"), "displayValue": audit.get("displayValue"), "errors": errors, "totalErrors": len(items)},
        where={"type": "browser-console", "description": "Review the sanitized messages and source locations listed in the evidence."},
        why_it_matters="Console errors can indicate broken scripts, failed requests, security restrictions, or functionality that is not working as intended.",
        actions=["Identify whether each error comes from your code or a third-party service.", "Fix failed requests or scripts, then retest the affected page behavior."],
    )


def check_heading_structure(audits, page_url=None):
    audit = _get_audit(audits, "heading-order")
    if not audit or not _has_issue(audit):
        return None
    items = _get_items(audit)
    elements = [node for item in items if isinstance(item, dict) if (node := _affected_node(item))]
    return _recommendation(
        id="heading-structure", category="accessibility", priority="MEDIUM",
        title="Improve heading structure",
        summary="Some headings may not follow a logical hierarchy.",
        evidence={"auditId": "heading-order", "score": audit.get("score"), "displayValue": audit.get("displayValue"), "affectedElements": elements[:MAX_EVIDENCE_ITEMS], "totalAffectedElements": len(items)},
        where={"type": "html-elements", "description": "Review the affected headings listed in the evidence."},
        why_it_matters="A clear heading hierarchy helps visitors scan and navigate content, including people using screen readers.",
        actions=["Use headings to reflect the page outline.", "Follow a logical hierarchy and avoid skipping levels without a reason."],
        example={"language": "html", "code": "<h1>Website performance</h1>\n<h2>Core Web Vitals</h2>\n<h3>Largest Contentful Paint</h3>"},
    )


RECOMMENDATION_RULES = (
    check_large_images,
    check_render_blocking_resources,
    check_unused_javascript,
    check_missing_title,
    check_missing_meta_description,
    check_image_alt,
    check_form_labels,
    check_document_language,
    check_color_contrast,
    check_deprecated_apis,
    check_https,
    check_console_errors,
    check_heading_structure,
)


def generate_recommendations(audits, page_url=None):
    """Run every recommendation rule using the same callable interface."""
    recommendations = []
    for rule in RECOMMENDATION_RULES:
        recommendation = rule(audits, page_url)
        if recommendation is not None:
            recommendations.append(recommendation)
    return recommendations
