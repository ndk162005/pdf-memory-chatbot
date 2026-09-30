import logging
import os
from pathlib import Path
from app.core.config import settings
from app.core.embeddings import EmbeddingService
from app.database.database import db_manager
from app.database.vector_store import get_vector_store
from app.database.models import ParagraphModel, UploadResponse
from app.processing.pdf_extractor import PDFExtractor
from app.processing.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class DocumentService:
    
    def __init__(self):
        self.extractor = PDFExtractor()
        self.processor = DocumentProcessor()
        self.embedding_service = EmbeddingService.get_instance()
    
    async def process_upload(self, file_path: str, filename: str) -> UploadResponse:
        """Process a PDF upload through the full ingestion pipeline."""
        try:
            # 1. Extract text from PDF
            logger.info(f'Extracting text from {filename}')
            pages = self.extractor.extract(file_path)
            total_pages = max(p['page_number'] for p in pages)
            
            # 2. Insert document into SQLite
            document_id = db_manager.insert_document(filename, total_pages)
            logger.info(f'Document {filename} inserted with id={document_id}')
            
            # 3. Process into chunks
            chunks = self.processor.process_pages(pages, document_id)
            
            if not chunks:
                raise ValueError('No meaningful text chunks extracted from PDF')
            
            # 4. Store paragraphs in SQLite
            paragraph_models = [
                ParagraphModel(
                    document_id=chunk['document_id'],
                    page_number=chunk['page_number'],
                    paragraph_number=chunk['paragraph_number'],
                    text=chunk['text']
                )
                for chunk in chunks
            ]
            paragraph_ids = db_manager.insert_paragraphs(paragraph_models)
            
            # 5. Generate embeddings
            logger.info(f'Generating embeddings for {len(chunks)} chunks')
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_service.generate_embeddings(texts)
            
            # 6. Store in ChromaDB
            vector_store = get_vector_store()
            chroma_ids = [f'doc{document_id}_para{pid}' for pid in paragraph_ids]
            metadatas = [
                {
                    'document_id': chunk['document_id'],
                    'filename': filename,
                    'page_number': chunk['page_number'],
                    'paragraph_number': chunk['paragraph_number']
                }
                for chunk in chunks
            ]
            
            vector_store.add_embeddings(
                ids=chroma_ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f'Document {filename} fully processed: {len(chunks)} chunks')
            
            return UploadResponse(
                status='success',
                document_id=document_id,
                filename=filename,
                pages=total_pages,
                paragraphs=len(chunks)
            )
            
        except Exception as e:
            logger.error(f'Error processing document {filename}: {e}')
            raise
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete a document and all associated data."""
        # Delete from ChromaDB
        vector_store = get_vector_store()
        vector_store.delete_document_vectors(document_id)
        
        # Delete from SQLite (cascades to paragraphs)
        deleted = db_manager.delete_document(document_id)
        
        if deleted:
            logger.info(f'Document {document_id} fully deleted')
        
        return deleted
