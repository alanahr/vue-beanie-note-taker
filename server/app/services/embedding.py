"""Sentence-transformers wrapper for generating vector embeddings.

The model is loaded lazily and cached via ``lru_cache`` so it is only
instantiated once per process. All functions are synchronous because
``sentence-transformers`` is a blocking library.
"""

from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache
def get_model() -> SentenceTransformer:
    """Load and cache the sentence-transformers model.

    The model ID comes from ``settings.embedding_model_name``. Caching
    ensures the model is loaded into memory only once per process.

    Returns:
        The initialised ``SentenceTransformer`` instance.
    """
    return SentenceTransformer(settings.embedding_model_name)


def generate_embedding(text: str) -> List[float]:
    """Generate a normalised embedding vector for a single text input.

    Args:
        text: The input string to embed.

    Returns:
        A list of floats representing the embedding vector.
    """
    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate normalised embedding vectors for a batch of texts.

    Args:
        texts: A list of input strings to embed.

    Returns:
        A list of embedding vectors, one per input text.
    """
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]
