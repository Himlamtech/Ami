"""Processor interfaces."""

from .document_processor import IDocumentProcessor
from .text_chunker import ITextChunker
from .web_crawler import IWebCrawler

__all__ = [
    "IDocumentProcessor",
    "ITextChunker",
    "IWebCrawler",
]
