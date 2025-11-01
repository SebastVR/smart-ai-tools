import re
from typing import List, Tuple

# Split on sentence-ending punctuation followed by whitespace.
_SENT_SPLIT = re.compile(r'(?<=[\.\!\?])\s+')

def split_sentences(text: str) -> List[str]:
    """Split text into sentences using a simple regex-based rule."""
    parts = _SENT_SPLIT.split(text.strip())
    return [p.strip() for p in parts if p.strip()]

def extractive_summary(
    text: str, ratio: float, max_sentences: int | None = None
) -> Tuple[List[str], int]:
    """
    Minimal extractive heuristic:
    - Split text into sentences.
    - Rank sentences by length (as a lightweight proxy for information density).
    - Select the top-N sentences and restore original order.
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