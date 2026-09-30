import logging
from app.core.config import settings
from app.core.embeddings import EmbeddingService
from app.database.vector_store import get_vector_store

logger = logging.getLogger(__name__)

class SemanticSearch:
    
    def __init__(self):
        self.embedding_service = EmbeddingService.get_instance()
    
    def search(self, query: str, top_k: int = None, document_id: int = None) -> list[dict]:
        """Search for relevant document chunks.
        
        Returns list of:
        {
            'document_id': int,
            'filename': str,
            'page_number': int,
            'paragraph_number': int,
            'text': str,
            'distance': float,
            'score': float
        }
        """
        top_k = top_k or settings.RETRIEVAL_TOP_K
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # Search ChromaDB
        vector_store = get_vector_store()
        where_filter = {'document_id': document_id} if document_id else None
        
        results = vector_store.search_embeddings(
            query_embedding=query_embedding,
            top_k=top_k,
            where=where_filter
        )
        
        # Parse results
        search_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i] if results['distances'] else 0.0
                # Convert cosine distance to similarity score (0-1)
                score = max(0.0, 1.0 - distance)
                
                search_results.append({
                    'document_id': results['metadatas'][0][i].get('document_id'),
                    'filename': results['metadatas'][0][i].get('filename', 'Unknown'),
                    'page_number': results['metadatas'][0][i].get('page_number', 0),
                    'paragraph_number': results['metadatas'][0][i].get('paragraph_number', 0),
                    'text': results['documents'][0][i] if results['documents'] else '',
                    'distance': round(distance, 4),
                    'score': round(score, 4)
                })
        
        logger.info(f'Semantic search for "{query[:50]}..." returned {len(search_results)} results')
        return search_results
