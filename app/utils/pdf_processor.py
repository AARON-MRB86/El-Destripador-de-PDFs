"""PDF text extraction utilities."""

from io import BytesIO
from pathlib import Path
from typing import Union

from app.exceptions import PdfExtractionError


class PdfTextExtractor:
    """Extracts text from PDF sources."""

    @classmethod
    def extract(cls, pdf_source: Union[BytesIO, str]) -> str:
        """
        Extract text from PDF source (bytes or file path).

        Args:
            pdf_source: BytesIO object or file path string

        Returns:
            Extracted text with normalized page separation

        Raises:
            PdfExtractionError: If extraction fails
        """
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise PdfExtractionError(
                "La dependencia de extraccion de PDF no esta instalada"
            ) from exc

        try:
            reader = PdfReader(pdf_source)
            page_texts = []
            for page in reader.pages:
                text = (page.extract_text() or "").strip()
                if text:
                    page_texts.append(text)
            return "\n\n".join(page_texts)
        except Exception as exc:
            raise PdfExtractionError(f"Error al extraer el texto: {str(exc)}") from exc
