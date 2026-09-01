"""Fixtures para pruebas unitarias de repositorios y validaciones.
Estos fixtures proporcionan objetos simulados y datos de prueba para facilitar la escritura de pruebas unitarias"""

import pytest
from unittest.mock import MagicMock

from app.repositories.documento_repository import DocumentRepository
from app.services.documento_service import DocumentService


class FakeDB:
    """Lightweight fake DB object exposing collections by name."""

    def __init__(self):
        self._cols = {
            "documents": MagicMock(),
            "counters": MagicMock(),
        }

    def __getitem__(self, name):
        return self._cols[name]


@pytest.fixture
def fake_db():
    """Provide a fresh fake database for repository tests."""
    return FakeDB()


@pytest.fixture
def repo(fake_db):
    """Provide a `DocumentRepository` instantiated with the fake DB."""
    return DocumentRepository(fake_db)


@pytest.fixture
def service(repo):
    """Provide a `DocumentService` instantiated with a repository backed by the fake DB."""
    return DocumentService(repo)


@pytest.fixture
def tmp_pdf_bytes():
    """Return a minimal byte string that looks like a PDF for validations."""
    return b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
