import chromadb
import logging
from app.core.config import settings
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = None):
        persist_dir = persist_directory or settings.VECTOR_DB_PATH
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={'hnsw:space': 'cosine'}
        )
        logger.info(f'ChromaDB initialized at {persist_dir}')
    
    def add_embeddings(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict]
    ):
        if not ids:
            return
        # ChromaDB has batch limits, process in chunks of 5000
        batch_size = 5000
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            self._collection.add(
                ids=ids[i:end],
                embeddings=embeddings[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end]
            )
        logger.info(f'Added {len(ids)} embeddings to ChromaDB')
    
    def search_embeddings(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        where: dict = None
    ) -> dict:
        kwargs = {
            'query_embeddings': [query_embedding],
            'n_results': min(top_k, self._collection.count()) if self._collection.count() > 0 else top_k,
            'include': ['documents', 'metadatas', 'distances']
        }
        if where:
            kwargs['where'] = where
        
        if self._collection.count() == 0:
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
        
        results = self._collection.query(**kwargs)
        return results
    
    def delete_document_vectors(self, document_id: int):
        try:
            self._collection.delete(where={'document_id': document_id})
            logger.info(f'Deleted vectors for document_id={document_id}')
        except Exception as e:
            logger.warning(f'Error deleting vectors for document {document_id}: {e}')
    
    def count_vectors(self) -> int:
        return self._collection.count()
    
    def reset(self):
        self._client.delete_collection(settings.CHROMA_COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={'hnsw:space': 'cosine'}
        )
        logger.info('Vector store reset')

_vector_store_instance = None

def get_vector_store() -> VectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
