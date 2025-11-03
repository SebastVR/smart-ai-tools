"""
Lightweight extractive summarization service.

Heuristic:
- Split text into sentences.
- Rank by length (as a proxy for information density).
- Keep top-N sentences and restore original order.
"""

import re
from typing import List, Tuple

_SENT_SPLIT = re.compile(r'(?<=[\.\!\?])\s+')


def split_sentences(text: str) -> List[str]:
    """Split text into sentences using a simple regex rule."""
    parts = _SENT_SPLIT.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def extractive_summary(
    text: str,
    ratio: float,
    max_sentences: int | None = None
) -> Tuple[List[str], int]:
    """
    Compute a minimal extractive summary.

    Args:
        text: Raw input text.
        ratio: Fraction of sentences to keep (0.05 - 0.6).
        max_sentences: Optional absolute cap for the number of sentences.

    Returns:
        chosen: The selected summary sentences in original order.
        total: Total number of sentences in the input text.
    """
    sentences = split_sentences(text)
    if not sentences:
        return [], 0

    ranked = sorted(sentences, key=len, reverse=True)
    n = max(1, int(len(sentences) * ratio))
    if max_sentences:
        n = min(n, max_sentences)

    chosen = sorted(ranked[:n], key=lambda s: sentences.index(s))
    return chosen, len(sentences)