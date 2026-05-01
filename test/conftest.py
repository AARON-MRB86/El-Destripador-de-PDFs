import pytest
from unittest.mock import MagicMock

from App.repositories.documento_repository import DocumentRepository


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
def tmp_pdf_bytes():
    """Return a minimal byte string that looks like a PDF for validations."""
    return b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
