from typing import Dict, List
from app.infra.llms.openai_llm import OpenAILLM
from app.infra.prompt.prompt import AMI_PROMPT
from app.infra.vectorstores.chroma_db import ChromaDB
from app.schemas.chat import ChatRequest, ChatResponse


class RAGService:
    def __init__(self):
        self.llm = OpenAILLM()
        self.vector_store = ChromaDB()
        # Lưu lịch sử session trong memory
        self.session_history: Dict[str, List[Dict[str, str]]] = {}
    
    def generate_response(self, query: str, session_id: str) -> ChatResponse:
        """Tạo response cho RAG chat với session management."""
        
        # Lấy context từ vector search
        search_results = self.vector_store.similarity_search(query, k=3)
        context = "\n".join([result["document"] for result in search_results])
        
        # Lấy lịch sử chat cho session
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        
        history = self.session_history[session_id]
        
        # Tạo messages cho LLM
        messages = AMI_PROMPT.copy()
        
        
        # Thêm lịch sử chat (giới hạn 5 cặp hỏi-đáp gần nhất)
        recent_history = history[-10:] if len(history) > 10 else history
        for chat in recent_history:
            messages.append({"role": "user", "content": chat["user"]})
            messages.append({"role": "assistant", "content": chat["assistant"]})
        
        # Thêm context vào system message
        context_message = {
            "role": "system", 
            "content": f"Context thông tin liên quan:\n{context}\n\nHãy sử dụng thông tin này để trả lời câu hỏi của user."
        }
        messages.append(context_message)
        
        # Thêm câu hỏi hiện tại
        messages.append({"role": "user", "content": query})
        
        # Gọi LLM
        answer = self.llm.generate(messages)
        
        # Lưu vào lịch sử
        history.append({"user": query, "assistant": answer})
        
        # Tạo response với lịch sử dạng list[dict[str, str]]
        history_format = []
        for chat in history:
            history_format.extend([
                {"role": "user", "content": chat["user"]},
                {"role": "assistant", "content": chat["assistant"]}
            ])
        
        return ChatResponse(
            answer=answer,
            session_id=session_id,
            history=history_format
        )