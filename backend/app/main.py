from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.health import router as health_router

from app.api.routes.audit import router as audit_router
app = FastAPI(
    title="WebPulse API",
    description="Website performance and optimization analysis API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.frontend_url.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(audit_router)


@app.get("/")
async def root():
    return {
        "message": "WebPulse API is running"
    }
