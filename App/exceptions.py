"""Custom application exceptions."""


class DocumentException(Exception):
    """Base exception for document operations."""

    pass


class DocumentNotFoundError(DocumentException):
    """Raised when a document is not found."""

    pass


class DuplicateDocumentError(DocumentException):
    """Raised when a document with same checksum already exists."""

    pass


class InvalidPdfError(DocumentException):
    """Raised when PDF validation fails."""

    pass


class InvalidFilenameError(DocumentException):
    """Raised when filename is invalid."""

    pass


class FileSizeExceededError(DocumentException):
    """Raised when file size exceeds maximum allowed."""

    pass


class PdfExtractionError(DocumentException):
    """Raised when PDF text extraction fails."""

    pass
