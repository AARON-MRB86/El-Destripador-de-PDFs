import hashlib
import importlib.util
import pathlib
from unittest.mock import MagicMock

import pytest


def _load_service_class():
    try:
        # Prefer normal import if package is available
        from App.services.documento_service import DocumentService

        return DocumentService
    except Exception:
        # Fallback: load module directly by path
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        module_path = repo_root / "App" / "services" / "documento_service.py"
        spec = importlib.util.spec_from_file_location("doc_service", str(module_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.DocumentService


def test_normalize_and_checksum_and_build_reference():
    DocumentService = _load_service_class()
    svc = DocumentService(db=MagicMock())

    with pytest.raises(ValueError):
        svc._normalize_original_filename(None)

    checksum = svc._calculate_checksum(b"abc")
    assert checksum == hashlib.sha256(b"abc").hexdigest()
    assert svc._build_memory_reference("deadbeef") == "memory://documents/deadbeef.pdf"


def test_validate_uploaded_pdf_basic():
    DocumentService = _load_service_class()
    svc = DocumentService(db=MagicMock())

    # wrong suffix
    with pytest.raises(ValueError):
        svc._validate_uploaded_pdf("file.txt", b"%PDF-" + b"data")

    # zero size
    with pytest.raises(ValueError):
        svc._validate_uploaded_pdf("file.pdf", b"")

    # invalid signature
    with pytest.raises(ValueError):
        svc._validate_uploaded_pdf("file.pdf", b"NOTPDF")
