"""PDF and document validation utilities."""

import hashlib
from pathlib import Path
from typing import Optional

from app.config import settings
from app.exceptions import (
    FileSizeExceededError,
    InvalidFilenameError,
    InvalidPdfError,
)


class PdfValidator:
    """Validates PDF files and bytes."""

    PDF_SIGNATURE = b"%PDF-"
    CHUNK_SIZE = 8192

    @classmethod
    def validate_filename(cls, filename: Optional[str]) -> str:
        """
        Validate and normalize filename.

        Args:
            filename: Original filename

        Returns:
            Normalized filename

        Raises:
            InvalidFilenameError: If filename is invalid
        """
        if not filename:
            raise InvalidFilenameError("Se requiere un archivo PDF")

        normalized = Path(filename).name.strip()
        if not normalized:
            raise InvalidFilenameError("Se requiere un archivo PDF")

        if Path(normalized).suffix.lower() != ".pdf":
            raise InvalidFilenameError("Solo se permiten archivos PDF")

        return normalized

    @classmethod
    def validate_bytes(cls, file_content: bytes) -> None:
        """
        Validate PDF bytes.

        Args:
            file_content: PDF file content

        Raises:
            InvalidPdfError: If bytes are invalid
            FileSizeExceededError: If file exceeds max size
        """
        if not file_content:
            raise InvalidPdfError("Archivo PDF invalido")

        if len(file_content) > settings.max_pdf_size_bytes:
            raise FileSizeExceededError(
                "El PDF supera el tamano maximo permitido de "
                f"{settings.max_pdf_size_bytes} bytes"
            )

        if file_content[: len(cls.PDF_SIGNATURE)] != cls.PDF_SIGNATURE:
            raise InvalidPdfError("Archivo PDF invalido")

    @classmethod
    def validate_file(cls, file_path: Path, expected_size: int) -> None:
        """
        Validate that file path points to a valid stored PDF.

        Args:
            file_path: Path to the file on disk
            expected_size: Expected size in bytes

        Raises:
            InvalidPdfError: If file validation fails
            FileSizeExceededError: If file exceeds max size
        """
        if not file_path.is_file():
            raise InvalidPdfError(f"Archivo no encontrado: {file_path}")

        if file_path.suffix.lower() != ".pdf":
            raise InvalidPdfError("Solo se permiten archivos PDF")

        actual_size = file_path.stat().st_size
        if actual_size != expected_size:
            raise InvalidPdfError(
                "El tamano del archivo no coincide: se esperaban "
                f"{expected_size} bytes y se encontraron {actual_size}"
            )

        if actual_size > settings.max_pdf_size_bytes:
            raise FileSizeExceededError(
                "El PDF supera el tamano maximo permitido de "
                f"{settings.max_pdf_size_bytes} bytes"
            )

        with file_path.open("rb") as pdf_file:
            if pdf_file.read(len(cls.PDF_SIGNATURE)) != cls.PDF_SIGNATURE:
                raise InvalidPdfError("Archivo PDF invalido")


class ChecksumCalculator:
    """Calculates SHA-256 checksums for files."""

    CHUNK_SIZE = 8192

    @classmethod
    def from_bytes(cls, file_content: bytes) -> str:
        """
        Calculate checksum from bytes.

        Args:
            file_content: File content

        Returns:
            SHA-256 checksum as hex string
        """
        digest = hashlib.sha256()
        digest.update(file_content)
        return digest.hexdigest()

    @classmethod
    def from_file(cls, file_path: Path) -> str:
        """
        Calculate checksum from file.

        Args:
            file_path: Path to file on disk

        Returns:
            SHA-256 checksum as hex string
        """
        digest = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(cls.CHUNK_SIZE), b""):
                digest.update(chunk)
        return digest.hexdigest()


class StringValidator:
    """Validates string inputs."""

    @classmethod
    def validate_required_string(cls, value: Optional[str], field_name: str) -> str:
        """
        Validate that string is not empty.

        Args:
            value: String value to validate
            field_name: Field name for error message

        Returns:
            Normalized string

        Raises:
            ValueError: If string is empty
        """
        if not value or not value.strip():
            raise ValueError(f"El {field_name} es obligatorio")
        return value.strip()
