"""Document service - Business logic."""

from io import BytesIO
from pathlib import Path
from typing import Any, List, Optional

from app.exceptions import (
    DocumentNotFoundError,
    DuplicateDocumentError,
    InvalidPdfError,
)
from app.models import Document
from app.repositories import DocumentRepository
from app.schemas import DocumentResponse, DocumentUpdate
from app.utils.pdf_processor import PdfTextExtractor
from app.utils.validators import (
    ChecksumCalculator,
    PdfValidator,
    StringValidator,
)


class DocumentService:
    """Service for document business logic."""

    def __init__(self, db: Any):
        """
        Initialize service with database session.

        Args:
            db: Database handle
        """
        self.repository = DocumentRepository(db)

    def create_document(
        self, name: str, original_filename: str | None, file_content: bytes
    ) -> DocumentResponse:
        """
        Create a new document from uploaded PDF bytes.

        Args:
            name: Human-readable document name
            original_filename: Original uploaded filename
            file_content: Uploaded PDF bytes

        Returns:
            Created document response

        Raises:
            ValueError: If validation fails
            DuplicateDocumentError: If document with same checksum exists
        """
        normalized_name = StringValidator.validate_required_string(name, "nombre")
        normalized_filename = PdfValidator.validate_filename(original_filename)
        PdfValidator.validate_bytes(file_content)

        checksum = ChecksumCalculator.from_bytes(file_content)
        if self.repository.get_by_checksum(checksum):
            raise DuplicateDocumentError(
                "Ya existe un documento con el mismo checksum"
            )

        extracted_text = PdfTextExtractor.extract(BytesIO(file_content))
        document = Document(
            name=normalized_name,
            original_filename=normalized_filename,
            file_path=f"memory://documents/{checksum}.pdf",
            checksum=checksum,
            file_size=len(file_content),
            extracted_text=extracted_text,
            is_processed=True,
        )

        created_document = self.repository.create(document)
        return self._to_response(created_document)

    def get_document(self, document_id: int) -> DocumentResponse:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document response

        Raises:
            DocumentNotFoundError: If document not found
        """
        document = self.repository.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Documento {document_id} no encontrado")
        return self._to_response(document)

    def get_all_documents(
        self, skip: int = 0, limit: int = 10
    ) -> List[DocumentResponse]:
        """
        Get all documents with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of document responses
        """
        documents = self.repository.get_all(skip, limit)
        return [self._to_response(doc) for doc in documents]

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
            DocumentNotFoundError: If document not found
            ValueError: If validation fails
        """
        update_data = document_data.model_dump(exclude_unset=True)
        if "name" in update_data:
            update_data["name"] = StringValidator.validate_required_string(
                update_data["name"], "nombre"
            )

        document = self.repository.update(document_id, update_data)
        if not document:
            raise DocumentNotFoundError(f"Documento {document_id} no encontrado")

        return self._to_response(document)

    def delete_document(self, document_id: int) -> bool:
        """
        Delete document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted

        Raises:
            DocumentNotFoundError: If document not found
        """
        document = self.repository.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Documento {document_id} no encontrado")

        return self.repository.delete(document_id)

    def extract_text(self, document_id: int) -> DocumentResponse:
        """
        Extract text from PDF document.

        Args:
            document_id: Document ID

        Returns:
            Updated document response

        Raises:
            DocumentNotFoundError: If document not found
            PdfExtractionError: If extraction fails
        """
        document = self.repository.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Documento {document_id} no encontrado")

        if document.is_processed and document.extracted_text is not None:
            return self._to_response(document)

        file_path = Path(document.file_path)
        PdfValidator.validate_file(file_path, document.file_size)

        current_checksum = ChecksumCalculator.from_file(file_path)
        if current_checksum != document.checksum:
            raise InvalidPdfError(
                "El archivo del documento ya no coincide con el checksum almacenado"
            )

        extracted_text = PdfTextExtractor.extract(str(file_path))
        update_data = {"extracted_text": extracted_text, "is_processed": True}
        updated_doc = self.repository.update(document_id, update_data)

        return self._to_response(updated_doc)


    def _to_response(self, document: Document) -> DocumentResponse:
        """Convert Document model to DocumentResponse."""
        return DocumentResponse.model_validate(document)