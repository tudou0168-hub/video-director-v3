"""Viral QA evaluator — V3-P3.6 (final stage).

Scores a generated video preview / render on 6 dimensions that align with
publicly observable content quality principles (NOT platform algorithm
weights, which are not public).

Dimensions:
  1. Hook               — 0-3s sentence carries conflict / keyword / pattern-break
  2. Promise            — 0-6s sentence tells viewer what they'll get
  3. Saveable value      — script contains reusable structure (checklist / steps / framework)
  4. Comment trigger     — script contains genuine question / ask (not "click like!")
  5. Visual rhythm       — number of unique visual_templates used across scenes
  6. Sync reliability    — derived from sync_report.json (max_drift <= 1.0s)

Each dimension scored 0-10. PASS if total >= 42/60 (70%).
Per-dimension PASS threshold: >= 7.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# Per-dimension keywords / signals (Chinese simplified).
HOOK_SIGNALS = (
    "为什么", "有没有", "真相", "记住", "搞错", "不要以为", "重点是", "核心是",
    "你只剩", "最后几天", "3 天", "反", "反差", "对比", "金句",
)
PROMISE_SIGNALS = (
    "我会", "今天我会", "告诉你", "教你", "怎么用", "如何", "方法", "步骤", "流程",
    "你将获得", "学到", "你会", "看完就会", "掌握", "你会掌握", "看完",
)
SAVEABLE_SIGNALS = (
    "步骤", "清单", "复盘", "框架", "方法", "模板", "套路", "原则", "标准",
    "第一条", "第二步", "第三步", "三个", "四个", "五个", "W1", "W2",
    "象限", "阶梯", "步骤", "概念", "层次",
)
COMMENT_SIGNALS = (
    "你愿意", "愿不愿意", "评论区", "告诉我", "你想", "你觉得", "你打算",
    "分享", "留言", "讨论", "经验", "先说",
)


def _count_signal_hits(text: str, signals: tuple[str, ...]) -> int:
    if not text:
        return 0
    return sum(1 for s in signals if s in text)


def _score_hook(narration_plan: dict[str, Any], storyboard: dict[str, Any]) -> dict[str, Any]:
    sentences = narration_plan.get("sentence_list", []) or []
    first = sentences[0].get("text", "") if sentences else ""
    has_keyword = any(sentences[0].get("emphasis_words") for _ in [0]) if sentences else False
    hits = _count_signal_hits(first, HOOK_SIGNALS)
    score = 0
    details: list[str] = []
    if 0 < len(first) <= 30:
        score += 3
        details.append("长度合适")
    elif len(first) > 30:
        details.append(f"首句 {len(first)} 字偏长（建议 ≤30）")
    if hits >= 1:
        score += 4
        details.append(f"冲击词命中 {hits} 个")
    else:
        details.append("首句缺少冲击词")
    if has_keyword:
        score += 3
        details.append("有 emphasis_words")
    # Bonus: hook uses one of the high-impact visual templates
    scenes = storyboard.get("scenes", []) or []
    if scenes and scenes[0].get("visual_template") in {
        "hook_big_claim", "countdown_strike", "keyword_punchline", "myth_bust", "before_after_flash",
    }:
        score += 0  # already a high-impact template; no extra but counted in rhythm
        details.append(f"hook visual = {scenes[0].get('visual_template')}")
    return {"score": min(10, score), "details": "; ".join(details) or "无信号"}


def _score_promise(narration_plan: dict[str, Any]) -> dict[str, Any]:
    sentences = narration_plan.get("sentence_list", []) or []
    # Look at the first 1-2 non-hook sentences (i.e. Promise slot).
    body = [s.get("text", "") for s in sentences[1:3] if s]
    blob = " ".join(body)
    hits = _count_signal_hits(blob, PROMISE_SIGNALS)
    score = 0
    details: list[str] = []
    if hits >= 2:
        score += 7
        details.append(f"承诺信号命中 {hits} 个")
    elif hits == 1:
        score += 4
        details.append("承诺信号 1 个")
    else:
        details.append("前 2-3 句缺少承诺信号")
    # Bonus: short promise density — only if hits >= 1 (avoid padding empty)
    if hits >= 1 and body and all(len(t) <= 35 for t in body):
        score += 3
        details.append("承诺句长度合理")
    return {"score": min(10, score), "details": "; ".join(details) or "无信号"}


def _score_saveable(narration_plan: dict[str, Any]) -> dict[str, Any]:
    sentences = narration_plan.get("sentence_list", []) or []
    blob = " ".join(s.get("text", "") for s in sentences)
    hits = _count_signal_hits(blob, SAVEABLE_SIGNALS)
    score = 0
    details: list[str] = []
    if hits >= 4:
        score += 9
        details.append(f"可复用结构信号 {hits} 个")
    elif hits >= 2:
        score += 6
        details.append(f"可复用结构信号 {hits} 个")
    elif hits >= 1:
        score += 3
        details.append("可复用结构信号偏少")
    else:
        details.append("缺少步骤/清单/框架等可复用结构")
    return {"score": min(10, score), "details": "; ".join(details) or "无信号"}


def _score_comment(narration_plan: dict[str, Any]) -> dict[str, Any]:
    sentences = narration_plan.get("sentence_list", []) or []
    blob = " ".join(s.get("text", "") for s in sentences)
    hits = _count_signal_hits(blob, COMMENT_SIGNALS)
    score = 0
    details: list[str] = []
    if hits >= 2:
        score += 9
        details.append(f"评论触发信号 {hits} 个")
    elif hits == 1:
        score += 6
        details.append("评论触发信号 1 个")
    else:
        details.append("缺少自然评论引导")
    # Check it's not a "click like / subscribe" pattern
    bad_signals = ("点赞", "关注", "订阅", "三连", "求赞")
    if any(b in blob for b in bad_signals):
        score = max(0, score - 3)
        details.append("含机械诱导词，建议改为自然问题")
    return {"score": min(10, score), "details": "; ".join(details) or "无信号"}


def _score_visual_rhythm(storyboard: dict[str, Any]) -> dict[str, Any]:
    scenes = storyboard.get("scenes", []) or []
    if not scenes:
        return {"score": 0, "details": "无分镜"}
    templates = [s.get("visual_template", "") for s in scenes]
    unique = set(t for t in templates if t)
    ratio = len(unique) / max(len(scenes), 1)
    score = round(ratio * 10, 1)
    details = f"unique visual_templates = {len(unique)} / {len(scenes)} = {ratio:.2f}"
    # Bonus: 30 seed library
    if len(unique) >= 6:
        score = min(10, score + 1)
        details += "; ≥6 变体（30 模板库已就绪）"
    return {"score": int(min(10, score)), "details": details}


def _score_sync_reliability(project_dir: Path) -> dict[str, Any]:
    # Accept either a project_dir (looks for rendered_smoke/sync_report.json inside)
    # or a parent that already points at rendered_smoke (then look for sync_report.json
    # directly). This keeps the caller flexible.
    if project_dir.name == "rendered_smoke":
        sync_path = project_dir / "sync_report.json"
    else:
        sync_path = project_dir / "rendered_smoke" / "sync_report.json"
    if not sync_path.exists():
        return {"score": 0, "details": "无 sync_report.json（请先跑 5s smoke render）"}
    try:
        data = json.loads(sync_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"score": 0, "details": f"sync_report.json 解析失败: {e}"}
    if data.get("status") != "PASS":
        return {"score": 0, "details": f"sync_report status != PASS (got {data.get('status')})"}
    drift = float(data.get("checks", {}).get("max_drift_seconds", 999.0))
    if drift <= 0.1:
        return {"score": 10, "details": f"max_drift = {drift:.3f}s（优秀）"}
    if drift <= 0.5:
        return {"score": 9, "details": f"max_drift = {drift:.3f}s（良好）"}
    if drift <= 1.0:
        return {"score": 7, "details": f"max_drift = {drift:.3f}s（达标）"}
    return {"score": 4, "details": f"max_drift = {drift:.3f}s（>1.0s 不达标）"}


def build_viral_quality_report(
    *,
    project_id: str,
    project_dir: Path,
    narration_plan: dict[str, Any],
    storyboard: dict[str, Any],
    sync_report_path: Path | None = None,
) -> dict[str, Any]:
    """Build viral_quality_report.json for a preview/render.

    Returns a dict with per-dimension scores, total, status (PASS/FAIL),
    and an A/B variant manifest (just enumerates the 2 candidate hook
    seeds + 2 candidate method/explainer seeds — actual A/B rendering is
    out of scope; the manifest is a guide for downstream manual selection).
    """
    dimensions = {
        "hook": _score_hook(narration_plan, storyboard),
        "promise": _score_promise(narration_plan),
        "saveable_value": _score_saveable(narration_plan),
        "comment_trigger": _score_comment(narration_plan),
        "visual_rhythm": _score_visual_rhythm(storyboard),
        "sync_reliability": _score_sync_reliability(sync_report_path.parent if sync_report_path else project_dir),
    }
    total = sum(d["score"] for d in dimensions.values())
    max_total = len(dimensions) * 10
    passed_dimensions = [name for name, d in dimensions.items() if d["score"] >= 7]
    failed_dimensions = [name for name, d in dimensions.items() if d["score"] < 7]
    status = "PASS" if total >= int(max_total * 0.7) and not failed_dimensions else "FAIL"
    return {
        "status": status,
        "project_id": project_id,
        "total_score": total,
        "max_score": max_total,
        "pass_threshold": int(max_total * 0.7),
        "passed_dimensions": passed_dimensions,
        "failed_dimensions": failed_dimensions,
        "dimensions": dimensions,
        "ab_variants": _ab_variant_manifest(storyboard),
        "notes": (
            "评分基于公开可见的内容质量原则（不冒充平台推荐算法）。"
            "用于内部筛选和复盘，不用于承诺爆款。"
        ),
    }


def _ab_variant_manifest(storyboard: dict[str, Any]) -> dict[str, Any]:
    """Suggest 2 hook variants + 2 visual variants for the same script.

    The manifest is a guide; actual A/B rendering is out of scope for
    V3-P3.6 — picking a different seed and re-running preview is
    cheaper than rendering two full MP4s upfront.
    """
    scenes = storyboard.get("scenes", []) or []
    if not scenes:
        return {"hook": [], "method": [], "explanation": []}
    current_hook = scenes[0].get("visual_template", "hook_big_claim")
    hook_alternates = [t for t in ("hook_big_claim", "countdown_strike", "keyword_punchline", "myth_bust", "before_after_flash") if t != current_hook][:2]
    return {
        "current_hook": current_hook,
        "hook_variants": hook_alternates,
        "method_variants": ["framework_quadrant", "step_ladder", "decision_tree", "concept_layers"][:2],
        "evidence_variants": ["metric_dashboard", "case_study_card", "evidence_cards", "progress_tracker"][:2],
        "cta_variants": ["end_score_goodbye", "scorecard", "button_banner", "comment_invite"][:2],
        "usage": "修改 ROLE_NARRATION_OVERRIDE keyword 顺序或调用 generate_preview 强制指定 seed_id 后重跑 preview",
    }
