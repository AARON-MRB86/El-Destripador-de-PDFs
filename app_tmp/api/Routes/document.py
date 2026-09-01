"""Rutas para gestión de documentos (endpoints REST).

Implementa los endpoints principales para crear, listar, actualizar,
eliminar y extraer texto de documentos PDF. Los errores de negocio se
señalizan con excepciones de `App.exceptions`, manejadas globalmente
por `register_exception_handlers` (ver `App.main`).
"""

from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import PlainTextResponse
from pymongo.database import Database

from app.repositories import DocumentRepository
from app.schemas import DocumentResponse, DocumentUpdate
from app.services import DocumentService
from app.utils.database import get_db

router = APIRouter(prefix="/documents", tags=["documents"])


def _get_doc_service(db: Database = Depends(get_db)) -> DocumentService:
    """Dependency: devuelve una instancia del servicio de documentos."""
    return DocumentService(DocumentRepository(db))


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    name: str = Form(..., description="Título del documento"),
    file: UploadFile = File(..., description="Archivo PDF a procesar"),
    service: DocumentService = Depends(_get_doc_service),
) -> DocumentResponse:
    """Registra y procesa un PDF subido. Devuelve el documento creado.

    Se valida el PDF y se extrae el texto en memoria antes de persistir.
    """
    try:
        payload = await file.read()
        return service.create_document(name, file.filename, payload)
    finally:
        await file.close()


@router.get("", response_model=List[DocumentResponse])
async def list_all_documents(
    skip: int = 0, limit: int = 10, service: DocumentService = Depends(_get_doc_service)
) -> List[DocumentResponse]:
    """Devuelve una lista paginada de documentos."""
    return service.get_all_documents(skip, limit)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def read_document(doc_id: int, service: DocumentService = Depends(_get_doc_service)) -> DocumentResponse:
    """Obtiene los detalles de un documento por su identificador."""
    return service.get_document(doc_id)


@router.put("/{doc_id}", response_model=DocumentResponse)
async def modify_document(doc_id: int, payload: DocumentUpdate, service: DocumentService = Depends(_get_doc_service)) -> DocumentResponse:
    """Actualiza campos de un documento existente."""
    return service.update_document(doc_id, payload)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document(doc_id: int, service: DocumentService = Depends(_get_doc_service)) -> None:
    """Elimina un documento. Lanza 404 si el documento no existe."""
    service.delete_document(doc_id)


@router.get("/{doc_id}/download", response_class=PlainTextResponse)
async def download_document_text(doc_id: int, service: DocumentService = Depends(_get_doc_service)) -> PlainTextResponse:
    """Devuelve el texto extraído de un documento como archivo de texto."""
    document = service.get_document(doc_id)

    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="El documento no tiene texto extraído")

    return PlainTextResponse(
        document.extracted_text,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=pdf-extract-{doc_id}.txt"},
    )


@router.post("/{doc_id}/extract", response_model=DocumentResponse)
async def extract_text(doc_id: int, service: DocumentService = Depends(_get_doc_service)) -> DocumentResponse:
    """Extrae (o devuelve) el texto de un PDF."""
    return service.extract_text(doc_id)
