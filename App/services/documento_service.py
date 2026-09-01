"""Document service - Business logic.

Orchestrates document CRUD and PDF processing. Validation, checksum
calculation and text extraction are delegated to `App.utils` so this
service has a single responsibility: coordinating the workflow.
"""

from io import BytesIO
from pathlib import Path
from typing import List, Optional

from App.exceptions import DocumentNotFoundError, DuplicateDocumentError, InvalidPdfError
from App.models import Document
from App.repositories import DocumentRepository
from App.schemas import DocumentResponse, DocumentUpdate
from App.utils.legacy_cleanup import remove_if_exists
from App.utils.pdf_processor import PdfTextExtractor
from App.utils.validators import ChecksumCalculator, PdfValidator, StringValidator


class DocumentService:
    """Service for document business logic."""

    def __init__(self, repository: DocumentRepository):
        """
        Initialize service with an injected repository.

        Args:
            repository: Repository used to persist and query documents.
        """
        self.repository = repository

    def create_document(
        self, name: str, original_filename: Optional[str], file_content: bytes
    ) -> DocumentResponse:
        """
        Create a new document from uploaded PDF bytes.

        Args:
            name: Human-readable document name
            original_filename: Original uploaded filename
            file_content: Uploaded PDF bytes

        Returns:
            Created document response
        """
        normalized_name = StringValidator.validate_required_string(
            name, "nombre del documento"
        )
        normalized_filename = PdfValidator.validate_filename(original_filename)
        PdfValidator.validate_bytes(file_content)
        checksum = ChecksumCalculator.from_bytes(file_content)

        if self.repository.get_by_checksum(checksum):
            raise DuplicateDocumentError("Ya existe un documento con el mismo checksum")

        extracted_text = PdfTextExtractor.extract(BytesIO(file_content))
        document = Document(
            name=normalized_name,
            original_filename=normalized_filename,
            file_path=self._build_memory_reference(checksum),
            checksum=checksum,
            file_size=len(file_content),
            extracted_text=extracted_text,
            is_processed=True,
        )

        created_document = self.repository.create(document)
        return DocumentResponse.model_validate(created_document)

    def get_document(self, document_id: int) -> DocumentResponse:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document response

        Raises:
            DocumentNotFoundError: If no document matches `document_id`
        """
        return DocumentResponse.model_validate(self._get_or_raise(document_id))

    def get_all_documents(
        self, skip: int = 0, limit: int = 10
    ) -> List[DocumentResponse]:
        """
        Get all documents.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of document responses
        """
        documents = self.repository.get_all(skip, limit)
        return [DocumentResponse.model_validate(doc) for doc in documents]

    def update_document(
        self, document_id: int, document_data: DocumentUpdate
    ) -> DocumentResponse:
        """
        Update document.

        Args:
            document_id: Document ID
            document_data: Update schema

        Returns:
            Updated document response

        Raises:
            DocumentNotFoundError: If no document matches `document_id`
        """
        self._get_or_raise(document_id)

        update_data = document_data.model_dump(exclude_unset=True)
        if "name" in update_data:
            update_data["name"] = StringValidator.validate_required_string(
                update_data["name"], "nombre del documento"
            )

        updated_document = self.repository.update(document_id, update_data)
        return DocumentResponse.model_validate(updated_document)

    def delete_document(self, document_id: int) -> None:
        """
        Delete document, removing any legacy on-disk file.

        Args:
            document_id: Document ID

        Raises:
            DocumentNotFoundError: If no document matches `document_id`
        """
        document = self._get_or_raise(document_id)
        self.repository.delete(document_id)
        remove_if_exists(document.file_path)

    def extract_text(self, document_id: int) -> DocumentResponse:
        """
        Extract text from PDF document.

        Documents processed in memory already have their text stored and
        are returned as-is. Legacy documents stored on disk are
        re-validated against their stored checksum before extraction.

        Args:
            document_id: Document ID

        Returns:
            Updated document response

        Raises:
            DocumentNotFoundError: If no document matches `document_id`
        """
        document = self._get_or_raise(document_id)

        if document.is_processed and document.extracted_text is not None:
            return DocumentResponse.model_validate(document)

        file_path = Path(document.file_path)
        PdfValidator.validate_file(file_path, document.file_size)

        current_checksum = ChecksumCalculator.from_file(file_path)
        if current_checksum != document.checksum:
            raise InvalidPdfError(
                "El archivo del documento ya no coincide con el checksum almacenado"
            )

        extracted_text = PdfTextExtractor.extract(str(file_path))
        updated_document = self.repository.update(
            document_id, {"extracted_text": extracted_text, "is_processed": True}
        )
        return DocumentResponse.model_validate(updated_document)

    def _get_or_raise(self, document_id: int) -> Document:
        """
        Fetch a document by ID or raise if it doesn't exist.

        Centralizes the "document not found" message construction.

        Args:
            document_id: Document ID

        Returns:
            The stored document

        Raises:
            DocumentNotFoundError: If no document matches `document_id`
        """
        document = self.repository.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Documento {document_id} no encontrado")
        return document

    def _build_memory_reference(self, checksum: str) -> str:
        """
        Build a logical reference for a document processed fully in memory.

        Args:
            checksum: SHA-256 checksum of the file

        Returns:
            Stable reference string stored for backward compatibility
        """
        return f"memory://documents/{checksum}.pdf"
