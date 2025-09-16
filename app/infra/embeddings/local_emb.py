# app/infra/embeddings/local_emb.py
import time
import torch
from sentence_transformers import SentenceTransformer
from typing import List

class LocalEmbeddings:
    def __init__(self, embeddings_model: str = "dangvantuan/vietnamese-document-embedding"):
        self.model = SentenceTransformer(
            embeddings_model,
            trust_remote_code=True,
            device="cuda" if torch.cuda.is_available() else "cpu",
        )

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        # Trả về list[list[float]]
        vecs = self.model.encode(documents, convert_to_numpy=True).tolist()
        return vecs

    def embed_text(self, query: str) -> List[float]:
        return self.model.encode([query], convert_to_numpy=True)[0].tolist()

    def get_dimension(self) -> int:
        # SentenceTransformer không luôn có get_dimension(); tự suy ra bằng 1 lần encode
        return len(self.embed_text("dim probe"))

    def health_check(self):
        start = time.time()
        _ = self.embed_text("Hello, world!")
        return f"Time taken: {time.time() - start:.3f}s"


# embeddings = LocalEmbeddings()
# print(embeddings.health_check())
