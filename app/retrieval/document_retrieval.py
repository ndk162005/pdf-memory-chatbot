import logging
from app.core.config import settings
from app.database.database import db_manager
from app.retrieval.semantic_search import SemanticSearch
from app.retrieval.ranking import ResultRanker

logger = logging.getLogger(__name__)

class DocumentRetrieval:
    
    def __init__(self):
        self.search = SemanticSearch()
        self.ranker = ResultRanker()
    
    def retrieve(self, query: str, top_k: int = None, document_id: int = None) -> list[dict]:
        """Retrieve relevant document context for a query.
        
        Returns list of:
        {
            'document_id': int,
            'filename': str,
            'page_number': int,
            'paragraph_number': int,
            'text': str,
            'score': float
        }
        """
        # 1. Semantic search in ChromaDB
        search_results = self.search.search(
            query=query,
            top_k=settings.RETRIEVAL_TOP_K,
            document_id=document_id
        )
        
        if not search_results:
            logger.info('No search results found')
            return []
        
        # 2. Rank and filter
        ranked = self.ranker.rank(
            results=search_results,
            top_k=top_k or settings.FINAL_CONTEXT_TOP_K
        )
        
        # 3. Enrich with document metadata from SQLite
        enriched = []
        for result in ranked:
            doc_id = result.get('document_id')
            doc = db_manager.get_document(doc_id) if doc_id else None
            
            enriched.append({
                'document_id': result.get('document_id'),
                'filename': doc['filename'] if doc else result.get('filename', 'Unknown'),
                'page_number': result.get('page_number'),
                'paragraph_number': result.get('paragraph_number'),
                'text': result.get('text', ''),
                'score': result.get('score', 0.0)
            })
        
        logger.info(f'Retrieved {len(enriched)} context chunks for query')
        return enriched
