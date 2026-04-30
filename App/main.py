
"""FastAPI application factory and lifespan helpers.

This module provides a robust app factory suitable for the project structure.
It uses the database helpers in `app.utils.database` to initialize indexes,
perform healthchecks and close the client on shutdown.
"""
from contextlib import asynccontextmanager
import logging
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from App.api import document_router
from App.config import settings
from App.utils.database import ensure_indexes, get_db, ping_database, close_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""Startup/shutdown lifecycle for the FastAPI app.

	- Ensures indexes/collections are created on startup.
	- Logs startup/shutdown events.
	- Closes DB client on shutdown.
	"""
	try:
		ensure_indexes()
		logger.info("%s: índices y colecciones inicializadas", settings.app_name)
		print(f"[OK] {settings.app_name} started successfully")
	except Exception:
		logger.exception("Fallo inicializando la base de datos en el arranque")
		raise

	yield

	# Shutdown: try to close DB client gracefully
	try:
		close_client()
		logger.info("%s: cliente de BD cerrado", settings.app_name)
		print(f"[OK] {settings.app_name} shutdown")
	except Exception:
		logger.exception("Error cerrando el cliente de la base de datos")


def create_app() -> FastAPI:
	"""Create and configure the FastAPI application.

	Returns:
		Configured FastAPI `app`.
	"""
	app = FastAPI(
		title=settings.app_name,
		description="API para registrar, validar y extraer texto de documentos PDF.",
		version=settings.app_version,
		debug=settings.debug,
		docs_url=settings.api_docs_url,
		redoc_url=settings.api_redoc_url,
		openapi_url=settings.api_openapi_url,
		lifespan=lifespan,
	)

	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.cors_allow_origins or ["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	app.include_router(document_router, prefix=settings.api_v1_prefix)


	@app.get("/", tags=["inicio"], summary="Ver informacion basica de la API")
	async def root():
		"""Mostrar informacion general de la API."""
		return {
			"message": f"Bienvenido a {settings.app_name}",
			"version": settings.app_version,
			"docs": settings.api_docs_url,
			"database": "mongodb",
			"database_name": settings.database_name,
		}


	@app.get("/health", tags=["inicio"], summary="Verificar estado de la API")
	async def health(db: Any = Depends(get_db)):
		"""Verificar que la API y MongoDB esten disponibles.

		Performs a lightweight `ping` against MongoDB and returns 503 if it fails.
		"""
		ok = ping_database()
		if not ok:
			raise HTTPException(
				status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
				detail="Base de datos no disponible",
			)

		return {
			"status": "ok",
			"database": "mongodb",
			"database_name": settings.database_name,
		}

	return app


app = create_app()

