"""Lightweight semantic long-term memory with vector recall.

Stores text entries as embedding vectors and retrieves them by cosine
similarity, so NOVA can recall relevant facts across sessions rather than only
the most recent turns.

The default embedder is a dependency-free hashing bag-of-words vectorizer
(deterministic, offline). It is intentionally pluggable: pass any
``Callable[[str], Sequence[float]]`` (e.g. a real embedding-model client) to
``SemanticMemory`` to upgrade recall quality without changing callers.
"""

import json
import logging
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_DIM = 256
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def hashing_embed(text: str, dim: int = DEFAULT_DIM) -> np.ndarray:
    """Embed text into a fixed-dim vector via token hashing (offline, stable)."""
    vec = np.zeros(dim, dtype=np.float32)
    for token in _TOKEN_RE.findall(text.lower()):
        vec[hash(token) % dim] += 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm else vec


class SemanticMemory:
    """Persistent vector store for semantic recall."""

    def __init__(
        self,
        path: Optional[Path] = None,
        embedder: Optional[Callable[[str], Sequence[float]]] = None,
        dim: int = DEFAULT_DIM,
    ):
        self.path = Path(path) if path else None
        self.dim = dim
        self._embedder = embedder or (lambda t: hashing_embed(t, dim))
        self._entries: List[Dict] = []
        if self.path and self.path.exists():
            self.load()

    def _embed(self, text: str) -> np.ndarray:
        return np.asarray(self._embedder(text), dtype=np.float32)

    def add(self, text: str, metadata: Optional[Dict] = None) -> None:
        """Add a memory entry and persist if a path is configured."""
        if not text or not text.strip():
            return
        self._entries.append(
            {
                "text": text,
                "metadata": metadata or {},
                "vector": self._embed(text).tolist(),
            }
        )
        if self.path:
            self.save()

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Return the ``top_k`` most similar entries with a ``score`` field."""
        if not self._entries:
            return []
        q = self._embed(query)
        q_norm = np.linalg.norm(q)
        if not q_norm:
            return []

        scored = []
        for entry in self._entries:
            v = np.asarray(entry["vector"], dtype=np.float32)
            denom = np.linalg.norm(v) * q_norm
            score = float(np.dot(q, v) / denom) if denom else 0.0
            scored.append((score, entry))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            {"text": e["text"], "metadata": e["metadata"], "score": s}
            for s, e in scored[:top_k]
            if s > 0
        ]

    def __len__(self) -> int:
        return len(self._entries)

    def save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._entries), encoding="utf-8")

    def load(self) -> None:
        try:
            self._entries = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001 - start fresh on corruption
            logger.warning(f"Could not load semantic memory: {e}")
            self._entries = []
