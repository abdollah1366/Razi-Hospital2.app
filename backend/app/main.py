from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.routers import admin, announcements, auth, dashboard, incidents, public

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    settings = get_settings()
    settings.check_production()
    app = FastAPI(
        title="سامانه جامع بیمارستان رازی تبریز",
        version="0.1.0",
        docs_url=None if settings.env == "production" else "/docs",
        redoc_url=None,
    )
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["Authorization", "Content-Type"],
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError):
        fields = {".".join(str(p) for p in e["loc"][1:]) or "body": e["msg"] for e in exc.errors()}
        return JSONResponse(
            status_code=422,
            content={
                "detail": {"code": "validation_error", "message": "ورودی نامعتبر است", "fields": fields}
            },
        )

    for r in (
        auth.router,
        admin.router,
        incidents.router,
        announcements.router,
        public.router,
        dashboard.router,
    ):
        app.include_router(r, prefix=API_PREFIX)

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
