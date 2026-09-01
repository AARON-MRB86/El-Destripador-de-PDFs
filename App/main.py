"""Application entrypoint: assembles the FastAPI app and its routes."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from App.api.Controllers.health import ping as check_health
from App.api.Routes.document import router as documents_router
from App.api.exception_handlers import register_exception_handlers
from App.config.settings import settings
from App.utils.database import ensure_indexes


def create_app() -> FastAPI:
    """Factory para crear la aplicación con la configuración y rutas del proyecto."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url=settings.api_docs_url,
        redoc_url=settings.api_redoc_url,
        openapi_url=settings.api_openapi_url,
    )

    register_exception_handlers(app)

    if settings.cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(documents_router, prefix=settings.api_v1_prefix)
    app.mount("/static", StaticFiles(directory="App/static"), name="static")

    @app.on_event("startup")
    async def startup_event() -> None:
        ensure_indexes()

    @app.get("/")
    async def home() -> FileResponse:
        return FileResponse("App/static/index.html")

    @app.get("/health")
    def health() -> dict:
        """Health check for orchestrators (Docker/Kubernetes/balanceadores)."""
        return check_health()

    return app


app = create_app()
