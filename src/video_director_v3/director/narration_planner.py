#!/usr/bin/env python3
"""Narration planner — V3 migrated from V2."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from video_director_v3.director.viral_script_distiller import distill_for_short_video

HOOK_KEYWORDS = ["为什么", "有没有", "你有没有", "有没有发现", "真正的问题", "你是不是", "你只剩", "倒计时", "3 天", "还剩", "金句", "重点是", "核心是"]
PAIN_KEYWORDS = ["问题", "卡", "焦虑", "累", "翻遍", "记不住", "想不起来", "从零开始", "之前也是", "状态", "列表", "清单"]
METHOD_KEYWORDS = ["第一步", "第二步", "第三步", "步骤", "先", "再", "最后", "需要素材时", "四象限", "框架", "矩阵", "要不要", "决策", "判断", "层次", "递进", "阶梯", "从 0 到"]
EVIDENCE_KEYWORDS = ["30 秒", "只需要", "以前", "现在", "效率", "拿到素材包", "不到 10 本", "不到 1 本", "指标", "数据", "增长", "对比", "提升", "完播率", "案例", "学员", "同学", "博主", "账号", "进度", "曲线", "每周"]
PROOF_KEYWORDS = ["你才能", "这样你", "把记住", "交给第二大脑", "真正的创造", "形成闭环", "维度", "板块", "三条", "四条", "评论", "想问", "评论区", "你愿意", "愿不愿意", "知识网络", "关系", "节点", "知识图谱"]
CTA_KEYWORDS = ["收藏", "关注", "照着搭", "跑一遍", "最小闭环", "下一步", "总结一句", "一句话", "马上", "立即", "完结", "下期", "系列", "再见", "得分"]
EXPLAIN_KEYWORDS = ["简单讲", "本质", "不是", "而是", "负责", "系统"]


def clean_text(raw_script: str) -> str:
    text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", raw_script, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
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


def classify_role(text: str, index: int, total: int) -> str:
    normalized = text.strip()
    if index == 0:
        return "hook"
    if index == total - 1:
        return "cta"

    if any(keyword in normalized for keyword in CTA_KEYWORDS):
        return "cta"
    if any(keyword in normalized for keyword in PROOF_KEYWORDS):
        return "proof"
    if "以前" in normalized and "现在" in normalized:
        return "evidence"
    if any(keyword in normalized for keyword in PAIN_KEYWORDS):
        return "pain"
    if any(keyword in normalized for keyword in EVIDENCE_KEYWORDS):
        return "evidence"
    if any(keyword in normalized for keyword in METHOD_KEYWORDS):
        return "method"
    if any(keyword in normalized for keyword in EXPLAIN_KEYWORDS):
        return "explain"
    if any(keyword in normalized for keyword in HOOK_KEYWORDS):
        return "hook"
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
    distillation = distill_for_short_video(sentences_raw)
    sentences_raw = distillation["sentences"]

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
        "distillation": distillation,
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
