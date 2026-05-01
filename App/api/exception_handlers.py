"""Exception handlers for API responses."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import (
    DuplicateDocumentError,
    DocumentException,
    DocumentNotFoundError,
    FileSizeExceededError,
    InvalidFilenameError,
    InvalidPdfError,
    PdfExtractionError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers for the application."""

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(
        request: Request, exc: DocumentNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DuplicateDocumentError)
    async def duplicate_document_handler(
        request: Request, exc: DuplicateDocumentError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidPdfError)
    async def invalid_pdf_handler(
        request: Request, exc: InvalidPdfError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidFilenameError)
    async def invalid_filename_handler(
        request: Request, exc: InvalidFilenameError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(FileSizeExceededError)
    async def file_size_exceeded_handler(
        request: Request, exc: FileSizeExceededError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": str(exc)},
        )

    @app.exception_handler(PdfExtractionError)
    async def pdf_extraction_error_handler(
        request: Request, exc: PdfExtractionError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DocumentException)
    async def document_exception_handler(
        request: Request, exc: DocumentException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(
        request: Request, exc: ValueError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
