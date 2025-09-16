# app/infra/vectorstores/chroma_db.py
from dataclasses import dataclass
import time
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import EmbeddingFunction

import rootutils
rootutils.setup_root(__file__, indicator=".env", pythonpath=True)

from app.infra.embeddings.local_emb import LocalEmbeddings
# from app.infra.embeddings.openai_emb import OpenAIEmbeddings  # nếu cần

# --- Wrapper để Chroma gọi trực tiếp hàm embed của bạn ---
class LocalEmbeddingFunction(EmbeddingFunction):
    def __init__(self, embedder: LocalEmbeddings):
        self.embedder = embedder
    def __call__(self, texts: List[str]) -> List[List[float]]:
        return self.embedder.embed_documents(texts)

@dataclass
class ChromaDBConfig:
    path: str = "./vectorstore"
    collection_name: str = "ami"
    distance: str = "cosine"  # 'cosine' | 'l2' | 'ip'

class ChromaDB:
    def __init__(
        self,
        config: ChromaDBConfig = ChromaDBConfig(),
        embeddings: Optional[LocalEmbeddings] = None,
    ):
        self.config = config
        self.embedder = embeddings or LocalEmbeddings()

        # Dùng PersistentClient (hoặc Client + Settings)
        self.client = chromadb.PersistentClient(path=self.config.path)

        # Thiết lập metric qua metadata và gắn embedding_function
        self.collection = self.client.get_or_create_collection(
            name=self.config.collection_name,
            metadata={"hnsw:space": self.config.distance},
            embedding_function=LocalEmbeddingFunction(self.embedder),
        )

    def add_documents(self, documents: List[str], ids: Optional[List[str]] = None, metadatas: Optional[List[Dict[str, Any]]] = None):
        if ids is None:
            ids = [str(i) for i in range(len(documents))]
        self.collection.add(documents=documents, ids=ids, metadatas=metadatas)


    def upsert_documents(self, documents: List[str], ids: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        self.collection.upsert(documents=documents, ids=ids, metadatas=metadatas)


    def delete_documents(self, ids: List[str]):
        self.collection.delete(ids=ids)

    def delete_all(self):
        self.collection.delete_all()


    def similarity_search(self, query: str, k: int = 3):
        # query_texts + n_results; có thể include distances nếu muốn
        res = self.collection.query(query_texts=[query], n_results=k, include=["distances", "documents", "metadatas"])
        docs = res.get("documents", [[]])[0]
        ids = res.get("ids", [[]])[0]
        dists = res.get("distances", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return [{"id": i, "document": d, "distance": dist, "metadata": m} for i, d, dist, m in zip(ids, docs, dists, metas)]

# --------- demo ----------
if __name__ == "__main__":
    # import pandas as pd
    # df = pd.read_csv("assets/data/processed/qa.csv")
    # texts = df["Context"].astype(str).tolist()

    chroma_db = ChromaDB()
    # chroma_db.add_documents(texts)
    start = time.time()
    results = chroma_db.similarity_search("PTIT có nghĩa là gì?", k=3)
    print(results)
    end = time.time()
    # print(f"Time taken: {end - start} seconds")
    # for r in results:
    #     print(r["id"], r["distance"], r["document"], "...")
    print(f"Time taken: {end - start} seconds")
