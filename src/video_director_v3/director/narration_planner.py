#!/usr/bin/env python3
"""Narration planner — V3 migrated from V2."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROLE_KEYWORDS = {
    "hook": ["为什么", "有没有发现", "真正", "不是"],
    "pain": ["问题", "卡", "焦虑", "累", "效率"],
    "method": ["第一", "第二", "第三", "先", "再", "最后", "步骤"],
    "quote": ["记住", "本质", "不是", "而是"],
    "cta": ["收藏", "关注", "流程", "下一步", "闭环"],
}


def clean_text(raw_script: str) -> str:
    text = re.sub(r"```.*?```", "", raw_script, flags=re.S)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = re.sub(r"\[[^\]]+\]", "", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    """Split text into sentences. Preserves structured lists but collapses inline newlines."""
    # Collapse single newlines to spaces (within paragraphs/lists)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    # Split on sentence delimiters AND paragraph breaks (double newlines)
    parts = re.split(r"[。！？!?；;]\s*|\n\n+", text)
    result = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Remove markdown headers
        p = re.sub(r"^#+\s*", "", p, flags=re.M)
        # Remove list markers
        p = re.sub(r"^-\s+", "", p, flags=re.M)
        p = re.sub(r"^\*\s+", "", p, flags=re.M)
        p = re.sub(r"^\d+[．、\.]\s*", "", p)
        # Remove bold markers
        p = re.sub(r"\*\*", "", p)
        p = p.strip()
        if len(p) >= 4:
            result.append(p)
    return result


def estimate_duration(text: str, speed: float = 5.8) -> float:
    chinese_chars = len(re.findall(r"[一-鿿A-Za-z0-9]", text))
    return round(max(1.8, chinese_chars / speed), 2)


def compress_narration_to_duration(
    sentences: list[str],
    target_duration: float,
    rate: float = 5.8,
) -> list[str]:
    """Select and scale sentences to produce ~38-43s of narration.

    Strategy:
    1. Drop lowest-priority sentences until total fits within budget
    2. Proportionally scale remaining sentences only if needed to reach 38s floor
    """
    min_duration = 38.0
    ideal_chars = int(target_duration * rate)
    min_chars = int(min_duration * rate)

    current_chars = sum(len(s) for s in sentences)
    if current_chars <= ideal_chars:
        return sentences

    role_order = {"hook": 5, "cta": 5, "pain": 4, "method": 3, "evidence": 3, "quote": 2, "explain": 1}
    scored = []
    for i, s in enumerate(sentences):
        role = classify_role(s, i, len(sentences))
        priority = role_order.get(role, 1)
        scored.append((i, s, priority, len(s)))

    scored.sort(key=lambda x: -x[2])

    # Step 1: Greedily select by priority until we fit
    selected = []
    chars_kept = 0
    for idx, text, priority, length in scored:
        if chars_kept + length <= ideal_chars:
            selected.append((idx, text, priority, length))
            chars_kept += length
        elif chars_kept < min_chars and chars_kept + length <= min_chars + 30:
            selected.append((idx, text, priority, length))
            chars_kept += length

    # Step 2: If still under min_chars, proportionally fill remaining budget
    if chars_kept < min_chars:
        remaining = ideal_chars - chars_kept
        # Add next-highest sentences to fill remaining budget
        for idx, text, priority, length in scored:
            if (idx, text, priority, length) not in selected:
                if chars_kept + length <= ideal_chars:
                    selected.append((idx, text, priority, length))
                    chars_kept += length
                if chars_kept >= min_chars:
                    break

    selected.sort(key=lambda x: x[0])
    result = [s for _, s, _, _ in selected]

    # Step 3: If total still exceeds budget, scale proportionally
    current = sum(len(s) for s in result)
    if current > ideal_chars:
        scale = ideal_chars / current
        result = [s[:max(12, int(len(s) * scale))] for s in result]

    return result


def classify_role(text: str, index: int, total: int) -> str:
    if index == 0:
        return "hook"
    if index == total - 1:
        return "cta"
    for role, keywords in ROLE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return role
    return "explain"


def build_narration_plan(
    raw_script: str,
    project_id: str,
    title: str = "",
    platform: str = "douyin",
    target_duration: float = 40.0,
) -> dict[str, Any]:
    cleaned = clean_text(raw_script)
    sentences_raw = split_sentences(cleaned)

    # V2-style: compress to fit target duration
    max_chars = int(target_duration * 5.8)
    total_chars = sum(len(s) for s in sentences_raw)
    if total_chars > max_chars:
        sentences_raw = compress_narration_to_duration(sentences_raw, target_duration)

    sentences = []
    for i, text in enumerate(sentences_raw):
        role = classify_role(text, i, len(sentences_raw))
        estimated_dur = estimate_duration(text)
        sentences.append({
            "sentence_id": f"S{i+1:02d}",
            "text": text,
            "role": role,
            "estimated_duration": estimated_dur,
            "pause_after": 0.2,
            "emphasis_words": [],
        })

    total_estimated = sum(s["estimated_duration"] for s in sentences)

    return {
        "project_id": project_id,
        "title": title or project_id,
        "platform": platform,
        "target_duration": target_duration,
        "sentence_count": len(sentences),
        "total_chinese_chars": sum(len(re.findall(r"[一-鿿]", s["text"])) for s in sentences),
        "estimated_total_duration": round(total_estimated, 2),
        "sentence_list": sentences,
        "director_output": {
            "scenes": _build_scenes_from_sentences(sentences, target_duration),
        },
    }


def _build_scenes_from_sentences(sentences: list[dict[str, Any]], target_duration: float) -> list[dict[str, Any]]:
    scene_roles = ["hook", "pain", "method", "method", "method", "evidence", "proof", "cta"]
    scene_dur = target_duration / len(scene_roles)
    cursor = 0.0
    scenes = []
    sent_idx = 0

    for i, role in enumerate(scene_roles):
        if cursor >= target_duration:
            break
        start = cursor
        duration = min(scene_dur, target_duration - cursor)
        narration = sentences[sent_idx]["text"] if sent_idx < len(sentences) else ""
        scenes.append({
            "scene_id": f"S{i+1:02d}",
            "role": role,
            "start": round(start, 2),
            "duration": round(duration, 2),
            "narration": narration,
        })
        cursor += duration
        sent_idx = min(sent_idx + 1, len(sentences) - 1)

    return scenes


def build_audio_timeline(narration_plan: dict[str, Any]) -> dict[str, Any]:
    current = 0.0
    timings = []
    for sentence in narration_plan.get("sentence_list", []):
        duration = float(sentence.get("estimated_duration", 3.0))
        start = round(current, 2)
        end = round(start + duration, 2)
        timings.append({
            "sentence_id": sentence.get("sentence_id", ""),
            "text": sentence.get("text", ""),
            "start": start,
            "end": end,
            "duration": duration,
            "pause_after": sentence.get("pause_after", 0.0),
            "emphasis_words": sentence.get("emphasis_words", []),
        })
        current = end + float(sentence.get("pause_after", 0.0))
    return {"total_duration": round(current, 2), "sentence_timings": timings}


def write_outputs(narration_plan: dict[str, Any], project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    voiceover = "\n".join(s.get("text", "") for s in narration_plan.get("sentence_list", []))
    (project_dir / "voiceover_script.md").write_text(voiceover, encoding="utf-8")
    (project_dir / "narration_plan.json").write_text(
        json.dumps(narration_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )