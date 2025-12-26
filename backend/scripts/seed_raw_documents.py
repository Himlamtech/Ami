"""Seed static markdown documents from data/raw into MongoDB."""

from __future__ import annotations

import asyncio
import json
import re
import unicodedata
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Any, List, Tuple

from app.application.use_cases.sync.change_detector import ChangeDetectorUseCase
from app.domain.entities.document import Document
from app.infrastructure.persistence.mongodb.client import get_database
from app.infrastructure.persistence.mongodb.repositories.mongodb_document_repository import (
    MongoDBDocumentRepository,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_OUTPUT = ROOT_DIR / "data" / "data.json"
RAW_DIR = ROOT_DIR / "data" / "raw"
GENERATED_JSON = RAW_DIR / "generated_metadata.json"

CATEGORY_RULES: List[Tuple[List[str], Dict[str, str]]] = [
    (
        ["mau", "don", "form", "phieu"],
        {"category": "form", "source_label": "Biểu mẫu", "tags": ["forms"]},
    ),
    (
        ["clb", "club", "doi", "team"],
        {"category": "club", "source_label": "Câu lạc bộ", "tags": ["clubs"]},
    ),
    (
        ["nganh", "chuong trinh", "program", "logistics", "marketing"],
        {
            "category": "program",
            "source_label": "Chương trình đào tạo",
            "tags": ["programs"],
        },
    ),
    (
        ["phong", "ban"],
        {
            "category": "department",
            "source_label": "Phòng ban",
            "tags": ["departments"],
        },
    ),
    (
        ["trung tam"],
        {"category": "center", "source_label": "Trung tâm", "tags": ["centers"]},
    ),
    (
        ["vien"],
        {
            "category": "institute",
            "source_label": "Viện/Institute",
            "tags": ["institutes"],
        },
    ),
    (
        ["website", "portal", "cong thong tin"],
        {"category": "website", "source_label": "Website", "tags": ["web"]},
    ),
    (
        ["quy che", "quy dinh"],
        {"category": "policy", "source_label": "Quy chế", "tags": ["policies"]},
    ),
    (
        ["goc", "gửi xe", "chi duong"],
        {"category": "campus-life", "source_label": "Đời sống", "tags": ["campus"]},
    ),
]


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-")
    return ascii_text.lower()


def pretty_title(file_name: str) -> str:
    base = Path(file_name).stem
    base = base.replace("_", " ").replace("-", " ")
    base = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", base)
    base = base.replace("Ptit", "PTIT").replace("Cdit", "CDIT")
    base = re.sub(r"\s+", " ", base).strip()
    return base.title()


def infer_category(file_name: str) -> Dict[str, Any]:
    cleaned = slugify(file_name)
    for keywords, meta in CATEGORY_RULES:
        if any(keyword in cleaned for keyword in keywords):
            return meta
    return {"category": "general", "source_label": "PTIT Raw Seed", "tags": ["general"]}


def generate_metadata_entries() -> List[Dict[str, Any]]:
    entries = []
    for path in sorted(RAW_DIR.glob("*.md")):
        meta = infer_category(path.name)
        title = pretty_title(path.name)
        entry = {
            "title": title or path.stem,
            "file_name": path.name,
            "category": meta["category"],
            "source_label": meta["source_label"],
            "tags": meta["tags"] + ["raw_seed"],
            "collection": "ptit_raw",
        }
        entries.append(entry)
    return entries


def save_metadata_files(entries: List[Dict[str, Any]]) -> None:
    DATA_OUTPUT.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    GENERATED_JSON.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )


async def seed_raw_documents(collection: str = "ptit_raw") -> Dict[str, int]:
    """Generate metadata for markdown files and store in MongoDB."""
    entries = generate_metadata_entries()
    save_metadata_files(entries)

    db = await get_database()
    repository = MongoDBDocumentRepository(db)

    stats = {"created": 0, "skipped": 0, "missing_files": 0}

    for entry in entries:
        file_name = entry["file_name"]
        file_path = RAW_DIR / file_name
        if not file_path.exists():
            stats["missing_files"] += 1
            continue

        existing = await repository.search_by_metadata(
            metadata_filter={"raw_path": str(file_path)},
            collection=collection,
        )
        if existing:
            stats["skipped"] += 1
            continue

        content = file_path.read_text(encoding="utf-8")
        metadata: Dict[str, Any] = {
            "category": entry["category"],
            "source_label": entry["source_label"],
            "raw_path": str(file_path),
            "ingest_source": "data/raw_seed",
            "word_count": len(content.split()),
            "char_count": len(content),
            "summary": content[:400],
            "content_hash": ChangeDetectorUseCase.compute_content_hash(content),
            "seeded_at": datetime.now(UTC).isoformat(),
        }

        document = Document(
            id="",
            title=entry["title"],
            file_name=file_name,
            source=entry["source_label"],
            collection=entry.get("collection", collection),
            content=content,
            metadata=metadata,
            tags=entry["tags"],
            chunk_count=0,
            vector_ids=[],
            created_by="seed-script",
        )

        await repository.create(document)
        stats["created"] += 1

    return stats


if __name__ == "__main__":
    result = asyncio.run(seed_raw_documents())
    print(
        f"Seed completed: created={result['created']} "
        f"skipped={result['skipped']} missing_files={result['missing_files']}"
    )
