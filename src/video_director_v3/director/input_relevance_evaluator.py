"""Input relevance evaluator - checks if input is suitable for video."""
from typing import Dict, Any


def evaluate_input(script_content: str) -> Dict[str, Any]:
    """Evaluate if input script is relevant for video generation."""
    word_count = len(script_content.split())
    char_count = len(script_content)

    # Score based on content volume - adapted for Chinese text
    score = 0.0
    if char_count > 500:
        score += 0.5
    elif char_count > 300:
        score += 0.4
    elif char_count > 200:
        score += 0.3
    elif char_count > 100:
        score += 0.2
    elif char_count > 50:
        score += 0.1

    # Additional score for having multiple paragraphs
    paragraphs = [p.strip() for p in script_content.split('\n') if p.strip()]
    if len(paragraphs) >= 5:
        score += 0.4
    elif len(paragraphs) >= 3:
        score += 0.2
    elif len(paragraphs) >= 2:
        score += 0.1

    # Additional score for line breaks within paragraphs (indicates structure)
    lines = [l.strip() for l in script_content.split('\n') if l.strip()]
    if len(lines) >= 10:
        score += 0.2
    elif len(lines) >= 5:
        score += 0.1

    # Cap at 1.0
    score = min(1.0, score)

    return {
        "score": score,
        "word_count": word_count,
        "char_count": char_count,
        "paragraph_count": len(paragraphs),
        "line_count": len(lines),
        "suitable": score >= 0.7,
    }