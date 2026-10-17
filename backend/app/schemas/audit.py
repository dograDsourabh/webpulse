import ipaddress
from typing import Optional
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, HttpUrl, field_validator


class AuditRequest(BaseModel):
    url: HttpUrl = Field(description="Public HTTP or HTTPS page to analyze")

    @field_validator("url")
    @classmethod
    def validate_public_target(cls, url):
        parsed = urlsplit(str(url))
        if parsed.username or parsed.password:
            raise ValueError("Website URLs must not contain a username or password.")

        hostname = (parsed.hostname or "").rstrip(".").casefold()
        if not hostname or hostname == "localhost" or hostname.endswith(".localhost"):
            raise ValueError("Enter a publicly reachable website URL.")

        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            address = None
        if address and (not address.is_global or address.is_reserved):
            raise ValueError("Enter a publicly reachable website URL.")

        return url


class ScoreResponse(BaseModel):
    performance: Optional[int] = None
    seo: Optional[int] = None
    accessibility: Optional[int] = None
    bestPractices: Optional[int] = None


class MetricResponse(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[str] = None
    displayValue: Optional[str] = None


class CoreWebVitalsResponse(BaseModel):
    lcp: MetricResponse
    inp: MetricResponse
    cls: MetricResponse


class MetricsResponse(BaseModel):
    fcp: MetricResponse
    tbt: MetricResponse
    speedIndex: MetricResponse
    ttfb: MetricResponse


class RecommendationResponse(BaseModel):
    id: str
    category: str
    priority: str
    title: str

    summary: str

    evidence: dict
    where: dict

    whyItMatters: str

    recommendedActions: list[str]

    example: Optional[dict] = None
    estimatedImpact: Optional[dict] = None


class AuditResponse(BaseModel):
    url: HttpUrl
    scores: ScoreResponse
    coreWebVitals: CoreWebVitalsResponse
    metrics: MetricsResponse
    recommendations: list[RecommendationResponse]


class AuditApiResponse(BaseModel):
    message: str
    data: AuditResponse
