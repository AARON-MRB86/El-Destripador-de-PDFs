"""
Nucleo del proyecto, aquí deben encontrarse los modelos.
NO INCLUIR DEPPENDENCIAS EXTERNAS.
"""

from .documento import Documento
from .metadata import Metadata

__all__ = ['Documento', 'Metadata']