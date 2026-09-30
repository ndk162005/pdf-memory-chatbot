import pytest
from app.database.vector_store import VectorStore

@pytest.fixture
def vector_store(tmp_path):
    store_dir = str(tmp_path / "chroma")
    return VectorStore(store_dir)

def test_add_and_search_embeddings(vector_store):
    embeddings = [[0.1, 0.2], [0.8, 0.9]]
    metadata = [{"document_id": "doc1", "paragraph_id": "p1", "text": "A"}, 
                {"document_id": "doc1", "paragraph_id": "p2", "text": "B"}]
    ids = ["id1", "id2"]
    
    vector_store.add_embeddings(embeddings, metadata, ids)
    
    results = vector_store.search([0.1, 0.2], top_k=1)
    assert len(results["ids"][0]) == 1
    assert results["ids"][0][0] == "id1"

def test_delete_document_vectors(vector_store):
    embeddings = [[0.1, 0.2]]
    metadata = [{"document_id": "doc1", "paragraph_id": "p1", "text": "A"}]
    ids = ["id1"]
    
    vector_store.add_embeddings(embeddings, metadata, ids)
    assert vector_store.count() == 1
    
    vector_store.delete_document("doc1")
    assert vector_store.count() == 0

def test_count_vectors(vector_store):
    embeddings = [[0.1], [0.2], [0.3]]
    metadata = [{"document_id": "doc1"} for _ in range(3)]
    ids = ["1", "2", "3"]
    vector_store.add_embeddings(embeddings, metadata, ids)
    assert vector_store.count() == 3

def test_search_empty_store(vector_store):
    results = vector_store.search([0.1, 0.2], top_k=2)
    assert len(results["ids"][0]) == 0

def test_metadata_preserved(vector_store):
    embeddings = [[1.0]]
    metadata = [{"document_id": "doc1", "paragraph_id": "p1", "text": "Test"}]
    ids = ["id1"]
    vector_store.add_embeddings(embeddings, metadata, ids)
    
    results = vector_store.search([1.0], top_k=1)
    meta = results["metadatas"][0][0]
    assert meta["document_id"] == "doc1"
    assert meta["paragraph_id"] == "p1"
    assert meta["text"] == "Test"
