"""
Document processor using markitdown.
Converts various file formats to markdown text.
"""

from markitdown import MarkItDown

from application.interfaces.processors.document_processor import IDocumentProcessor


class MarkItDownProcessor(IDocumentProcessor):
    """Document processor using markitdown."""

    def __init__(self):
        self.converter = MarkItDown()

    async def process_file(self, file_path: str) -> str:
        """Process file and extract text."""
        result = self.converter.convert(file_path)
        return result.text_content

    async def process_bytes(self, file_bytes: bytes, mime_type: str) -> str:
        """Process file bytes and extract text."""
        # MarkItDown doesn't support bytes directly, need to save to temp file
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=self._get_extension(mime_type)
        ) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            result = self.converter.convert(tmp_path)
            return result.text_content
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def get_supported_formats(self) -> list:
        """Get list of supported file formats."""
        return [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/html",
            "text/plain",
            "image/jpeg",
            "image/png",
        ]

    def _get_extension(self, mime_type: str) -> str:
        """Get file extension from MIME type."""
        mime_map = {
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
            "text/html": ".html",
            "text/plain": ".txt",
            "image/jpeg": ".jpg",
            "image/png": ".png",
        }
        return mime_map.get(mime_type, "")
