"""Exportaciones del paquete API.

Este modulo expone el router de documentos para que pueda importarse
como `from App.api import document_router`.
"""
from app.api.Routes.document import router as document_router

__all__ = ["document_router"]
