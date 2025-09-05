import rootutils

rootutils.setup_root(__file__, indicator=".env", pythonpath=True)

from datetime import datetime
from uuid import UUID

from langchain_openai import ChatOpenAI

from app.core.config import get_config
from app.infra.features.rag.prompt import RAG_PROMPT
from app.infra.storage.json_storage import JSONChatStorage
from app.infra.storage.vector_store import VectorStoreService
from app.schemas.chat import Message


# ---- RAG Service ----------------------------------------------------------
class RAGService:
    """Basic RAG on top of Chroma vector store."""

    def __init__(self):
        self.config = get_config()
        self.vector_store = VectorStoreService()
        self.storage = JSONChatStorage()

        model_name = self.config.DEFAULT_CHAT_MODEL_ID.value or "gpt-5-nano"
        self._llm = ChatOpenAI(model=model_name, temperature=0.5)

    def generate_response(self, question: str, session_id: str) -> str:
        # Tìm kiếm tài liệu liên quan
        relevant_docs = self.vector_store.similarity_search(question, k=3)

        # Sinh câu trả lời
        response = self._llm.invoke(
            RAG_PROMPT.invoke({"question": question, "context": relevant_docs})
        )

        # Lưu lịch sử chat
        messages = [
            Message(role="user", content=question, timestamp=datetime.now()),
            Message(
                role="assistant", content=response.content, timestamp=datetime.now()
            ),
        ]
        self.storage.append_messages(UUID(session_id), messages)

        return response.content


# rag_service = RAGService()
# start_time = time.time()
# response = rag_service.generate_response("Giám đốc học viện là ai?")
# print(response)
# end_time = time.time()
# print(f"Time taken: {end_time - start_time} seconds")
