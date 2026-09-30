from sentence_transformers import SentenceTransformer
import numpy as np
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    _model = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if EmbeddingService._model is None:
            try:
                logger.info(f'Loading embedding model: {settings.EMBEDDING_MODEL_NAME}')
                EmbeddingService._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                logger.info('Embedding model loaded')
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                raise
    
    def generate_embedding(self, text: str) -> list[float]:
        try:
            embedding = self._model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            embeddings = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False, batch_size=32)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
