"""Text chunker implementation with multiple strategies."""

import re
from typing import List

from app.application.interfaces.processors import ITextChunker


class TextChunker(ITextChunker):
    """
    Text chunker with multiple strategies.

    Supports:
    - fixed: Fixed-size chunks with character overlap
    - sentence: Split by sentences, respecting chunk_size
    - paragraph: Split by paragraphs, respecting chunk_size
    - semantic: Smart splitting by headers/sections (for markdown)
    """

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        strategy: str = "fixed",
    ) -> List[str]:
        """
        Chunk text into smaller pieces.

        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            strategy: "fixed", "sentence", "paragraph", "semantic"

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        text = text.strip()

        # Choose strategy
        if strategy == "sentence":
            return self._chunk_by_sentence(text, chunk_size, chunk_overlap)
        elif strategy == "paragraph":
            return self._chunk_by_paragraph(text, chunk_size, chunk_overlap)
        elif strategy == "semantic":
            return self._chunk_semantic(text, chunk_size, chunk_overlap)
        else:  # default: fixed
            return self._chunk_fixed(text, chunk_size, chunk_overlap)

    def estimate_chunks(self, text: str, chunk_size: int) -> int:
        """Estimate number of chunks."""
        if not text:
            return 0
        return max(1, len(text) // chunk_size + (1 if len(text) % chunk_size else 0))

    # ==================== Chunking Strategies ====================

    def _chunk_fixed(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        """Fixed-size chunking with overlap."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at a natural boundary (space, newline)
            if end < len(text):
                # Look for last space/newline in the chunk
                last_break = max(
                    chunk.rfind(" "),
                    chunk.rfind("\n"),
                    chunk.rfind("."),
                )
                if last_break > chunk_size * 0.5:  # At least half the chunk
                    chunk = text[start : start + last_break + 1]
                    end = start + last_break + 1

            chunk = chunk.strip()
            if chunk:
                chunks.append(chunk)

            # Move start with overlap
            start = end - chunk_overlap
            if start >= len(text):
                break

        return chunks

    def _chunk_by_sentence(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        """Chunk by sentences, combining until chunk_size."""
        # Split into sentences
        sentences = self._split_sentences(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_len = len(sentence)

            if current_length + sentence_len > chunk_size and current_chunk:
                # Save current chunk
                chunks.append(" ".join(current_chunk))

                # Keep overlap sentences
                overlap_text = " ".join(current_chunk)
                overlap_start = max(0, len(overlap_text) - chunk_overlap)

                # Find sentences that fit in overlap
                current_chunk = []
                current_length = 0
                for s in reversed(current_chunk):
                    if current_length + len(s) <= chunk_overlap:
                        current_chunk.insert(0, s)
                        current_length += len(s) + 1
                    else:
                        break

            current_chunk.append(sentence)
            current_length += sentence_len + 1

        # Add remaining
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return [c.strip() for c in chunks if c.strip()]

    def _chunk_by_paragraph(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        """Chunk by paragraphs, combining until chunk_size."""
        # Split by double newlines or single newlines for markdown
        paragraphs = re.split(r"\n\s*\n|\n(?=[-*#])", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para_len = len(para)

            # If single paragraph is too large, split it
            if para_len > chunk_size:
                # Save current chunk first
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0

                # Split large paragraph by sentences
                sub_chunks = self._chunk_by_sentence(para, chunk_size, chunk_overlap)
                chunks.extend(sub_chunks)
                continue

            if current_length + para_len > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_length = 0

            current_chunk.append(para)
            current_length += para_len + 2  # +2 for \n\n

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return [c.strip() for c in chunks if c.strip()]

    def _chunk_semantic(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        """
        Semantic chunking for markdown/structured text.

        Splits by headers (##, ###, etc.) and maintains context.
        """
        # Find all headers
        header_pattern = r"^(#{1,6})\s+(.+)$"
        lines = text.split("\n")

        sections = []
        current_section = {"header": "", "content": [], "level": 0}

        for line in lines:
            header_match = re.match(header_pattern, line)

            if header_match:
                # Save previous section
                if current_section["content"] or current_section["header"]:
                    sections.append(current_section)

                level = len(header_match.group(1))
                current_section = {
                    "header": line,
                    "content": [],
                    "level": level,
                }
            else:
                current_section["content"].append(line)

        # Add last section
        if current_section["content"] or current_section["header"]:
            sections.append(current_section)

        # Build chunks from sections
        chunks = []
        current_chunk_parts = []
        current_length = 0
        parent_headers = []  # Track parent headers for context

        for section in sections:
            section_text = section["header"]
            if section["content"]:
                section_text += "\n" + "\n".join(section["content"])
            section_text = section_text.strip()

            if not section_text:
                continue

            section_len = len(section_text)

            # Update parent headers
            level = section["level"]
            if level > 0:
                # Remove headers at same or lower level
                parent_headers = [h for h in parent_headers if h["level"] < level]
                parent_headers.append({"header": section["header"], "level": level})

            # If section is too large, split it
            if section_len > chunk_size:
                if current_chunk_parts:
                    chunks.append("\n\n".join(current_chunk_parts))
                    current_chunk_parts = []
                    current_length = 0

                # Add context (parent headers) and split
                context = "\n".join([h["header"] for h in parent_headers[:-1]])
                content_to_split = (
                    context + "\n\n" + section_text if context else section_text
                )

                sub_chunks = self._chunk_by_paragraph(
                    content_to_split, chunk_size, chunk_overlap
                )
                chunks.extend(sub_chunks)
                continue

            if current_length + section_len > chunk_size and current_chunk_parts:
                chunks.append("\n\n".join(current_chunk_parts))
                current_chunk_parts = []
                current_length = 0

            current_chunk_parts.append(section_text)
            current_length += section_len + 2

        if current_chunk_parts:
            chunks.append("\n\n".join(current_chunk_parts))

        return [c.strip() for c in chunks if c.strip()]

    # ==================== Helpers ====================

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Vietnamese and English sentence endings
        # Handle common abbreviations
        text = re.sub(
            r"(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|e\.g|i\.e)\.\s", r"\1<DOT> ", text
        )

        # Split by sentence endings
        sentences = re.split(r"(?<=[.!?])\s+", text)

        # Restore dots
        sentences = [s.replace("<DOT>", ".") for s in sentences]

        return [s.strip() for s in sentences if s.strip()]
