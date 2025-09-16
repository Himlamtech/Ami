import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY: str
    CHROMA_DB_PATH: str
    CHROMA_DB_COLLECTION_NAME: str | None
    ALLOWED_ORIGINS: list[str] | None
    SERVER_HOST: str
    SERVER_PORT: int
    DEBUG: bool

    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")
        self.CHROMA_DB_COLLECTION_NAME = os.getenv("CHROMA_DB_COLLECTION_NAME")
        self.ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
        self.SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"


# Create a global config instance
config = Config()
