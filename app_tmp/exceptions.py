"""Excepciones de aplicacion personalizadas."""


class DocumentException(Exception):
    """Exception base para operaciones con documentos."""

    pass


class DocumentNotFoundError(DocumentException):
    """Generado cuando no se encuentra un documento."""

    pass


class DuplicateDocumentError(DocumentException):
    """Generado cuando ya existe un documento con el mismo checksum."""

    pass


class InvalidPdfError(DocumentException):
    """Generado cuando la validación de PDF falla."""

    pass


class InvalidFilenameError(DocumentException):
    """Generado cuando el nombre de archivo es inválido."""

    pass


class FileSizeExceededError(DocumentException):
    """Generado cuando el tamaño del archivo excede el máximo permitido."""

    pass


class PdfExtractionError(DocumentException):
    """Generado cuando falla la extracción de texto de un PDF."""

    pass
