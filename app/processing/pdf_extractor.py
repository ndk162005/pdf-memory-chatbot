import fitz  # PyMuPDF
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFExtractor:
    
    @staticmethod
    def extract(file_path: str) -> list[dict]:
        """Extract text from PDF, page by page.
        Returns list of {'page_number': int, 'text': str}
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f'PDF file not found: {file_path}')
        if not path.suffix.lower() == '.pdf':
            raise ValueError(f'Not a PDF file: {file_path}')
        
        pages = []
        try:
            doc = fitz.open(file_path)
            if doc.page_count == 0:
                raise ValueError('PDF has no pages')
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text('text')
                if text and text.strip():
                    pages.append({
                        'page_number': page_num + 1,  # 1-indexed
                        'text': text.strip()
                    })
            
            doc.close()
            
            if not pages:
                raise ValueError('PDF contains no extractable text')
            
            logger.info(f'Extracted {len(pages)} pages from {path.name}')
            return pages
            
        except fitz.FileDataError as e:
            raise ValueError(f'Corrupt or invalid PDF: {e}')
    
    @staticmethod
    def get_page_count(file_path: str) -> int:
        doc = fitz.open(file_path)
        count = doc.page_count
        doc.close()
        return count
