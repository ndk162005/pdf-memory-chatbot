import pytest
from unittest.mock import MagicMock
from app.retrieval.ranking import ResultRanker
from app.retrieval.semantic_search import SemanticSearch

def test_ranker_sorts_by_score():
    ranker = ResultRanker()
    results = [
        {"id": "1", "score": 0.5},
        {"id": "2", "score": 0.9},
        {"id": "3", "score": 0.7}
    ]
    ranked = ranker.rank(results, top_k=3)
    assert ranked[0]["id"] == "2"
    assert ranked[1]["id"] == "3"
    assert ranked[2]["id"] == "1"

def test_ranker_deduplicates():
    ranker = ResultRanker()
    results = [
        {"id": "1", "score": 0.9, "text": "Same text"},
        {"id": "2", "score": 0.8, "text": "Same text"}
    ]
    ranked = ranker.rank(results, top_k=2)
    assert len(ranked) == 1
    assert ranked[0]["id"] == "1"

def test_ranker_respects_top_k():
    ranker = ResultRanker()
    results = [{"id": str(i), "score": 1.0 - i*0.1} for i in range(5)]
    ranked = ranker.rank(results, top_k=2)
    assert len(ranked) == 2

def test_ranker_empty_results():
    ranker = ResultRanker()
    assert ranker.rank([], top_k=5) == []

def test_semantic_search_integration():
    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = {
        "ids": [["id1"]],
        "metadatas": [[{"document_id": "doc1", "text": "hello"}]],
        "distances": [[0.1]]
    }
    
    mock_embed_service = MagicMock()
    mock_embed_service.generate_embedding.return_value = [0.1, 0.2]
    
    searcher = SemanticSearch(vector_store=mock_vector_store, embedding_service=mock_embed_service)
    results = searcher.search("query", top_k=1)
    
    assert len(results) == 1
    assert results[0]["id"] == "id1"
    assert results[0]["score"] == pytest.approx(0.9)
