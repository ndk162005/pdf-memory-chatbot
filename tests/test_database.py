import pytest
from app.database.database import DatabaseManager

@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    manager = DatabaseManager(db_path)
    return manager

def test_create_tables(db):
    assert db.conn is not None

def test_insert_and_get_document(db):
    doc = db.insert_document("test.pdf", 5)
    assert doc.filename == "test.pdf"
    assert doc.page_count == 5
    
    retrieved = db.get_document(doc.id)
    assert retrieved.id == doc.id
    assert retrieved.filename == "test.pdf"

def test_insert_and_get_paragraphs(db):
    doc = db.insert_document("test.pdf", 5)
    paragraphs = [
        {"document_id": doc.id, "page_number": 1, "paragraph_number": 1, "text": "P1"},
        {"document_id": doc.id, "page_number": 1, "paragraph_number": 2, "text": "P2"}
    ]
    db.insert_paragraphs(paragraphs)
    
    retrieved = db.get_document_paragraphs(doc.id)
    assert len(retrieved) == 2
    assert retrieved[0].text == "P1"
    assert retrieved[1].text == "P2"

def test_list_documents(db):
    db.insert_document("doc1.pdf", 1)
    db.insert_document("doc2.pdf", 2)
    docs = db.list_documents()
    assert len(docs) == 2

def test_delete_document_cascades_paragraphs(db):
    doc = db.insert_document("test.pdf", 1)
    paragraphs = [{"document_id": doc.id, "page_number": 1, "paragraph_number": 1, "text": "P1"}]
    db.insert_paragraphs(paragraphs)
    
    db.delete_document(doc.id)
    assert db.get_document(doc.id) is None
    assert len(db.get_document_paragraphs(doc.id)) == 0

def test_get_nonexistent_document_returns_none(db):
    assert db.get_document("fake_id") is None

def test_get_document_paragraphs_ordered(db):
    doc = db.insert_document("test.pdf", 1)
    paragraphs = [
        {"document_id": doc.id, "page_number": 1, "paragraph_number": 2, "text": "P2"},
        {"document_id": doc.id, "page_number": 1, "paragraph_number": 1, "text": "P1"}
    ]
    db.insert_paragraphs(paragraphs)
    
    retrieved = db.get_document_paragraphs(doc.id)
    assert retrieved[0].paragraph_number == 1
    assert retrieved[1].paragraph_number == 2
