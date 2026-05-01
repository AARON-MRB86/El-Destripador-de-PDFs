"""Rutas para gestión de documentos (endpoints REST).

Se implementan los endpoints principales para crear, listar,
actualizar, eliminar y extraer texto de documentos PDF.
Esta versión conserva la funcionalidad pero utiliza mensajes
y nombres internos distintos al proyecto de referencia.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from App.schemas import DocumentResponse, DocumentUpdate
from App.services import DocumentService
from App.utils.database import get_db

router = APIRouter(prefix="/documents", tags=["documents"])


def _get_doc_service(db: Any = Depends(get_db)) -> DocumentService:
    """Dependency: devuelve una instancia del servicio de documentos."""
    return DocumentService(db)


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
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
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
    doc = service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento {doc_id} no encontrado")
    return doc


@router.put("/{doc_id}", response_model=DocumentResponse)
async def modify_document(doc_id: int, payload: DocumentUpdate, service: DocumentService = Depends(_get_doc_service)) -> DocumentResponse:
    """Actualiza campos de un documento existente."""
    try:
        updated = service.update_document(doc_id, payload)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento {doc_id} no encontrado")
        return updated
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document(doc_id: int, service: DocumentService = Depends(_get_doc_service)):
    """Elimina un documento.

    Lanza 404 si el documento no existe.
    """
    ok = service.delete_document(doc_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento {doc_id} no encontrado")


@router.post("/{doc_id}/extract", response_model=DocumentResponse)
async def extract_text(doc_id: int, service: DocumentService = Depends(_get_doc_service)) -> DocumentResponse:
    """Extrae (o devuelve) el texto de un PDF. Maneja errores de validación."""
    try:
        doc = service.extract_text(doc_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento {doc_id} no encontrado")
        return doc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
