"""Input relevance evaluator — V3."""
import json
import re
from pathlib import Path
from typing import Any


def evaluate_input(script_text: str) -> dict[str, Any]:
    """Evaluate input script and return relevance score."""
    char_count = len(script_text)
    paragraphs = [p.strip() for p in script_text.split("\n") if p.strip()]
    lines = [l.strip() for l in script_text.split("\n") if l.strip()]

    score = 0.0
    if char_count > 300:
        score += 0.4
    elif char_count > 200:
        score += 0.3
    elif char_count > 100:
        score += 0.2
    elif char_count > 50:
        score += 0.1

    if len(paragraphs) >= 5:
        score += 0.3
    elif len(paragraphs) >= 3:
        score += 0.2
    elif len(paragraphs) >= 2:
        score += 0.1

    if len(lines) >= 10:
        score += 0.2
    elif len(lines) >= 5:
        score += 0.1

    score = min(1.0, score)
    suitable = score >= 0.7

    return {
        "score": score,
        "suitable": suitable,
        "char_count": char_count,
        "paragraph_count": len(paragraphs),
        "line_count": len(lines),
    }


def build_input_relevance_report(project_dir: Path) -> dict[str, Any]:
    script_path = project_dir / "input_script.md"
    narration_path = project_dir / "narration_plan.json"

    script_text = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
    narration_plan = {}
    if narration_path.exists():
        narration_plan = json.loads(narration_path.read_text(encoding="utf-8"))

    sentences = narration_plan.get("sentence_list", [])
    narration_text = " ".join(s.get("text", "") for s in sentences)

    char_count = len(script_text)
    word_count = len(script_text.split())
    sentence_count = len(sentences)

    # Score based on content volume
    score = 0.0
    if char_count > 300:
        score += 0.4
    elif char_count > 200:
        score += 0.3
    elif char_count > 100:
        score += 0.2
    elif char_count > 50:
        score += 0.1

    paragraphs = [p.strip() for p in script_text.split("\n") if p.strip()]
    if len(paragraphs) >= 5:
        score += 0.3
    elif len(paragraphs) >= 3:
        score += 0.2
    elif len(paragraphs) >= 2:
        score += 0.1

    lines = [l.strip() for l in script_text.split("\n") if l.strip()]
    if len(lines) >= 10:
        score += 0.2
    elif len(lines) >= 5:
        score += 0.1

    score = min(1.0, score)

    status = "PASS" if score >= 0.7 else "FAIL"

    return {
        "status": status,
        "input_relevance_score": score,
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": len(paragraphs),
        "line_count": len(lines),
        "narration_sentence_count": len(sentences),
    }