"""Exportaciones del paquete API.
Este modulo se encarga de expone los enrutadores para que puedan ser utilizados según necesidad.
Permite la importacion de 'from App.api import document_router'.
"""
from App.api.Routes.router import router as document_router

__all__ = ["document_router"]
