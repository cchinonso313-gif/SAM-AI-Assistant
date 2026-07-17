import pytest

from backend.core.semantic_memory import SemanticMemory, hashing_embed


def test_hashing_embed_normalized():
    v = hashing_embed("hello world")
    assert abs(float((v * v).sum()) - 1.0) < 1e-5


def test_add_and_search_relevance():
    mem = SemanticMemory()
    mem.add("The capital of France is Paris")
    mem.add("I enjoy eating pizza and pasta")
    mem.add("Python is a programming language")

    results = mem.search("what food do I like")
    assert results
    assert "pizza" in results[0]["text"]


def test_search_empty():
    assert SemanticMemory().search("anything") == []


def test_add_ignores_blank():
    mem = SemanticMemory()
    mem.add("   ")
    assert len(mem) == 0


def test_persistence_roundtrip(tmp_path):
    path = tmp_path / "mem.json"
    mem = SemanticMemory(path=path)
    mem.add("remember this fact", metadata={"tag": "note"})
    assert path.exists()

    reloaded = SemanticMemory(path=path)
    assert len(reloaded) == 1
    results = reloaded.search("remember fact")
    assert results and results[0]["metadata"]["tag"] == "note"


def test_custom_embedder():
    calls = []

    def embedder(text):
        calls.append(text)
        return [1.0, 0.0, 0.0]

    mem = SemanticMemory(embedder=embedder)
    mem.add("a")
    mem.search("b")
    assert calls  # embedder was used


def test_corrupt_file_starts_fresh(tmp_path):
    path = tmp_path / "mem.json"
    path.write_text("not json")
    mem = SemanticMemory(path=path)
    assert len(mem) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
