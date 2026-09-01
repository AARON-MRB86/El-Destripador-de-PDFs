"""Controladores de excepciones para respuestas de API."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import (
    DuplicateDocumentError, DocumentException, DocumentNotFoundError, FileSizeExceededError, InvalidFilenameError, InvalidPdfError, PdfExtractionError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos los handlers de exepciones para la aplicacion"""

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(
        request: Request, exc: DocumentNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
    """Respuesta de error para documentos no encontrados"""

    @app.exception_handler(DuplicateDocumentError)
    async def duplicate_document_handler(
        request: Request, exc: DuplicateDocumentError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )
    """Respuesta de error para documentos duplicados"""

    @app.exception_handler(InvalidPdfError)
    async def invalid_pdf_handler(
        request: Request, exc: InvalidPdfError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
    """Respuesta de error para archivos PDF no válidos"""

    @app.exception_handler(InvalidFilenameError)
    async def invalid_filename_handler(
        request: Request, exc: InvalidFilenameError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
    """Respuesta de error para nombres de archivo no válidos"""

    @app.exception_handler(FileSizeExceededError)
    async def file_size_exceeded_handler(
        request: Request, exc: FileSizeExceededError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": str(exc)},
        )
    """Respuesta de error para archivos que exceden el tamaño permitido"""

    @app.exception_handler(PdfExtractionError)
    async def pdf_extraction_error_handler(
        request: Request, exc: PdfExtractionError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
    """Respuesta de error para fallos en la extracción de texto de PDF"""

    @app.exception_handler(DocumentException)
    async def document_exception_handler(
        request: Request, exc: DocumentException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
    """Respuesta de error para excepciones generales de documentos"""

    @app.exception_handler(ValueError)
    async def value_error_handler(
        request: Request, exc: ValueError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
    """Respuesta de error para errores de valor"""
