"""Pluggable knowledge packs + embedding retrieval for the voice agent.

`KB_SOURCE` selects which pack the agent answers from:
  - "portfolio" (default): Abdur Rehman Afzal's portfolio knowledge base
    (../knowledge_base.txt) - lets recruiters "talk to his CV".
  - "b1" (future): a curated property-listings pack for a real-estate concierge.

Retrieval mirrors the main RAG project: sentence-transformers embeddings +
cosine similarity. Chunks are embedded once at load; each query is embedded and
matched against them (top-k). Local embeddings keep per-query latency low, which
matters for a real-time voice agent.
"""

import os
from functools import lru_cache

import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "all-MiniLM-L6-v2"


def _portfolio_default_path() -> str:
    # knowledge_base.txt lives at the repo root, one level above voice-agent/.
    here = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(here, "..", "knowledge_base.txt"))


# Registry of packs: source key -> callable returning the file path.
# Adding the B1 pack later is just a new entry here + a curated listings file.
_PACK_PATHS = {
    "portfolio": lambda: os.getenv("KB_PATH", _portfolio_default_path()),
    # "b1": lambda: os.getenv("KB_PATH", os.path.join(
    #     os.path.dirname(__file__), "knowledge", "b1_listings.txt")),
}


class KnowledgeBase:
    """Loads a knowledge pack and answers similarity queries against it."""

    def __init__(self, source: str):
        self.source = source
        path = _PACK_PATHS[source]()
        logger.info(f"Loading knowledge pack '{source}' from {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Same chunking as the main project: split on blank lines.
        self.chunks = [c.strip() for c in content.split("\n\n") if c.strip()]

        self._model = SentenceTransformer(_MODEL_NAME)
        # normalize_embeddings=True -> unit vectors, so cosine == dot product.
        self._embeddings = self._model.encode(self.chunks, normalize_embeddings=True)
        logger.info(f"Knowledge pack ready: {len(self.chunks)} chunks embedded")

    def retrieve(self, query: str, k: int = 4) -> list[str]:
        """Return the top-k most relevant chunks for a query."""
        if not query or not self.chunks:
            return []
        q = self._model.encode([query], normalize_embeddings=True)[0]
        similarities = self._embeddings @ q  # cosine similarity (unit vectors)
        top = np.argsort(similarities)[::-1][:k]
        return [self.chunks[i] for i in top]


@lru_cache(maxsize=None)
def _build_kb(source: str) -> KnowledgeBase:
    return KnowledgeBase(source)


def get_kb(source: str | None = None) -> KnowledgeBase:
    """Return a cached KnowledgeBase for the active source (default from env)."""
    source = source or os.getenv("KB_SOURCE", "portfolio")
    if source not in _PACK_PATHS:
        logger.warning(f"Unknown KB_SOURCE '{source}', falling back to 'portfolio'")
        source = "portfolio"
    return _build_kb(source)  # cached on the concrete source key
