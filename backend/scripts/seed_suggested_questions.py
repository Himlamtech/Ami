"""Seed suggested questions and embeddings."""

import asyncio
from datetime import datetime

from app.infrastructure.persistence.mongodb.client import MongoDBClient
from app.infrastructure.persistence.mongodb.repositories.mongodb_suggested_question_repository import (
    MongoDBSuggestedQuestionRepository,
)
from app.infrastructure.ai.embeddings import HuggingFaceEmbeddings
from app.infrastructure.persistence.qdrant import QdrantVectorStore
from app.application.use_cases.suggestions import QUESTION_COLLECTION
from app.domain.entities.suggested_question import SuggestedQuestion


QUESTIONS = [
    {
        "text": "Học phí PTIT năm nay là bao nhiêu?",
        "category": "finance",
        "tags": ["hoc_phi", "tai_chinh"],
    },
    {
        "text": "Địa chỉ của trường ở đâu?",
        "category": "campus",
        "tags": ["dia_diem", "co_so"],
    },
    {
        "text": "Khi nào mở miễn học miễn thi tiếng Anh?",
        "category": "english",
        "tags": ["tieng_anh", "mien_hoc_mien_thi"],
    },
    {
        "text": "Lab Samsung nằm ở đâu?",
        "category": "campus",
        "tags": ["lab", "samsung"],
    },
    {
        "text": "Thủ tục đăng ký học phần như thế nào?",
        "category": "registration",
        "tags": ["dang_ky", "hoc_phan"],
    },
    {
        "text": "Lịch thi học kỳ khi nào?",
        "category": "exam",
        "tags": ["lich_thi", "hoc_ky"],
    },
    {
        "text": "Cách xin mẫu đơn nghỉ học?",
        "category": "procedure",
        "tags": ["mau_don", "nghi_hoc"],
    },
    {
        "text": "Điều kiện xét học bổng là gì?",
        "category": "scholarship",
        "tags": ["hoc_bong"],
    },
]


async def main():
    mongo = MongoDBClient()
    await mongo.connect()
    repo = MongoDBSuggestedQuestionRepository(mongo.db)

    embedder = HuggingFaceEmbeddings()
    vector_store = QdrantVectorStore(default_collection=QUESTION_COLLECTION)

    texts = []
    payloads = []

    for item in QUESTIONS:
        existing = await repo.find_by_text(item["text"])
        if existing:
            question = existing
        else:
            question = SuggestedQuestion(
                id="",
                text=item["text"],
                category=item["category"],
                tags=item["tags"],
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            question = await repo.create(question)

        texts.append(question.text)
        payloads.append(
            {
                "question_id": question.id,
                "text": question.text,
                "category": question.category,
                "tags": question.tags,
            }
        )

    embeddings = await embedder.embed_batch(texts)
    await vector_store.add_documents(
        documents=[
            {"content": text, "metadata": payload}
            for text, payload in zip(texts, payloads)
        ],
        embeddings=embeddings,
        collection_name=QUESTION_COLLECTION,
    )

    await mongo.disconnect()
    print(f"Seeded {len(QUESTIONS)} suggested questions.")


if __name__ == "__main__":
    asyncio.run(main())
