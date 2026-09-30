import re
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    
    def __init__(self, max_chunk_size: int = None, chunk_overlap: int = None):
        self.max_chunk_size = max_chunk_size or settings.MAX_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    def process_pages(self, pages: list[dict], document_id: int) -> list[dict]:
        """Process extracted pages into paragraph chunks.
        
        Args:
            pages: list of {'page_number': int, 'text': str}
            document_id: the document ID from SQLite
            
        Returns:
            list of {'document_id': int, 'page_number': int, 'paragraph_number': int, 'text': str}
        """
        all_chunks = []
        global_paragraph_number = 0
        
        for page in pages:
            page_number = page['page_number']
            text = page['text']
            
            # Split into natural paragraphs
            paragraphs = self._split_into_paragraphs(text)
            
            for para in paragraphs:
                # Clean the paragraph
                cleaned = self._clean_text(para)
                if not cleaned or len(cleaned.strip()) < 20:
                    continue  # Skip very short/empty chunks
                
                # Split large paragraphs
                if len(cleaned) > self.max_chunk_size:
                    sub_chunks = self._split_large_paragraph(cleaned)
                    for chunk in sub_chunks:
                        global_paragraph_number += 1
                        all_chunks.append({
                            'document_id': document_id,
                            'page_number': page_number,
                            'paragraph_number': global_paragraph_number,
                            'text': chunk
                        })
                else:
                    global_paragraph_number += 1
                    all_chunks.append({
                        'document_id': document_id,
                        'page_number': page_number,
                        'paragraph_number': global_paragraph_number,
                        'text': cleaned
                    })
        
        logger.info(f'Processed {len(all_chunks)} chunks for document {document_id}')
        return all_chunks
    
    def _split_into_paragraphs(self, text: str) -> list[str]:
        # Split on double newlines (natural paragraph boundaries)
        paragraphs = re.split(r'\n\s*\n', text)
        # If no double newlines, try single newlines with enough separation
        if len(paragraphs) <= 1:
            paragraphs = re.split(r'\n(?=[A-Z])', text)
        # Filter empty
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _clean_text(self, text: str) -> str:
        # Remove excessive whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        # Remove excessive newlines  
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Strip
        text = text.strip()
        return text
    
    def _split_large_paragraph(self, text: str) -> list[str]:
        """Split oversized paragraph into smaller chunks with overlap."""
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            if current_length + sentence_len > self.max_chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                # Keep overlap
                overlap_chunks = []
                overlap_length = 0
                for s in reversed(current_chunk):
                    if overlap_length + len(s) <= self.chunk_overlap:
                        overlap_chunks.insert(0, s)
                        overlap_length += len(s)
                    else:
                        break
                
                current_chunk = overlap_chunks
                current_length = overlap_length
            
            current_chunk.append(sentence)
            current_length += sentence_len
        
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
        
        # If sentence splitting didn't work (no sentence boundaries), do character split
        if not chunks:
            for i in range(0, len(text), self.max_chunk_size - self.chunk_overlap):
                chunk = text[i:i + self.max_chunk_size]
                if chunk.strip():
                    chunks.append(chunk.strip())
        
        return chunks
