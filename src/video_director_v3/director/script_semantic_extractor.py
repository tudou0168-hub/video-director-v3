"""Script semantic extractor — V3."""
import json
import re
from pathlib import Path
from typing import Any


def extract_semantics(script_content: str) -> dict[str, Any]:
    """Extract semantic structure from input script."""
    sentences = [s.strip() for s in re.split(r"[。！？!?；;]\s*", script_content) if s.strip()]
    char_count = len(script_content)
    chinese_chars = len(re.findall(r"[一-鿿]", script_content))

    # Detect topic keywords
    text_lower = script_content.lower()
    topics = []
    if "obsidian" in text_lower or "知识库" in script_content:
        topics.append("knowledge_base")
    if "效率" in script_content or "效率" in script_content:
        topics.append("productivity")
    if "第二大脑" in script_content or "大脑" in script_content:
        topics.append("second_brain")
    if "笔记" in script_content or "note" in text_lower:
        topics.append("note_taking")

    key_points = []
    for sent in sentences[:5]:
        if len(sent) > 10:
            key_points.append(sent[:50])

    return {
        "topics": topics,
        "key_points": key_points,
        "tone": "informative",
        "target_audience": "knowledge_workers",
        "sentence_count": len(sentences),
        "chinese_char_count": chinese_chars,
    }


def write_semantic_output(semantics: dict[str, Any], project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "script_semantics.json").write_text(
        json.dumps(semantics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )