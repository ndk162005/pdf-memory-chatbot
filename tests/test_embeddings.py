import pytest
import math
from app.core.embeddings import EmbeddingService

def test_generate_single_embedding():
    service = EmbeddingService.get_instance()
    emb = service.generate_embedding("Test text")
    assert isinstance(emb, list)
    assert isinstance(emb[0], float)

def test_generate_multiple_embeddings():
    service = EmbeddingService.get_instance()
    embs = service.generate_embeddings(["Text one", "Text two"])
    assert len(embs) == 2

def test_embedding_dimension():
    service = EmbeddingService.get_instance()
    emb = service.generate_embedding("Test text")
    assert len(emb) == 384

def test_embeddings_are_normalized():
    service = EmbeddingService.get_instance()
    emb = service.generate_embedding("Test text")
    norm = sum(x**2 for x in emb) ** 0.5
    assert math.isclose(norm, 1.0, rel_tol=1e-2)

def test_empty_list():
    service = EmbeddingService.get_instance()
    embs = service.generate_embeddings([])
    assert embs == []

def test_similar_texts_have_similar_embeddings():
    service = EmbeddingService.get_instance()
    embs = service.generate_embeddings(["A quick brown fox", "The fast brown fox", "Random text about completely different things"])
    
    def cosine(v1, v2):
        return sum(x*y for x, y in zip(v1, v2))
        
    sim1 = cosine(embs[0], embs[1])
    sim2 = cosine(embs[0], embs[2])
    assert sim1 > sim2
