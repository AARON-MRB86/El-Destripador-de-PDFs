"""Document API endpoints."""

from typing import Any, List

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.schemas import DocumentResponse, DocumentUpdate
from app.services import DocumentService
from app.utils.database import get_db

router = APIRouter(prefix="/documents", tags=["documentos"])


def get_document_service(db: Any = Depends(get_db)) -> DocumentService:
    """Dependency to obtain document service."""
    return DocumentService(db)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear y procesar un nuevo documento",
)
async def create_document(
    name: str = Form(..., description="Nombre del documento"),
    file: UploadFile = File(..., description="Archivo PDF a registrar"),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Create a new document from uploaded PDF.
    The PDF is validated and processed in memory.

    Args:
        name: Document name
        file: PDF file uploaded by client
        service: Document service

    Returns:
        Created document
    """
    file_content = await file.read()
    try:
        return service.create_document(name, file.filename, file_content)
    finally:
        await file.close()


@router.get(
    "", response_model=List[DocumentResponse], summary="Listar todos los documentos"
)
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    service: DocumentService = Depends(get_document_service),
) -> List[DocumentResponse]:
    """
    List all documents with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        service: Document service

    Returns:
        List of documents
    """
    return service.get_all_documents(skip, limit)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Obtener un documento por ID",
)
async def get_document(
    document_id: int, service: DocumentService = Depends(get_document_service)
) -> DocumentResponse:
    """
    Get a document by ID.

    Args:
        document_id: Document ID
        service: Document service

    Returns:
        Document details
    """
    return service.get_document(document_id)


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Actualizar un documento",
)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Update a document.

    Args:
        document_id: Document ID
        document_data: Document data to update
        service: Document service

    Returns:
        Updated document
    """
    return service.update_document(document_id, document_data)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un documento",
)
async def delete_document(
    document_id: int, service: DocumentService = Depends(get_document_service)
) -> None:
    """
    Delete a document.

    Args:
        document_id: Document ID
        service: Document service
    """
    service.delete_document(document_id)


@router.post(
    "/{document_id}/extract",
    response_model=DocumentResponse,
    summary="Obtener o completar el texto extraido de un documento",
)
async def extract_text(
    document_id: int, service: DocumentService = Depends(get_document_service)
) -> DocumentResponse:
    """
    Extract text from a PDF document.
    If already processed in memory, returns stored result.

    Args:
        document_id: Document ID
        service: Document service

    Returns:
        Document with extracted text
    """
    return service.extract_text(document_id)

