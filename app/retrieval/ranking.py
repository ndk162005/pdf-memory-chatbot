import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class ResultRanker:
    
    def rank(self, results: list[dict], top_k: int = None) -> list[dict]:
        """Re-rank and deduplicate search results.
        
        Args:
            results: list of search result dicts with 'score', 'text', etc.
            top_k: number of final results to return
            
        Returns:
            Ranked and deduplicated list of results
        """
        top_k = top_k or settings.FINAL_CONTEXT_TOP_K
        
        if not results:
            return []
        
        # Deduplicate by text similarity
        deduplicated = self._deduplicate(results)
        
        # Sort by score descending
        ranked = sorted(deduplicated, key=lambda x: x.get('score', 0), reverse=True)
        
        # Take top_k
        final = ranked[:top_k]
        
        logger.info(f'Ranked {len(results)} results -> {len(final)} final results')
        return final
    
    def _deduplicate(self, results: list[dict], similarity_threshold: float = 0.9) -> list[dict]:
        """Remove near-duplicate results based on text overlap."""
        if not results:
            return []
        
        unique = [results[0]]
        
        for result in results[1:]:
            is_duplicate = False
            for existing in unique:
                overlap = self._text_overlap(result.get('text', ''), existing.get('text', ''))
                if overlap > similarity_threshold:
                    # Keep the one with higher score
                    if result.get('score', 0) > existing.get('score', 0):
                        unique.remove(existing)
                        unique.append(result)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(result)
        
        return unique
    
    def _text_overlap(self, text1: str, text2: str) -> float:
        """Calculate text overlap ratio using word sets."""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
