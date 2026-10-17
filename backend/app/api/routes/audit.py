import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.audit import AuditApiResponse, AuditRequest
from app.services.pagespeed import PageSpeedConfigurationError, run_pagespeed
from app.services.normalizer import normalize_pagespeed_result


router = APIRouter(
    prefix="/api",
    tags=["Audit"],
)


@router.post("/audit"
            , response_model=AuditApiResponse)
async def create_audit(request: AuditRequest):
    try:
        result = await run_pagespeed(str(request.url))

        normalized_result = normalize_pagespeed_result(
            str(request.url),
            result,
        )

        return {
            "message": "Audit completed",
            "data": normalized_result,
        }

    except PageSpeedConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "pagespeed_not_configured",
                "message": "Website analysis is not configured yet. Set PAGESPEED_API_KEY in the backend environment.",
            },
        ) from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail={
                "code": "pagespeed_timeout",
                "message": "Google PageSpeed took too long to analyze this website. Try again in a moment.",
            },
        ) from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (400, 403):
            status_code = 503
            code = "pagespeed_configuration_error"
            message = "Google PageSpeed rejected the request. Confirm the API key, API access, and quota are configured correctly."
        elif exc.response.status_code == 429:
            status_code = 503
            code = "pagespeed_rate_limited"
            message = "Google PageSpeed is temporarily rate limiting requests. Try again shortly."
        else:
            status_code = 502
            code = "pagespeed_provider_error"
            message = "Google PageSpeed could not complete this analysis. Check the URL and try again."
        raise HTTPException(
            status_code=status_code,
            detail={"code": code, "message": message},
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "pagespeed_unreachable",
                "message": "WebPulse could not reach Google PageSpeed. Check your connection and try again.",
            },
        ) from exc
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "invalid_pagespeed_response",
                "message": "Google PageSpeed returned an unexpected result. Please try again later.",
            },
        ) from exc
