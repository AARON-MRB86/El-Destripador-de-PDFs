"""API package exports.

This module exposes the main routers for the application so callers
can import `from App.api import document_router`.
"""
from App.api.Routes.router import router as document_router

__all__ = ["document_router"]
