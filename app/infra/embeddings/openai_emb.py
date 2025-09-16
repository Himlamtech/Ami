import logging
import time

import rootutils
from openai import OpenAI

rootutils.setup_root(__file__, indicator=".env", pythonpath=True)

from app.core.config import Config

logger = logging.getLogger(__name__)


class OpenAIEmbeddings:
    def __init__(
        self,
        config: Config() = Config(),
        model: str = "text-embedding-3-small",
        dimension: int = 1536,
    ):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = model
        self.dimension = dimension

    def embed_documents(self, documents: list[str]):
        return self.client.embeddings.create(input=documents, model=self.model)

    def embed_text(self, query: str):
        return self.client.embeddings.create(input=query, model=self.model)

    def get_model(self):
        return self.model

    def get_dimension(self):
        return self.dimension

    def health_check(self):
        start_time = time.time()
        response = self.client.embeddings.create(
            input="Hello, world!", model=self.model
        )
        end_time = time.time()
        return f"Time taken: {end_time - start_time} seconds, response: {response}"


# emb = OpenAIEmbeddings()
# print(emb.health_check())
