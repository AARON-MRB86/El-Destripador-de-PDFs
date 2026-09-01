"""Pruebas unitarias para el servicio de documentos.
Verifican la orquestación de DocumentService: construcción de referencias en
memoria, propagación de errores de validación (delegados a App.utils) y el
manejo de documentos inexistentes."""

import pytest

from app.exceptions import DocumentNotFoundError, InvalidFilenameError, InvalidPdfError


def test_build_memory_reference(service):
    assert service._build_memory_reference("deadbeef") == "memory://documents/deadbeef.pdf"


def test_create_document_requires_name(service, tmp_pdf_bytes):
    with pytest.raises(ValueError):
        service.create_document("   ", "file.pdf", tmp_pdf_bytes)


def test_create_document_rejects_non_pdf_filename(service, tmp_pdf_bytes):
    with pytest.raises(InvalidFilenameError):
        service.create_document("Doc", "file.txt", tmp_pdf_bytes)


def test_create_document_rejects_invalid_signature(service):
    with pytest.raises(InvalidPdfError):
        service.create_document("Doc", "file.pdf", b"NOTPDF")


def test_get_document_raises_when_missing(service, repo):
    repo.collection.find_one.return_value = None
    with pytest.raises(DocumentNotFoundError):
        service.get_document(999)
