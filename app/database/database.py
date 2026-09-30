import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from app.core.config import settings
from app.database.models import DocumentModel, ParagraphModel

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = None
    
    def get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute('PRAGMA foreign_keys = ON')
        return self._connection
    
    def create_tables(self):
        conn = self.get_connection()
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                total_pages INTEGER NOT NULL,
                uploaded_at TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS paragraphs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                page_number INTEGER NOT NULL,
                paragraph_number INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_paragraphs_document_id ON paragraphs (document_id);
            CREATE INDEX IF NOT EXISTS idx_paragraphs_page_number ON paragraphs (page_number);
        ''')
        conn.commit()
        logger.info('Database tables created')
    
    def insert_document(self, filename: str, total_pages: int) -> int:
        conn = self.get_connection()
        cursor = conn.execute(
            'INSERT INTO documents (filename, total_pages, uploaded_at) VALUES (?, ?, ?)',
            (filename, total_pages, datetime.now().isoformat())
        )
        conn.commit()
        doc_id = cursor.lastrowid
        logger.info(f'Inserted document: {filename} (id={doc_id})')
        return doc_id
    
    def insert_paragraph(self, document_id: int, page_number: int, paragraph_number: int, text: str) -> int:
        conn = self.get_connection()
        cursor = conn.execute(
            'INSERT INTO paragraphs (document_id, page_number, paragraph_number, text) VALUES (?, ?, ?, ?)',
            (document_id, page_number, paragraph_number, text)
        )
        conn.commit()
        return cursor.lastrowid
    
    def insert_paragraphs(self, paragraphs: list[ParagraphModel]) -> list[int]:
        conn = self.get_connection()
        ids = []
        for p in paragraphs:
            cursor = conn.execute(
                'INSERT INTO paragraphs (document_id, page_number, paragraph_number, text) VALUES (?, ?, ?, ?)',
                (p.document_id, p.page_number, p.paragraph_number, p.text)
            )
            ids.append(cursor.lastrowid)
        conn.commit()
        logger.info(f'Inserted {len(ids)} paragraphs')
        return ids
    
    def get_document(self, document_id: int) -> dict | None:
        conn = self.get_connection()
        row = conn.execute('SELECT * FROM documents WHERE id = ?', (document_id,)).fetchone()
        if row:
            return dict(row)
        return None
    
    def get_paragraph(self, paragraph_id: int) -> dict | None:
        conn = self.get_connection()
        row = conn.execute('SELECT * FROM paragraphs WHERE id = ?', (paragraph_id,)).fetchone()
        if row:
            return dict(row)
        return None
    
    def get_document_paragraphs(self, document_id: int) -> list[dict]:
        conn = self.get_connection()
        rows = conn.execute(
            'SELECT * FROM paragraphs WHERE document_id = ? ORDER BY page_number, paragraph_number',
            (document_id,)
        ).fetchall()
        return [dict(row) for row in rows]
    
    def list_documents(self) -> list[dict]:
        conn = self.get_connection()
        rows = conn.execute('SELECT * FROM documents ORDER BY uploaded_at DESC').fetchall()
        return [dict(row) for row in rows]
    
    def delete_document(self, document_id: int) -> bool:
        conn = self.get_connection()
        # Paragraphs cascade delete due to FK
        cursor = conn.execute('DELETE FROM documents WHERE id = ?', (document_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f'Deleted document id={document_id}')
        return deleted
    
    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

# Global instance
db_manager = DatabaseManager()
