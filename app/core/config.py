import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    # Ollama
    OLLAMA_BASE_URL: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'qwen3:8b')
    OLLAMA_TIMEOUT: int = int(os.getenv('OLLAMA_TIMEOUT', '120'))
    
    # Embeddings
    EMBEDDING_MODEL_NAME: str = os.getenv('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
    
    # Database
    DATABASE_DIR: Path = BASE_DIR / 'data' / 'database'
    DATABASE_PATH: str = str(DATABASE_DIR / 'documents.db')
    VECTOR_DB_PATH: str = str(BASE_DIR / 'data' / 'vector_db')
    
    # Upload
    UPLOAD_DIR: Path = BASE_DIR / 'uploads'
    
    # Retrieval
    RETRIEVAL_TOP_K: int = int(os.getenv('RETRIEVAL_TOP_K', '10'))
    FINAL_CONTEXT_TOP_K: int = int(os.getenv('FINAL_CONTEXT_TOP_K', '5'))
    
    # Chunking
    MAX_CHUNK_SIZE: int = int(os.getenv('MAX_CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP: int = int(os.getenv('CHUNK_OVERLAP', '100'))
    
    # Conversation
    MAX_CONVERSATION_MESSAGES: int = int(os.getenv('MAX_CONVERSATION_MESSAGES', '20'))
    
    # ChromaDB collection name
    CHROMA_COLLECTION_NAME: str = 'document_paragraphs'

    @classmethod
    def ensure_dirs(cls):
        cls.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        Path(cls.VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_dirs()
