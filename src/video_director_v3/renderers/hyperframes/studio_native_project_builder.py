"""Build a minimal Studio-native HyperFrames preview project."""
from __future__ import annotations

import json
import shutil
import subprocess
import re
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any

from video_director_v3.director.template_contracts import require_contract_scene
from video_director_v3.renderers.hyperframes.publish_templates import get_scene_body


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _scene_flag(scene: dict[str, Any], key: str) -> bool:
    value = scene.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def _compact_text(text: str, limit: int) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip(" ，,。！？!?；;:：")
    if len(cleaned) <= limit:
        return cleaned
    cut_points = [cleaned.rfind(ch, 0, limit) for ch in "，,。！？!?；;:："]
    cut = max(cut_points) if cut_points else -1
    if cut >= max(6, limit // 2):
        return cleaned[:cut].rstrip(" ，,。！？!?；;:：")
    return cleaned[:limit].rstrip(" ，,。！？!?；;:：")


def _scene_has_digits(*values: Any) -> bool:
    for value in values:
        if re.search(r"\d", str(value or "")):
            return True
    return False


def _visual_scene_family(scene: dict[str, Any]) -> str:
    role = str(scene.get("role") or scene.get("scene_pack_role") or "").strip().lower()
    layout_family = str(scene.get("layout_family") or "").strip()
    if role == "hook" or layout_family in {"hero_metric", "hero_statement"}:
        return "hook"
    if role in {"cta", "offer", "verdict"} or layout_family in {"action_close", "checklist_close", "insight_close", "offer_close"}:
        return "close"
    if role in {"pain", "problem", "conflict"} or layout_family in {"myth_bust", "broken_chain", "pain_card_stack"}:
        return "problem"
    if role in {"proof", "evidence"} or layout_family in {"proof_matrix", "comparison_board"}:
        return "proof"
    if layout_family in {"framework_map", "knowledge_graph", "concept_layers", "progress_tracker", "section_board"}:
        return "framework"
    if layout_family in {"tool_pipeline", "config_panel", "file_tree", "process_ladder", "step_ladder", "tool_stack", "decision_fork", "opportunity_map"}:
        return "tool"
    if role == "method":
        return "tool"
    return "other"


def _visual_scene_target_spec(audio_duration: float, source_scene_count: int) -> dict[str, float | int]:
    if audio_duration < 30 or source_scene_count <= 4:
        target = max(1, min(source_scene_count, max(1, source_scene_count)))
        return {
            "target_visual_scenes": target,
            "max_visual_scenes": source_scene_count,
            "min_visual_scene_duration": 1.0,
            "preferred_visual_scene_duration": round(audio_duration / max(target, 1), 3) if target else 0.0,
        }
    if audio_duration <= 60:
        target = max(4, round(audio_duration / 12))
        target = min(target, source_scene_count)
        return {
            "target_visual_scenes": target,
            "max_visual_scenes": min(6, source_scene_count),
            "min_visual_scene_duration": 4.0,
            "preferred_visual_scene_duration": round(max(7.0, audio_duration / max(target, 1)), 3),
        }
    if audio_duration <= 90:
        target = max(6, min(8, round(audio_duration / 12)))
        target = min(target, source_scene_count)
        return {
            "target_visual_scenes": target,
            "max_visual_scenes": min(9, source_scene_count),
            "min_visual_scene_duration": 7.0,
            "preferred_visual_scene_duration": round(audio_duration / max(target, 1), 3),
        }
    if audio_duration <= 120:
        target = min(8, source_scene_count)
        return {
            "target_visual_scenes": target,
            "max_visual_scenes": min(10, source_scene_count),
            "min_visual_scene_duration": 7.0,
            "preferred_visual_scene_duration": round(max(10.0, min(16.0, audio_duration / max(target, 1))), 3),
        }
    target = max(9, min(12, round(audio_duration / 14)))
    target = min(target, source_scene_count)
    return {
        "target_visual_scenes": target,
        "max_visual_scenes": min(14, source_scene_count),
        "min_visual_scene_duration": 7.0,
        "preferred_visual_scene_duration": round(max(10.0, min(16.0, audio_duration / max(target, 1))), 3),
    }


def _chapter_content_item_limit(layout_family: str) -> int:
    return {
        "hero_metric": 4,
        "hero_statement": 4,
        "tool_pipeline": 6,
        "config_panel": 6,
        "file_tree": 6,
        "process_ladder": 6,
        "step_ladder": 6,
        "tool_stack": 6,
        "framework_map": 6,
        "proof_matrix": 6,
        "comparison_board": 6,
        "knowledge_graph": 6,
        "concept_layers": 6,
        "progress_tracker": 6,
        "section_board": 6,
        "action_close": 6,
        "checklist_close": 6,
        "insight_close": 6,
        "offer_close": 6,
    }.get(layout_family, 5)


def _chapter_content_item_count(scene: dict[str, Any]) -> int:
    layout_family = str(scene.get("layout_family") or "").strip()
    slots = scene.get("slots", {}) if isinstance(scene.get("slots", {}), dict) else {}
    headline = str(scene.get("display_headline") or scene.get("visual_headline") or "").strip()
    subtitle = str(scene.get("display_subtitle") or scene.get("display_conclusion") or "").strip()
    anchor = str(scene.get("memory_anchor") or "").strip()
    result = str(scene.get("save_reason") or "").strip()

    if layout_family in {"hero_metric", "hero_statement"}:
        count = sum(1 for value in (headline, subtitle, anchor, result) if value)
        return max(3, min(4, count or 3))

    if layout_family in {"tool_pipeline", "config_panel", "file_tree", "process_ladder", "step_ladder", "tool_stack"}:
        items = []
        for key in ("steps", "tools"):
            values = slots.get(key)
            if isinstance(values, list):
                items.extend([str(value).strip() for value in values if str(value).strip()])
        visible = len(items) or 3
        return max(4, min(6, visible + 1))

    if layout_family in {"framework_map", "proof_matrix", "comparison_board", "knowledge_graph", "concept_layers", "progress_tracker", "section_board"}:
        items = []
        for key in ("quadrants", "nodes", "layers", "stages", "sections", "key_results", "proof_items"):
            values = slots.get(key)
            if isinstance(values, list):
                items.extend([str(value).strip() for value in values if str(value).strip()])
        visible = len(items) or 4
        return max(4, min(6, visible + 1))

    if layout_family in {"action_close", "checklist_close", "insight_close", "offer_close"}:
        items = []
        for key in ("checklist", "next_steps", "key_results"):
            values = slots.get(key)
            if isinstance(values, list):
                items.extend([str(value).strip() for value in values if str(value).strip()])
        visible = len(items) or 3
        return max(4, min(6, visible + 1))

    return max(3, min(5, sum(1 for value in (headline, subtitle, anchor, result) if value) or 3))


def _scene_text_candidates(scene: dict[str, Any]) -> list[str]:
    slots = scene.get("slots", {}) if isinstance(scene.get("slots", {}), dict) else {}
    candidates: list[str] = []
    values = [
        scene.get("narration"),
        scene.get("display_headline"),
        scene.get("visual_headline"),
        scene.get("display_subtitle"),
        scene.get("memory_anchor"),
        scene.get("save_reason"),
        scene.get("visual_object"),
        scene.get("display_conclusion"),
        scene.get("voiceover"),
    ]
    for value in values:
        text = str(value or "").strip()
        if text:
            candidates.append(text)
    for key in ("main_claim", "pain_point", "stack_title", "method_title", "workflow_result", "final_result", "framework_title", "graph_title", "center_claim", "usage_note", "proof_title", "proof_items", "final_claim", "next_step", "cta_text"):
        value = slots.get(key)
        if isinstance(value, list):
            for item in value:
                text = str(item or "").strip()
                if text:
                    candidates.append(text)
        else:
            text = str(value or "").strip()
            if text:
                candidates.append(text)
    return candidates


def _chapter_goal_for_group(chapter_family: str, representative: dict[str, Any], chapter_index: int, total: int) -> str:
    if chapter_index == 1:
        return "strong_hook"
    if chapter_family == "hook":
        return "strong_hook"
    if chapter_family == "problem":
        return "problem_statement"
    if chapter_family == "tool":
        return "process_flow"
    if chapter_family == "proof":
        return "proof_structure"
    if chapter_family == "close":
        return "closing_action" if chapter_index >= total else "closing_bridge"
    if chapter_family == "framework":
        return "structure_map"
    role = str(representative.get("role") or representative.get("scene_pack_role") or "").strip().lower()
    if role in {"cta", "offer", "verdict"}:
        return "closing_action"
    if role in {"proof", "evidence"}:
        return "proof_structure"
    if role in {"pain", "problem", "conflict"}:
        return "problem_statement"
    if role == "hook":
        return "strong_hook"
    return "bridge"


def _chapter_support_anchor(chapter_goal: str, chapter_family: str, layout_family: str) -> str:
    anchors = {
        "strong_hook": "开场钩子",
        "problem_statement": "问题定位",
        "process_flow": "流程闭环",
        "proof_structure": "证据支撑",
        "closing_action": "下一步动作",
        "closing_bridge": "收束过渡",
        "structure_map": "结构图",
        "bridge": "承上启下",
    }
    if layout_family in {"hero_metric", "hero_statement"}:
        return "主视觉"
    if layout_family in {"tool_pipeline", "config_panel", "file_tree", "process_ladder", "step_ladder", "tool_stack"}:
        return "流程支撑"
    if layout_family in {"framework_map", "proof_matrix", "comparison_board", "knowledge_graph", "concept_layers", "progress_tracker", "section_board"}:
        return "结构支撑"
    if layout_family in {"action_close", "checklist_close", "insight_close", "offer_close"}:
        return "收束动作"
    return anchors.get(chapter_goal, chapter_family or "结构支撑")


def _choose_layout_family_for_chapter(
    *,
    chapter_goal: str,
    chapter_family: str,
    representative: dict[str, Any],
    chapter_index: int,
    total_chapters: int,
    used_counts: Counter[str],
    prev_layout_family: str | None,
) -> str:
    layout_family = str(representative.get("layout_family") or "").strip()
    digits_present = _scene_has_digits(
        representative.get("display_headline"),
        representative.get("visual_headline"),
        representative.get("memory_anchor"),
        representative.get("save_reason"),
        representative.get("visual_object"),
    )
    if chapter_index == 1:
        if digits_present:
            preferred = ["hero_metric", "hero_statement", "myth_bust"]
        else:
            preferred = ["hero_statement", "myth_bust", "hero_metric"]
    elif chapter_goal == "strong_hook":
        preferred = ["hero_statement", "myth_bust", "hero_metric"]
    elif chapter_goal == "problem_statement":
        preferred = ["myth_bust", "broken_chain", "pain_card_stack", "decision_fork"]
    elif chapter_goal == "process_flow":
        preferred = ["tool_pipeline", "config_panel", "tool_stack", "process_ladder"]
    elif chapter_goal == "proof_structure":
        preferred = ["proof_matrix", "comparison_board", "knowledge_graph", "decision_fork", "section_board"]
    elif chapter_goal in {"closing_action", "closing_bridge"}:
        preferred = ["action_close", "checklist_close", "insight_close", "offer_close"]
    elif chapter_goal == "structure_map":
        preferred = ["framework_map", "proof_matrix", "comparison_board", "decision_fork", "section_board"]
    else:
        preferred = ["config_panel", "comparison_board", "section_board", "framework_map"]
    if layout_family in preferred:
        preferred = [layout_family] + [item for item in preferred if item != layout_family]
    if prev_layout_family:
        preferred = [item for item in preferred if item != prev_layout_family] + [prev_layout_family]
    max_allowed = 2
    for candidate in preferred:
        if candidate and used_counts.get(candidate, 0) < max_allowed:
            return candidate
    for candidate in preferred:
        if candidate:
            return candidate
    return layout_family or "hero_statement"


def _build_layout_box(
    *,
    layout_family: str,
    chapter_goal: str,
    chapter_index: int,
    total_chapters: int,
    primary_message: str,
    support_elements: list[str],
) -> dict[str, Any]:
    chapter_band = {
        "hero_metric": (230, 346),
        "hero_statement": (246, 332),
        "myth_bust": (258, 336),
        "tool_pipeline": (296, 262),
        "config_panel": (286, 278),
        "tool_stack": (292, 270),
        "process_ladder": (286, 276),
        "proof_matrix": (294, 286),
        "comparison_board": (292, 284),
        "framework_map": (296, 286),
        "decision_fork": (290, 280),
        "section_board": (292, 280),
        "action_close": (300, 270),
        "checklist_close": (296, 274),
        "insight_close": (296, 274),
        "offer_close": (300, 270),
    }
    main_top, main_bottom = chapter_band.get(layout_family, (286, 284))
    if chapter_index == 1:
        main_top = min(main_top, 250)
        main_bottom = max(main_bottom, 320)
    if chapter_goal in {"closing_action", "closing_bridge"}:
        main_top = max(main_top, 294)
        main_bottom = max(main_bottom, 278)
    support_top = min(1080, max(180, main_top + 112))
    support_bottom = min(1540, max(1240, 1480 - max(0, len(support_elements) - 1) * 34))
    center_y = int((main_top + (1920 - main_bottom)) / 2)
    caption_top = 1580
    header_bottom = 170
    support_cards: list[dict[str, int]] = []
    support_x = 690 if layout_family not in {"hero_metric", "hero_statement"} else 712
    support_w = 310 if layout_family not in {"hero_metric", "hero_statement"} else 286
    support_h = 160 if chapter_goal not in {"closing_action", "closing_bridge"} else 148
    for idx, _ in enumerate(support_elements[:2]):
        support_cards.append({
            "x": support_x,
            "y": int(support_top + idx * (support_h + 18)),
            "w": support_w,
            "h": support_h,
        })
    return {
        "main_top": int(main_top),
        "main_bottom": int(main_bottom),
        "support_top": int(support_top),
        "support_bottom": int(support_bottom),
        "center_y": center_y,
        "caption_top": caption_top,
        "header_bottom": header_bottom,
        "support_cards": support_cards,
    }


def _compress_elements(primary_message: str, support_candidates: list[str]) -> tuple[list[str], list[str]]:
    primary = _compact_text(primary_message, 16)
    support: list[str] = []
    duplicates: list[str] = []
    normalized_primary = re.sub(r"\s+", "", primary)
    for candidate in support_candidates:
        text = _compact_text(candidate, 24)
        if not text:
            continue
        normalized = re.sub(r"\s+", "", text)
        if not normalized or normalized == normalized_primary or normalized in normalized_primary or normalized_primary in normalized:
            duplicates.append(text)
            continue
        if any(re.sub(r"\s+", "", existing) == normalized for existing in support):
            duplicates.append(text)
            continue
        support.append(text)
        if len(support) >= 2:
            break
    return support, duplicates


def _pick_representative_scene(group: list[dict[str, Any]]) -> dict[str, Any]:
    if len(group) == 1:
        return group[0]
    family_counts = Counter(_visual_scene_family(scene) for scene in group)
    dominant_family = max(family_counts.items(), key=lambda item: (item[1], item[0]))[0]

    def score(scene: dict[str, Any], index: int) -> tuple[float, float, float, float]:
        layout_family = str(scene.get("layout_family") or "").strip()
        family = _visual_scene_family(scene)
        content_count = _chapter_content_item_count(scene)
        limit = _chapter_content_item_limit(layout_family)
        match_score = 3.0 if family == dominant_family else 0.0
        limit_score = 1.0 if content_count <= limit else -2.5
        duration_score = float(scene.get("duration", 0))
        center_bonus = -abs(index - (len(group) - 1) / 2.0) * 0.1
        return (match_score + limit_score, duration_score, center_bonus, -float(content_count))

    best_index = max(range(len(group)), key=lambda idx: score(group[idx], idx))
    return group[best_index]


def _segment_visual_chapters(
    scenes: list[dict[str, Any]],
    *,
    audio_duration: float,
) -> list[tuple[int, int]]:
    scene_count = len(scenes)
    if scene_count <= 1:
        return [(0, scene_count)]
    spec = _visual_scene_target_spec(audio_duration, scene_count)
    target_count = int(spec["target_visual_scenes"])
    if target_count >= scene_count:
        return [(index, index + 1) for index in range(scene_count)]
    min_duration = float(spec["min_visual_scene_duration"])
    preferred_duration = float(spec["preferred_visual_scene_duration"])
    max_duration = float(spec["max_visual_scenes"]) * preferred_duration if preferred_duration else audio_duration
    prefix = [0.0]
    for scene in scenes:
        prefix.append(prefix[-1] + float(scene.get("duration", 0)))

    def segment_duration(start: int, end: int) -> float:
        return round(prefix[end] - prefix[start], 3)

    def segment_cost(start: int, end: int) -> float:
        group = scenes[start:end]
        duration = segment_duration(start, end)
        families = [_visual_scene_family(scene) for scene in group]
        counts = Counter(families)
        dominant_count = max(counts.values()) if counts else 0
        dominant_ratio = dominant_count / len(group) if group else 0.0
        content_counts = [_chapter_content_item_count(scene) for scene in group]
        average_items = sum(content_counts) / len(content_counts) if content_counts else 0.0
        cost = abs(duration - preferred_duration) * 1.4
        if duration < min_duration:
            cost += (min_duration - duration) * 8.0
        if duration > max_duration:
            cost += (duration - max_duration) * 4.0
        if len(group) > 4:
            cost += (len(group) - 4) * 1.0
        if len(counts) > 2:
            cost += (len(counts) - 2) * 2.0
        if dominant_ratio < 0.6:
            cost += 1.5
        if average_items > 0:
            cost += max(0.0, average_items - 5.0) * 0.8
        if start > 0 and _visual_scene_family(scenes[start - 1]) == families[0]:
            cost += 0.35
        return round(cost, 4)

    # DP over exact chapter count so the result is stable and close to the
    # requested density range. The project is small enough that the O(n^2 * k)
    # partition search is cheap.
    inf = 10**9
    dp = [[inf] * (target_count + 1) for _ in range(scene_count + 1)]
    back: list[list[int | None]] = [[None] * (target_count + 1) for _ in range(scene_count + 1)]
    dp[0][0] = 0.0
    for end in range(1, scene_count + 1):
        for chapters in range(1, target_count + 1):
            for start in range(chapters - 1, end):
                previous = dp[start][chapters - 1]
                if previous >= inf:
                    continue
                candidate = previous + segment_cost(start, end)
                if candidate < dp[end][chapters]:
                    dp[end][chapters] = candidate
                    back[end][chapters] = start

    if dp[scene_count][target_count] >= inf:
        return [(index, index + 1) for index in range(scene_count)]

    ranges: list[tuple[int, int]] = []
    end = scene_count
    chapters = target_count
    while chapters > 0:
        start = back[end][chapters]
        if start is None:
            return [(index, index + 1) for index in range(scene_count)]
        ranges.append((start, end))
        end = start
        chapters -= 1
    ranges.reverse()
    return ranges


def _build_visual_chapters(
    *,
    storyboard_scenes: list[dict[str, Any]],
    caption_beats: list[dict[str, Any]],
    audio_duration: float,
    scene_pack_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    if not storyboard_scenes:
        return []
    if audio_duration < 30 or len(storyboard_scenes) <= 4:
        ranges = [(index, index + 1) for index in range(len(storyboard_scenes))]
    else:
        ranges = _segment_visual_chapters(storyboard_scenes, audio_duration=audio_duration)

    caption_items: list[dict[str, Any]] = []
    for caption in caption_beats:
        if not isinstance(caption, dict):
            continue
        start = float(caption.get("start", caption.get("start_time", 0)) or 0)
        end = float(caption.get("end_time", 0) or caption.get("end", 0) or (start + float(caption.get("duration", 0) or 0)))
        caption_items.append({**caption, "start_time": start, "end_time": end})

    chapters: list[dict[str, Any]] = []
    used_layout_counts: Counter[str] = Counter()
    prev_layout_family: str | None = None
    for chapter_index, (start_idx, end_idx) in enumerate(ranges, start=1):
        group = storyboard_scenes[start_idx:end_idx]
        group_family_counts = Counter(_visual_scene_family(scene) for scene in group)
        chapter_family = max(group_family_counts.items(), key=lambda item: (item[1], item[0]))[0] if group_family_counts else "other"
        representative = _pick_representative_scene(group)
        representative_id = str(representative.get("scene_id") or representative.get("id") or f"S{chapter_index:02d}")
        rep_pack = scene_pack_by_id.get(representative_id, {})
        scene_pack_compiled = bool(rep_pack)
        representative_for_layout = dict(representative)
        if rep_pack:
            representative_for_layout.update(rep_pack)
        chapter_start = float(group[0].get("start", group[0].get("start_time", 0)) or 0)
        chapter_end = float(group[-1].get("start", group[-1].get("start_time", 0)) or 0) + float(group[-1].get("duration", 0) or 0)
        chapter_duration = round(max(chapter_end - chapter_start, 0.0), 3)
        source_scene_ids = [
            str(item.get("scene_id") or item.get("id") or f"S{start_idx + offset + 1:02d}")
            for offset, item in enumerate(group)
        ]
        caption_ids = [
            str(item.get("caption_id") or "")
            for item in caption_items
            if chapter_start <= float(item.get("start_time", 0) or 0) < chapter_end
            and str(item.get("caption_id") or "").strip()
        ]
        chapter_goal = _chapter_goal_for_group(chapter_family, representative, chapter_index, len(ranges))
        layout_family = _choose_layout_family_for_chapter(
            chapter_goal=chapter_goal,
            chapter_family=chapter_family,
            representative=representative_for_layout,
            chapter_index=chapter_index,
            total_chapters=len(ranges),
            used_counts=used_layout_counts,
            prev_layout_family=prev_layout_family,
        )
        if chapter_family == "hook":
            role = "hook"
        elif chapter_family == "problem":
            role = "problem"
        elif chapter_family == "tool":
            role = "method"
        elif chapter_family == "proof":
            role = "proof"
        elif chapter_family == "close":
            role = "cta" if chapter_index >= len(ranges) else "verdict"
        else:
            role = str(representative.get("role") or representative.get("scene_pack_role") or "method").strip() or "method"
            if role in {"evidence", "result"}:
                role = "proof"
            elif role in {"explain", "method"}:
                role = "method"
            elif role == "pain":
                role = "problem"
        text_candidates = _scene_text_candidates(representative) + _scene_text_candidates(rep_pack or {})
        if chapter_index == 1:
            pref = [text for text in text_candidates if _scene_has_digits(text)] or text_candidates
        else:
            pref = text_candidates
        primary_message = _compact_text(
            pref[0] if pref else (chapter_family if chapter_family != "other" else representative.get("visual_object") or representative.get("memory_anchor") or "主视觉"),
            16,
        )
        if chapter_index == 1 and layout_family not in {"hero_metric", "hero_statement", "myth_bust"}:
            layout_family = "hero_metric" if _scene_has_digits(primary_message) else "hero_statement"
        support_source = [text for text in text_candidates[1:6] if text]
        support_elements, duplicate_elements = _compress_elements(primary_message, support_source)
        if not support_elements:
            fallback_candidates = [
                representative.get("save_reason"),
                representative.get("memory_anchor"),
                representative.get("display_subtitle"),
                representative.get("display_conclusion"),
                chapter_goal.replace("_", " "),
                chapter_family,
                "先把这一层跑通",
            ]
            normalized_primary = re.sub(r"\s+", "", primary_message)
            for candidate in fallback_candidates:
                fallback_text = _compact_text(candidate or "", 24)
                if fallback_text and re.sub(r"\s+", "", fallback_text) != normalized_primary:
                    support_elements = [fallback_text]
                    break
            if not support_elements:
                support_elements = [_chapter_support_anchor(chapter_goal, chapter_family, layout_family)]
        visual_hook = _compact_text(
            support_elements[0] if support_elements else representative.get("display_subtitle") or representative.get("save_reason") or primary_message,
            18,
        )
        visual_object = _compact_text(representative.get("visual_object") or representative.get("layout_variant") or layout_family, 16)
        memory_anchor = _compact_text(
            representative.get("memory_anchor") or primary_message or representative.get("display_subtitle") or visual_object,
            24,
        )
        save_reason_source = representative.get("save_reason") or representative.get("display_conclusion")
        if not save_reason_source and support_elements:
            save_reason_source = support_elements[0]
        if not save_reason_source:
            save_reason_source = memory_anchor
        save_reason = _compact_text(save_reason_source, 24)
        primary_elements = [primary_message] + support_elements[:1]
        content_item_count = min(6, max(1, len(primary_elements) + len(support_elements)))
        content_item_limit = _chapter_content_item_limit(layout_family)
        layout_box = _build_layout_box(
            layout_family=layout_family,
            chapter_goal=chapter_goal,
            chapter_index=chapter_index,
            total_chapters=len(ranges),
            primary_message=primary_message,
            support_elements=support_elements,
        )
        layout_variant = "compact" if chapter_goal == "closing_action" else "balanced" if layout_family in {"hero_metric", "hero_statement", "tool_pipeline"} else "wide"
        chapter_pack = dict(rep_pack or representative)
        chapter_pack.update({
            "id": f"V{chapter_index:02d}",
            "scene_id": f"V{chapter_index:02d}",
            "role": role,
            "scene_pack_role": role,
            "template_type": str((rep_pack or representative).get("template_type") or "method_steps"),
            "layout_family": layout_family,
            "layout_variant": layout_variant,
            "chapter_goal": chapter_goal,
            "primary_message": primary_message,
            "primary_elements": primary_elements,
            "support_elements": support_elements,
            "visual_hook": visual_hook,
            "layout_box": layout_box,
            "forbidden_duplicates": duplicate_elements[:2],
            "visual_object": visual_object,
            "memory_anchor": memory_anchor,
            "save_reason": save_reason,
            "display_headline": primary_message,
            "display_subtitle": support_elements[0] if support_elements else save_reason,
            "visual_headline": primary_message,
            "display_conclusion": save_reason,
            "source_scene_ids": source_scene_ids,
            "caption_ids": caption_ids,
            "source_scene_count": len(group),
            "source_scene_range": [start_idx + 1, end_idx],
            "scene_pack_compiled": scene_pack_compiled,
            "start": round(chapter_start, 3),
            "start_time": round(chapter_start, 3),
            "duration": chapter_duration,
            "end": round(chapter_end, 3),
            "end_time": round(chapter_end, 3),
            "content_item_count": content_item_count,
            "content_item_limit": content_item_limit,
            "layout_density_overflow": max(0, content_item_count - content_item_limit),
        })
        used_layout_counts[layout_family] += 1
        prev_layout_family = layout_family
        chapters.append({
            **chapter_pack,
            "scene_id": f"V{chapter_index:02d}",
            "id": f"V{chapter_index:02d}",
            "source_scene_ids": source_scene_ids,
            "caption_ids": caption_ids,
            "source_scene_count": len(group),
            "source_scene_range": [start_idx + 1, end_idx],
            "role": role,
            "scene_pack_role": role,
            "layout_family": layout_family,
            "start": round(chapter_start, 3),
            "start_time": round(chapter_start, 3),
            "duration": chapter_duration,
            "end": round(chapter_end, 3),
            "end_time": round(chapter_end, 3),
            "scene_pack_compiled": scene_pack_compiled,
            **({"scene_pack_scene": chapter_pack} if scene_pack_compiled else {}),
            "content_item_count": content_item_count,
            "content_item_limit": content_item_limit,
            "layout_density_overflow": max(0, content_item_count - content_item_limit),
        })
    return chapters


def scale_storyboard_to_audio(storyboard: dict[str, Any], audio_duration: float) -> dict[str, Any]:
    scenes = storyboard.get("scenes", [])
    if not scenes:
        return {**storyboard, "scenes": []}
    current_end = max(float(s.get("start", 0)) + float(s.get("duration", 0)) for s in scenes)
    factor = audio_duration / max(current_end, 0.001)
    scaled = []
    for index, scene in enumerate(scenes):
        start = round(float(scene.get("start", 0)) * factor, 3)
        end = audio_duration if index == len(scenes) - 1 else round(
            (float(scene.get("start", 0)) + float(scene.get("duration", 0))) * factor, 3
        )
        scaled.append({**scene, "start": start, "duration": round(end - start, 3)})
    return {
        **storyboard,
        "project": {**storyboard.get("project", {}), "duration": audio_duration, "audio_duration": audio_duration},
        "scenes": scaled,
    }


# ─── V3-P3.8 — Layer 2 anti-repetition fallback ──────────────
# When two adjacent scenes end up with the same (visual_template,
# layout_variant), mutate the scene dict in place to pick a different
# render_template from the role's rotation pool. The scene dict is the
# only source of truth: the mutation happens before director_scenes and
# scene_html are built, so the on-disk JSON and the on-screen HTML
# always reflect the same final values (plan §4.1).
#
# V3-P3.8R1: the feature gate is the project-wide
# `should_enable_v3_p38_features(design_variance)` from
# `templates.scene_protocol`. There is no separate threshold constant
# in this file — the gate is single-sourced.


def _pick_rotated_template(role: str, current: str, scene_index: int) -> str | None:
    """Return a render_template from the role's pool that differs from `current`.

    Layer 2 of V3-P3.8. Used by `_anti_repeat_rotate_scene` only.
    """
    from video_director_v3.templates.scene_protocol import (
        RENDER_TEMPLATE_POOLS,
        pick_render_template_for_role,
    )

    pool = RENDER_TEMPLATE_POOLS.get(role)
    if not pool or len(pool) < 2:
        return None
    # Walk forward from scene_index+1 to find a candidate ≠ current.
    for offset in range(1, len(pool) + 1):
        candidate = pick_render_template_for_role(role, scene_index + offset)
        if candidate and candidate != current:
            return candidate
    return None


def _anti_repeat_rotate_scene(
    scene: dict[str, Any],
    scene_index: int,
    prev_template: str | None,
    prev_variant: str | None,
) -> tuple[str | None, str | None]:
    """If `scene` would collide with the previous scene's (template, variant),
    mutate `scene` in place to a different visual_template and re-derive the
    layout variant. Returns the new (prev_template, prev_variant) for the next
    call.
    """
    current_template = scene.get("visual_template", "")
    # Compute the layout_variant that _hud_scene_config would pick for this
    # scene. We don't call _hud_scene_config twice — we look at the
    # narration-derived variant for the current template via the per-template
    # variant functions. (We use the simple narration-based detection here
    # because the goal is only to detect collision, not to render.)
    if current_template == prev_template and prev_template is not None:
        # Same template as previous — must rotate.
        role = scene.get("role", "explain")
        rotated = _pick_rotated_template(role, current_template, scene_index)
        if rotated and rotated != current_template:
            scene["visual_template"] = rotated
            current_template = rotated
    # We don't try to also re-pick the layout_variant here — the per-template
    # variant functions are content-driven and typically produce different
    # variants for different narrations. Layer 1 (storyboard_builder) and
    # the template variant functions together cover the typical case.
    return current_template, None


def build_studio_native_project(
    *,
    project_dir: Path,
    storyboard: dict[str, Any],
    narration_plan: dict[str, Any],
    tts_result: dict[str, Any],
    caption_beats: dict[str, Any],
    visual_beats: dict[str, Any],
    transitions: dict[str, Any],
    scene_pack: dict[str, Any] | None = None,
    design_variance: int = 7,
) -> dict[str, Any]:
    """Build the final HyperFrames Studio native preview project.

    This function is the **final preview source of truth** (V3-P3.8R1
    contract — see plan §4.1). It writes both `data/director_timeline.json`
    and `index.html` from the same in-memory `director_scenes` list, so
    the on-disk JSON and the on-screen HTML always agree.

    The upstream `motion_storyboard.json` (written by
    `build_motion_storyboard`) is an *initial suggestion* only — its
    `visual_template` may be rewritten here under Layer 2 fallback when
    two adjacent scenes collide. Do not read `motion_storyboard.json`
    to determine the final preview's visual_template.
    """
    timeline_dir = project_dir / "hyperframes_timeline"
    assets_dir = timeline_dir / "assets"
    data_dir = timeline_dir / "data"
    assets_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    audio_path = Path(tts_result["audio_path"])
    shutil.copy2(audio_path, assets_dir / "voiceover.mp3")
    duration = float(tts_result["real_duration"])

    source_scenes = storyboard.get("scenes", [])
    scene_pack_by_id = {
        item.get("id"): item
        for item in (scene_pack or {}).get("scenes", [])
        if item.get("id")
    }
    captions = caption_beats.get("caption_beats", [])
    visual_chapters = _build_visual_chapters(
        storyboard_scenes=source_scenes,
        caption_beats=captions,
        audio_duration=duration,
        scene_pack_by_id=scene_pack_by_id,
    )
    scene_html = []
    director_scenes = []
    prev_template: str | None = None
    prev_variant: str | None = None
    from video_director_v3.templates.scene_protocol import should_enable_v3_p38_features
    use_layer2 = should_enable_v3_p38_features(design_variance)
    for original_scene in visual_chapters:
        # V3-P3.8: deep-copy each scene so the caller's storyboard dict is
        # never mutated. Layer 2 may rewrite the visual_template on the
        # working copy; the caller's input stays pristine.
        scene = json.loads(json.dumps(original_scene)) if use_layer2 else original_scene
        sid = scene.get("scene_id", "V01")
        role = scene.get("role", "explain")
        start = float(scene.get("start", 0))
        scene_duration = max(float(scene.get("duration", 0)) - 0.001, 0)
        narration = scene.get("narration", "").strip() or role
        # V3-P3.8: Layer-2 fallback. If a scene's (template, layout_variant)
        # collides with the previous scene, rotate the visual_template in
        # place BEFORE _hud_scene_config runs, so the scene dict stays the
        # single source of truth. The build_studio_native_project caller can
        # disable this by passing design_variance < 5.
        if use_layer2:
            new_prev_t, _ = _anti_repeat_rotate_scene(
                scene, len(director_scenes), prev_template, prev_variant
            )
        contract_scene = scene.get("scene_pack_scene") if scene.get("scene_pack_compiled") else None
        if contract_scene and contract_scene.get("template_type") in _SUPPORTED_CONTRACT_TEMPLATES:
            hud_scene = _contract_hud_scene_config(
                scene=scene,
                contract_scene=contract_scene,
                is_last_scene=len(director_scenes) == len(visual_chapters) - 1,
            )
        else:
            if contract_scene:
                scene["scene_pack_scene"] = contract_scene
            hud_scene = _hud_scene_config(scene, len(director_scenes), narration)
        # V3-P3.8 P2-1: the last scene's CTA defaults to a finish-board
        # layout (end_score_goodbye) for a strong closing feel, unless the
        # narration keyword routing already picked a different CTA variant
        # (button_banner, scorecard, end_score_goodbye). Guarded by the
        # same design_variance threshold as Layer 2.
        if use_layer2 and role == "cta" and len(director_scenes) == len(visual_chapters) - 1:
            if hud_scene.get("layout_variant") not in {"button_banner", "scorecard", "end_score_goodbye"}:
                hud_scene["layout_variant"] = "end_score_goodbye"
                hud_scene.setdefault("score", "100")
                hud_scene.setdefault("score_label", "本章掌握度")
                hud_scene.setdefault("next_teaser", "下期讲：把检索真正接进 AI 流程")
        prev_template = hud_scene.get("visual_template", "")
        prev_variant = hud_scene.get("layout_variant", "")
        layout_family = str(hud_scene.get("layout_family") or "hero_statement").strip() or "hero_statement"
        caption_mode = str(hud_scene.get("caption_mode") or "standard_caption").strip() or "standard_caption"
        ending_variant = str(hud_scene.get("ending_variant") or "").strip()
        director_scenes.append({
            **hud_scene, "id": sid, "start_time": start,
            "end_time": round(start + float(scene.get("duration", 0)), 3),
        })
        # V3-P3.10A — composition class auto-pick by scene index % 3
        composition_class = _COMPOSITIONS_BY_INDEX[len(director_scenes) % 3]
        debug_visual_strategy = _scene_flag(hud_scene, "debug_visual_strategy")
        scene_html.append(f"""
<section id="scene-{escape(sid.lower())}" class="scene clip role-{escape(role)} tpl-{escape(prev_template)} hf-bg-cinematic hf-bg-{escape(role)} {composition_class} vf-visual-stage vf-layout-{escape(layout_family)} vf-caption-{escape(caption_mode)} vf-ending-{escape(ending_variant or 'none')}" style="{escape(_scene_strategy_style(hud_scene))}" data-start="{start}" data-duration="{round(scene_duration, 3)}" data-track-index="1" data-visual-template="{escape(prev_template)}" data-role="{escape(role)}" data-layout-family="{escape(layout_family)}" data-caption-mode="{escape(caption_mode)}" data-ending-variant="{escape(ending_variant)}" data-debug-visual-strategy="{str(debug_visual_strategy).lower()}">
  {get_scene_body(sid, role, hud_scene)}
  <div class="hf-vignette"></div>
  <div class="hf-hud-header"><span class="hf-hud-bar"></span><span class="hf-hud-en">{escape((hud_scene.get("hud_label_en") or role.upper() + " / HUD SYSTEM").strip())}</span><b class="hf-hud-sid">{escape(sid)}</b>{('<i class="hf-hud-zh">' + escape(hud_scene.get("hud_label_zh", "").strip()) + '</i>') if hud_scene.get("hud_label_zh", "").strip() else ""}</div>
</section>""")

    caption_html = []
    normalized_captions = []
    for item in captions:
        start = float(item.get("start", item.get("start_time", 0)))
        item_duration = float(item.get("duration", 0))
        scene_for_caption = next(
            (
                scene
                for scene in director_scenes
                if float(scene.get("start_time", 0)) <= start < float(scene.get("end_time", 0))
            ),
            director_scenes[0] if director_scenes else {},
        )
        caption_mode = str(scene_for_caption.get("caption_mode") or item.get("caption_mode") or "standard_caption").strip() or "standard_caption"
        normalized_captions.append({
            **item, "start_time": start, "end_time": round(start + item_duration, 3),
        })
        caption_html.append(
            f'<div id="caption-{escape(item.get("caption_id", "beat").lower())}" class="caption clip caption--{escape(caption_mode)}" data-start="{start}" '
            f'data-duration="{round(max(item_duration - 0.02, 0), 3)}" '
            f'data-track-index="2" data-caption-mode="{escape(caption_mode)}" data-scene-id="{escape(str(scene_for_caption.get("id") or ""))}">{escape(item.get("text", ""))}</div>'
        )

    html = f"""<!doctype html>
<html lang="zh"><head><meta charset="utf-8"><title>{escape(narration_plan.get("title", project_dir.name))}</title>
<style>
/* V3-P3.9R1 — stronger contrast, brighter text, clearer hierarchy */
:root {{
  --hf-cyan: #38E1FF;
  --hf-amber: #FFC83D;
  --hf-red: #FF5577;
  --hf-green: #2EE874;
  --hf-purple: #C77DFF;
  --hf-text: #F8FAFC;
  --hf-text-dim: rgba(248,250,252,0.78);
  --hf-muted: rgba(248,250,252,0.62);
  --hf-bg: #04060C;
  --hf-bg-deep: #02030A;
}}
*{{box-sizing:border-box}}
html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:var(--hf-bg);color:var(--hf-text);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}}
#root,.scene{{position:absolute;inset:0;overflow:hidden}}

/* Per-scene cinematic background (replaces the old flat #050812 + grid).
   Each role gets a different temperature via the .hf-bg-{role} modifier. */
.hf-bg-cinematic{{
  background:
    radial-gradient(ellipse 1200px 900px at 78% 18%, rgba(37,216,255,0.10), transparent 65%),
    radial-gradient(ellipse 1100px 800px at 18% 78%, rgba(168,85,247,0.08), transparent 60%),
    linear-gradient(180deg, #050812 0%, #0a0d1a 50%, #050812 100%);
}}
.hf-bg-hook{{background:
  radial-gradient(ellipse 1400px 1100px at 80% 12%, rgba(56,225,255,0.28), transparent 55%),
  radial-gradient(ellipse 1100px 800px at 15% 75%, rgba(255,200,61,0.18), transparent 60%),
  linear-gradient(180deg, #04060C 0%, #061a2a 50%, #04060C 100%)}}
.hf-bg-pain{{background:
  radial-gradient(ellipse 1300px 1000px at 75% 18%, rgba(255,85,119,0.24), transparent 55%),
  radial-gradient(ellipse 1100px 800px at 15% 75%, rgba(255,200,61,0.16), transparent 60%),
  linear-gradient(180deg, #100408 0%, #1a0610 50%, #04060C 100%)}}
.hf-bg-method{{background:
  radial-gradient(ellipse 1300px 1000px at 75% 18%, rgba(46,232,116,0.26), transparent 55%),
  radial-gradient(ellipse 1100px 800px at 18% 75%, rgba(56,225,255,0.16), transparent 60%),
  linear-gradient(180deg, #04060C 0%, #061a10 50%, #04060C 100%)}}
.hf-bg-evidence{{background:
  radial-gradient(ellipse 1300px 1000px at 78% 18%, rgba(255,200,61,0.26), transparent 55%),
  radial-gradient(ellipse 1100px 800px at 18% 75%, rgba(56,225,255,0.18), transparent 60%),
  linear-gradient(180deg, #04060C 0%, #1a0e08 50%, #04060C 100%)}}
.hf-bg-explain{{background:
  radial-gradient(ellipse 1300px 1000px at 78% 18%, rgba(199,125,255,0.28), transparent 55%),
  radial-gradient(ellipse 1100px 800px at 18% 75%, rgba(56,225,255,0.18), transparent 60%),
  linear-gradient(180deg, #04060C 0%, #100618 50%, #04060C 100%)}}
.hf-bg-cta{{background:
  radial-gradient(ellipse 1400px 1100px at 50% 28%, rgba(46,232,116,0.32), transparent 55%),
  radial-gradient(ellipse 1100px 800px at 50% 78%, rgba(56,225,255,0.18), transparent 60%),
  linear-gradient(180deg, #04060C 0%, #061a10 50%, #04060C 100%)}}
.hf-bg-proof, .hf-bg-input, .hf-bg-memory, .hf-bg-retrieval, .hf-bg-summary, .hf-bg-ready {{
  background: radial-gradient(ellipse 1200px 900px at 75% 18%, rgba(37,216,255,0.10), transparent 60%),
    linear-gradient(180deg, #050812 0%, #0a0d1a 50%, #050812 100%);
}}

/* Subtle film grain (CSS noise) — single low-cost SVG via data URI */
.hf-bg-cinematic::before{{
  content:"";position:absolute;inset:0;pointer-events:none;opacity:.05;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/><feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.4 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
}}

/* Vignette overlay — softer so small text stays readable */
.hf-vignette{{
  position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 120% 100% at 50% 50%, transparent 55%, rgba(0,0,0,0.32) 100%);
  z-index:1;
}}

/* V3-P3.11B — HUD header compact: smaller font, inline zh, tighter gap */
.hf-hud-header{{
  position:absolute;top:46px;left:60px;right:60px;display:flex;align-items:center;gap:12px;
  z-index:5;pointer-events:none;
}}
.hf-hud-bar{{
  display:inline-block;width:5px;height:24px;background:var(--hf-cyan);
  box-shadow:0 0 16px var(--hf-cyan);border-radius:2px;
}}
.hf-hud-en{{
  font:800 20px/1 "SF Mono","JetBrains Mono",ui-monospace,monospace;
  letter-spacing:.12em;color:#FFFFFF;text-transform:uppercase;
  text-shadow:0 0 14px rgba(56,225,255,0.7);
}}
.hf-hud-sid{{
  margin-left:auto;font:800 20px/1 "SF Mono","JetBrains Mono",ui-monospace,monospace;
  letter-spacing:.16em;color:rgba(248,250,252,0.72);
}}
/* zh sub-label rendered inline after hf-hud-en instead of absolute at top:104px */
.hf-hud-zh{{
  font:600 16px/1 "PingFang SC",sans-serif;
  letter-spacing:.12em;color:rgba(248,250,252,0.78);margin-left:4px;
}}

/* Glass panel — base for cards (deeper, brighter, stronger border) */
.hf-glass-panel{{
  background:rgba(2,4,12,0.62);
  backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
  border:1.5px solid rgba(56,225,255,0.5);
  box-shadow:0 0 48px rgba(56,225,255,0.18), inset 0 1px 0 rgba(255,255,255,0.10);
  border-radius:22px;
  position:relative;
}}
.hf-glass-panel::before, .hf-glass-panel::after{{
  content:"";position:absolute;width:22px;height:22px;border:3px solid var(--hf-cyan);
  opacity:0.85;
}}
.hf-glass-panel::before{{top:-1px;left:-1px;border-right:none;border-bottom:none;}}
.hf-glass-panel::after{{bottom:-1px;right:-1px;border-left:none;border-top:none;}}

/* Glass panel color variants — brighter borders, deeper bg, stronger glow */
.hf-glass-cyan{{border-color:rgba(56,225,255,0.7);box-shadow:0 0 48px rgba(56,225,255,0.24), inset 0 1px 0 rgba(255,255,255,0.10);}}
.hf-glass-cyan::before, .hf-glass-cyan::after{{border-color:var(--hf-cyan);}}
.hf-glass-amber{{border-color:rgba(255,200,61,0.75);box-shadow:0 0 48px rgba(255,200,61,0.24), inset 0 1px 0 rgba(255,255,255,0.10);}}
.hf-glass-amber::before, .hf-glass-amber::after{{border-color:var(--hf-amber);}}
.hf-glass-red{{border-color:rgba(255,85,119,0.75);box-shadow:0 0 48px rgba(255,85,119,0.24), inset 0 1px 0 rgba(255,255,255,0.10);}}
.hf-glass-red::before, .hf-glass-red::after{{border-color:var(--hf-red);}}
.hf-glass-green{{border-color:rgba(46,232,116,0.78);box-shadow:0 0 48px rgba(46,232,116,0.28), inset 0 1px 0 rgba(255,255,255,0.10);}}
.hf-glass-green::before, .hf-glass-green::after{{border-color:var(--hf-green);}}
.hf-glass-purple{{border-color:rgba(199,125,255,0.72);box-shadow:0 0 48px rgba(199,125,255,0.24), inset 0 1px 0 rgba(255,255,255,0.10);}}
.hf-glass-purple::before, .hf-glass-purple::after{{border-color:var(--hf-purple);}}

/* Hero typography — V3-P3.9R1: 24px hud, 56-72px sub, 120-180px super, 220-360px numbers */
.hf-big-title{{
  font-weight:900;line-height:1.05;letter-spacing:-.025em;
  font-size:clamp(72px,9vw,108px);
  color:#FFFFFF;
  text-shadow:0 6px 36px rgba(0,0,0,0.7);
  word-break:keep-all;
  overflow:visible;
  white-space:pre-line;
}}
.hf-big-title .accent{{color:var(--hf-amber);text-shadow:0 0 28px rgba(255,200,61,0.6);}}
.hf-big-title .accent-cyan{{color:var(--hf-cyan);text-shadow:0 0 28px rgba(56,225,255,0.6);}}
.hf-big-title .accent-green{{color:var(--hf-green);text-shadow:0 0 28px rgba(46,232,116,0.6);}}

.hf-sub-title{{
  font:700 28px/1.3 "PingFang SC",sans-serif;
  letter-spacing:.06em;color:var(--hf-text-dim);
  margin-top:20px;
}}

.hf-big-number{{
  font:900 320px/0.92 "SF Pro Display","Helvetica Neue",Arial,sans-serif;
  letter-spacing:-.04em;color:var(--hf-cyan);
  text-shadow:0 0 40px rgba(56,225,255,0.6);
  display:inline-block;line-height:1;
}}
.hf-big-number.amber{{color:var(--hf-amber);text-shadow:0 0 40px rgba(255,200,61,0.6);}}
.hf-big-number.green{{color:var(--hf-green);text-shadow:0 0 40px rgba(46,232,116,0.6);}}
.hf-big-number.purple{{color:var(--hf-purple);text-shadow:0 0 40px rgba(199,125,255,0.6);}}
.hf-big-number.white{{color:#FFFFFF;text-shadow:0 0 40px rgba(255,255,255,0.5);}}

.hf-step-number{{
  font:900 160px/1 "SF Pro Display","Helvetica Neue",Arial,sans-serif;
  color:var(--hf-cyan);text-shadow:0 0 28px rgba(56,225,255,0.55);
  display:inline-block;line-height:1;
}}
.hf-step-number.amber{{color:var(--hf-amber);text-shadow:0 0 28px rgba(255,200,61,0.55);}}
.hf-step-number.green{{color:var(--hf-green);text-shadow:0 0 28px rgba(46,232,116,0.55);}}

/* Status stamp badge */
.hf-status-stamp{{
  display:inline-block;padding:6px 14px;border:1.5px solid currentColor;border-radius:4px;
  font:800 14px/1 "SF Mono",ui-monospace,monospace;letter-spacing:.22em;
  text-transform:uppercase;background:rgba(6,8,16,0.7);
}}
.hf-status-live{{color:var(--hf-cyan);}}
.hf-status-viral{{color:var(--hf-amber);}}
.hf-status-pass{{color:var(--hf-green);}}
.hf-status-ready{{color:var(--hf-cyan);}}
.hf-status-risk{{color:var(--hf-red);}}

/* Metric card */
.hf-metric-card{{
  background:rgba(6,8,16,0.5);
  backdrop-filter:blur(10px);
  -webkit-backdrop-filter:blur(10px);
  border:1px solid rgba(37,216,255,0.32);
  border-radius:18px;padding:32px 28px;
  box-shadow:0 0 28px rgba(37,216,255,0.10);
  display:flex;flex-direction:column;gap:10px;
}}
.hf-metric-label{{font:600 14px/1 "SF Mono",ui-monospace,monospace;letter-spacing:.18em;
  text-transform:uppercase;color:rgba(244,247,255,0.55);}}
.hf-metric-value{{font:900 56px/1 "SF Pro Display",Arial,sans-serif;color:var(--hf-text);}}
.hf-metric-delta{{font:700 16px/1 "SF Mono",ui-monospace,monospace;}}

/* Progress bar (0→100%) */
.hf-progress{{position:relative;height:8px;background:rgba(244,247,255,0.08);border-radius:4px;overflow:hidden;}}
.hf-progress > .hf-progress-fill{{
  position:absolute;left:0;top:0;bottom:0;width:0%;
  background:linear-gradient(90deg,var(--hf-cyan),var(--hf-amber));
  box-shadow:0 0 12px var(--hf-cyan);
  animation:hf-progress-fill 1.2s cubic-bezier(.2,.7,.2,1) forwards;
}}

/* Animations */
@keyframes hf-scale-in{{0%{{transform:scale(.85);opacity:0}}100%{{transform:scale(1);opacity:1}}}}
@keyframes hf-count-up{{0%{{transform:scale(.6);opacity:0}}60%{{transform:scale(1.08);opacity:1}}100%{{transform:scale(1);opacity:1}}}}
@keyframes hf-stagger-in{{0%{{transform:translateY(20px);opacity:0}}100%{{transform:translateY(0);opacity:1}}}}
@keyframes hf-progress-fill{{0%{{width:0%}}100%{{width:var(--hf-target,100%)}}}}
@keyframes hf-stamp-pop{{0%{{transform:scale(0);opacity:0}}60%{{transform:scale(1.18);opacity:1}}100%{{transform:scale(1);opacity:1}}}}
@keyframes hf-pulse{{0%,100%{{box-shadow:0 0 28px rgba(46,213,115,.18)}}50%{{box-shadow:0 0 48px rgba(46,213,115,.42)}}}}
.hf-scale-in{{animation:hf-scale-in .6s cubic-bezier(.2,.7,.2,1) both;}}
.hf-count-up{{animation:hf-count-up .9s cubic-bezier(.2,.7,.2,1) both;}}
.hf-stagger-in{{animation:hf-stagger-in .5s cubic-bezier(.2,.7,.2,1) both;}}
.hf-stamp-pop{{animation:hf-stamp-pop .4s cubic-bezier(.2,.7,.2,1) both;}}
.hf-pulse{{animation:hf-pulse 2.4s ease-in-out infinite;}}

/* Old classes (kept so the 15 untouched templates still render) */
.bg-grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(37,216,255,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(37,216,255,.08) 1px,transparent 1px);background-size:64px 64px}}
.bg-glow{{position:absolute;width:720px;height:720px;border-radius:50%;filter:blur(36px);animation:glow 3.4s ease-in-out infinite}}
.bg-glow-1{{left:-220px;top:120px}}.bg-glow-2{{right:-240px;bottom:160px}}
.hud-frame{{position:absolute;inset:28px;border:1px solid rgba(37,216,255,.32);clip-path:polygon(0 0,100% 0,100% 94%,94% 100%,0 100%);pointer-events:none}}
.hud-top,.hud-bottom{{position:absolute;left:52px;right:52px;display:flex;justify-content:space-between;color:#25d8ff;font:800 18px/1 monospace;letter-spacing:.16em}}
.hud-top{{top:52px}}.hud-bottom{{bottom:318px}}.hud-bottom i{{font-style:normal;color:rgba(255,255,255,.55)}}

/* Caption — mode-aware, not one flat bottom strip for every scene */
.caption{{
  position:absolute;left:var(--vf-caption-left,60px);right:var(--vf-caption-right,60px);bottom:var(--vf-caption-bottom,56px);
  padding:var(--vf-caption-padding,18px 24px);
  border:1.5px solid var(--vf-caption-border,rgba(56,225,255,0.55));
  border-radius:22px;
  background:var(--vf-caption-bg,rgba(2,4,12,0.82));
  backdrop-filter:blur(16px);
  -webkit-backdrop-filter:blur(16px);
  box-shadow:0 0 42px rgba(56,225,255,0.22), inset 0 1px 0 rgba(255,255,255,0.10);
  max-width:min(1120px, calc(100% - 140px));
  font-size:var(--vf-caption-size,32px);line-height:1.22;font-weight:850;text-align:center;
  color:#FFFFFF;
  z-index:6;
}}
.caption.caption--minimal_caption{{font-size:var(--vf-caption-size,30px);letter-spacing:-.01em;opacity:.94;}}
.caption.caption--emphasis_caption{{font-size:var(--vf-caption-size,34px);border-width:2px;box-shadow:0 0 54px rgba(255,107,53,0.24), inset 0 1px 0 rgba(255,255,255,0.14);letter-spacing:-.01em;font-weight:900;}}
.caption.caption--quote_caption{{font-size:var(--vf-caption-size,32px);font-style:italic;letter-spacing:-.01em;}}
.caption.caption--action_caption{{font-size:var(--vf-caption-size,34px);text-transform:none;letter-spacing:.01em;font-weight:900;}}
.caption.caption--minimal_caption{{
  --vf-caption-left:72px;--vf-caption-right:72px;--vf-caption-bottom:56px;
  --vf-caption-padding:18px 24px;--vf-caption-size:30px;
  --vf-caption-bg:rgba(2,4,12,0.78);--vf-caption-border:rgba(255,255,255,0.20);
}}
.caption.caption--emphasis_caption{{
  --vf-caption-left:72px;--vf-caption-right:72px;--vf-caption-bottom:56px;
  --vf-caption-padding:18px 24px;--vf-caption-size:34px;
  --vf-caption-bg:rgba(255,107,53,0.14);--vf-caption-border:rgba(255,107,53,0.80);
}}
.caption.caption--quote_caption{{
  --vf-caption-left:72px;--vf-caption-right:72px;--vf-caption-bottom:56px;
  --vf-caption-padding:18px 24px;--vf-caption-size:32px;
  --vf-caption-bg:rgba(56,225,255,0.10);--vf-caption-border:rgba(56,225,255,0.66);
  font-style:italic;
}}
.caption.caption--action_caption{{
  --vf-caption-left:72px;--vf-caption-right:72px;--vf-caption-bottom:56px;
  --vf-caption-padding:18px 24px;--vf-caption-size:34px;
  --vf-caption-bg:rgba(46,232,116,0.12);--vf-caption-border:rgba(46,232,116,0.72);
  text-align:center;
}}
/* V3-P3.11B — faint gradient backing anchors subtitle area without being visible */
.caption::before{{
  content:"";position:absolute;left:-24px;right:-24px;bottom:-24px;height:160px;
  background:linear-gradient(transparent, rgba(0,0,0,0.12));
  border-radius:0 0 32px 32px;pointer-events:none;z-index:-1;
}}

/* Scene bottom safe-zone — reserves 300px so cards never occlude captions (V3-P3.11A: expanded from 280) */
.scene .hf-safe-zone{{top:var(--vf-safe-top,190px) !important;left:var(--vf-safe-left,72px) !important;right:var(--vf-safe-right,72px) !important;bottom:auto !important;padding-bottom:var(--vf-safe-bottom,300px) !important;}}
.vf-strategy-shell{{position:absolute;inset:0;pointer-events:none;}}
.vf-visual-stage{{
  position:absolute;inset:0;pointer-events:none;z-index:2;
}}
.vf-skeleton-main{{
  position:absolute;top:var(--vf-main-top,260px);left:var(--vf-main-left,72px);right:var(--vf-main-right,72px);bottom:var(--vf-main-bottom,280px);
  pointer-events:none;z-index:3;
}}
.vf-visual-center-band{{
  position:relative;display:grid;align-items:start;gap:var(--vf-center-gap,24px);
}}
.vf-support-layer{{
  position:relative;display:grid;align-content:start;gap:18px;
}}
.vf-caption-zone{{
  position:absolute;inset:0;pointer-events:none;z-index:6;
}}
.vf-glass-anchor-card{{
  position:relative;
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
}}
.vf-content-region{{
  position:absolute;inset:0;pointer-events:none;z-index:3;
}}
.scene[data-debug-visual-strategy="true"] .vf-strategy-meta{{display:block;}}
.vf-strategy-meta{{
  display:none;
  position:absolute;top:var(--vf-meta-top,120px);right:var(--vf-meta-right,72px);left:var(--vf-meta-left,auto);width:var(--vf-meta-width,280px);
  padding:18px 20px;border-radius:24px;background:rgba(2,4,12,0.72);border:1px solid rgba(56,225,255,0.24);backdrop-filter:blur(12px);
  color:#fff;z-index:4;box-shadow:0 0 24px rgba(56,225,255,0.10);
}}
.vf-strategy-tag{{font:800 16px/1.1 monospace;letter-spacing:.18em;color:rgba(248,250,252,0.55);margin-bottom:10px;}}
.vf-strategy-family{{font-size:28px;font-weight:900;line-height:1.12;color:#fff;margin-bottom:8px;}}
.vf-strategy-object{{font-size:22px;font-weight:800;color:var(--hf-cyan);margin-bottom:8px;}}
.vf-strategy-anchor{{font-size:26px;font-weight:900;color:var(--hf-amber);line-height:1.12;margin-bottom:6px;}}
.vf-strategy-save{{font-size:18px;line-height:1.42;color:rgba(248,250,252,0.74);}}
.vf-strategy-caption{{margin-top:12px;font:800 16px/1.1 monospace;letter-spacing:.16em;color:rgba(248,250,252,0.50);}}
.vf-hook-region .hf-status-stamp,
.vf-problem-region .hf-status-stamp,
.vf-proof-region .hf-status-stamp,
.vf-cta-region .hf-status-stamp{{
  box-shadow:0 0 28px rgba(56,225,255,0.12);
}}
.vf-hook-region .hf-glass-panel,
.vf-problem-region .hf-glass-panel,
.vf-proof-region .hf-glass-panel,
.vf-cta-region .hf-glass-panel{{
  backdrop-filter:blur(18px);
}}
.vf-proof-region .hf-metric-card{{
  min-width:280px;
}}
.vf-ending-board{{position:absolute;left:var(--vf-ending-left,72px);right:var(--vf-ending-right,72px);bottom:var(--vf-ending-bottom,140px);padding:22px 24px;border-radius:26px;background:rgba(2,4,12,0.78);border:1px solid rgba(255,255,255,0.12);backdrop-filter:blur(14px);z-index:5;box-shadow:0 0 28px rgba(56,225,255,0.12);}}
.vf-ending-label{{font:800 18px/1 monospace;letter-spacing:.18em;color:var(--hf-amber);margin-bottom:10px;}}
.vf-ending-title{{font-size:48px;font-weight:900;line-height:1.08;color:#fff;margin-bottom:10px;}}
.vf-ending-sub{{font-size:24px;line-height:1.42;color:rgba(248,250,252,0.76);}}
.vf-ending-cta{{font-size:38px;font-weight:900;line-height:1.12;color:var(--hf-cyan);margin-bottom:10px;}}
.vf-ending-list{{display:grid;gap:10px;margin-top:12px;}}
.vf-ending-item{{padding:12px 16px;border-radius:14px;background:rgba(255,255,255,0.06);font-size:22px;line-height:1.36;color:#fff;}}
.vf-ending-homework .vf-ending-label{{color:var(--hf-purple);}}
.vf-ending-checklist .vf-ending-label{{color:var(--hf-cyan);}}
.vf-ending-action .vf-ending-cta{{color:var(--hf-green);}}
.vf-ending-offer .vf-ending-cta{{color:var(--hf-amber);}}
.vf-ending-insight .vf-ending-title{{color:var(--hf-cyan);}}

@keyframes glow{{0%,100%{{opacity:.58;transform:scale(1)}}50%{{opacity:.92;transform:scale(1.12)}}}}

/* V3-P3.10A — Smooth scene transition compatible with native opacity toggle */
.scene {{
  transition: opacity 0.5s cubic-bezier(.2,.7,.2,1),
              transform 0.5s cubic-bezier(.2,.7,.2,1) !important;
}}

/* V3-P3.10A — Old-template overlay降级.
   让 data-motion-target="scene-bg" 变成半透明 dimming 层，
   Section 自身的 hf-bg-cinematic / hf-bg-{role} 渐变现在可见。
   不用 z-index — 模板 div 在 section 内，opacity 已能透出。 */
[data-motion-target="scene-bg"] {{
  background: rgba(2, 4, 12, 0.22) !important;
}}
[data-motion-target="scene-bg"] .bg-grid {{ opacity: 0.18 !important; }}

/* V3-P3.10A — Three light composition classes for vertical center-of-gravity. */
.hf-comp-upper  {{ padding-top: 200px; }}
.hf-comp-center {{ padding-top: 320px; }}
.hf-comp-lower  {{ padding-top: 460px; }}

/* V3-P3.11A — Per-scene entrance keyframes (CSS only, no custom JS seek).
   These fire when the section has class .hf-entering. */
@keyframes hf-scale-in {{
  0%  {{ transform: scale(.85); opacity: 0; }}
  100%{{ transform: scale(1);  opacity: 1; }}
}}
@keyframes hf-count-up {{
  0%  {{ transform: scale(.6);  opacity: 0; }}
  60% {{ transform: scale(1.08); opacity: 1; }}
  100%{{ transform: scale(1);   opacity: 1; }}
}}
@keyframes hf-stagger-in {{
  0%  {{ transform: translateY(20px); opacity: 0; }}
  100%{{ transform: translateY(0);    opacity: 1; }}
}}
@keyframes hf-progress-fill {{
  0%  {{ width: 0%; }}
  100%{{ width: var(--hf-target, 100%); }}
}}
@keyframes hf-stamp-pop {{
  0%  {{ transform: scale(0);    opacity: 0; }}
  60% {{ transform: scale(1.18); opacity: 1; }}
  100%{{ transform: scale(1);    opacity: 1; }}
}}
@keyframes hf-pulse {{
  0%, 100% {{ box-shadow: 0 0 28px rgba(46,232,116,.18); }}
  50%      {{ box-shadow: 0 0 48px rgba(46,232,116,.42); }}
}}

/* V3-P3.10A-R3 — Default VISIBLE so contact sheet / static captures
   never black out. Animation fires on .hf-entering only; if animation
   doesn't trigger, elements remain fully visible. */
.hf-animate-title,
.hf-animate-card,
.hf-animate-number,
.hf-animate-line,
.hf-animate-stamp {{
  opacity: 1;
  transform: none;
}}

.hf-entering .hf-animate-title  {{ animation: hf-scale-in      0.6s cubic-bezier(.2,.7,.2,1) both; }}
.hf-entering .hf-animate-card   {{ animation: hf-stagger-in    0.5s cubic-bezier(.2,.7,.2,1) both; }}
.hf-entering .hf-animate-number {{ animation: hf-count-up      0.9s cubic-bezier(.2,.7,.2,1) both; }}
.hf-entering .hf-animate-line   {{ animation: hf-progress-fill 1.2s cubic-bezier(.2,.7,.2,1) both; }}
.hf-entering .hf-animate-stamp  {{ animation: hf-stamp-pop     0.4s cubic-bezier(.2,.7,.2,1) both; }}

/* V3-P3.11E — shared utility components (static CSS, no JS/animation dep) */
.hf-page-anchor{{
  position:absolute;left:96px;right:96px;bottom:340px;text-align:center;
}}
.hf-page-anchor > .hf-glow-divider{{
  width:100px;height:3px;margin:0 auto 16px;
  background:linear-gradient(90deg,rgba(56,225,255,0.6),transparent);
  border-radius:2px;
}}
.hf-result-card{{
  background:rgba(6,12,22,0.68);
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
  border:1px solid rgba(80,220,255,0.35);
  border-radius:20px;
  box-shadow:0 0 30px rgba(0,220,255,0.12), inset 0 1px 0 rgba(255,255,255,0.08);
  padding:28px 36px;
}}
.hf-flow-line{{
  position:absolute;left:50%;width:3px;
  background:linear-gradient(180deg,rgba(56,225,255,0.5),rgba(56,225,255,0.05));
  transform:translateX(-50%);border-radius:2px;
}}
.hf-mini-badge{{
  display:inline-flex;padding:4px 12px;border-radius:4px;
  font:700 12px/1 "SF Mono",ui-monospace,monospace;letter-spacing:.16em;
}}
</style></head><body>
<div id="root" data-composition-id="{escape(project_dir.name)}" data-start="0" data-width="1080" data-height="1920" data-duration="{duration}">
<audio id="voiceover-audio" data-start="0" data-duration="{duration}" data-track-index="0" data-volume="1" src="assets/voiceover.mp3"></audio>
{"".join(scene_html)}
<div class="vf-caption-zone">
{"".join(caption_html)}
</div>
</div>
<script>window.__timelines = window.__timelines || {{}};</script>
</body></html>"""
    (timeline_dir / "index.html").write_text(html, encoding="utf-8")
    _write_json(data_dir / "script.json", narration_plan)
    _write_json(data_dir / "tts_result.json", tts_result)
    _write_json(data_dir / "caption_beats.json", {"duration_sec": duration, "beats": normalized_captions})
    timeline_payload = {
        "total_duration_sec": duration,
        "source_scene_count": len(source_scenes),
        "visual_chapter_count": len(director_scenes),
        "visual_chapters": director_scenes,
        "scenes": director_scenes,
    }
    _write_json(data_dir / "director_timeline.json", timeline_payload)
    _write_json(data_dir / "visual_beats.json", visual_beats)
    _write_json(data_dir / "transition_map.json", transitions)
    _write_json(timeline_dir / "meta.json", {
        "phase": "V3-P3.1-Audio-First",
        "project": project_dir.name,
        "project_id": project_dir.name,
        "entry_point": "hyperframes_timeline/index.html",
        "entry_point_path": str(timeline_dir / "index.html"),
        "canvas": {"width": 1080, "height": 1920},
        "audio_duration": duration, "scene_count": len(director_scenes), "source_scene_count": len(source_scenes), "caption_count": len(captions),
    })
    return {
        "timeline_dir": str(timeline_dir), "index": str(timeline_dir / "index.html"),
        "duration": duration, "scene_count": len(director_scenes), "source_scene_count": len(source_scenes), "caption_count": len(captions),
    }


_SUPPORTED_CONTRACT_TEMPLATES = {
    "hook",
    "problem_conflict",
    "before_after",
    "proof",
    "final_cta",
    "method_steps",
    "framework_quadrant",
    "progress_tracker",
    "tool_stack",
    "keyword_punchline",
    "myth_bust",
    "case_study_card",
    "concept_layers",
    "knowledge_graph",
    "result_summary",
}


def _contract_template_visual(template_type: str) -> tuple[str, str]:
    mapping = {
        "hook": ("hook_big_claim", "center_claim"),
        "problem_conflict": ("broken_chain", "chain_flow"),
        "before_after": ("before_after_compare", "compare_columns"),
        "proof": ("before_after_compare", "symptom_panel"),
        "final_cta": ("checklist_cta", "checklist_steps"),
        "method_steps": ("step_ladder", "ladder"),
        "framework_quadrant": ("framework_quadrant", "quadrants"),
        "progress_tracker": ("progress_tracker", "tracks"),
        "tool_stack": ("tool_stack", "stack"),
        "keyword_punchline": ("keyword_punchline", "punch"),
        "myth_bust": ("myth_bust", "myth_truth"),
        "case_study_card": ("case_study_card", "case"),
        "concept_layers": ("concept_layers", "layers"),
        "knowledge_graph": ("knowledge_graph", "graph"),
        "result_summary": ("section_board", "summary"),
    }
    return mapping.get(template_type, ("hook_big_claim", "center_claim"))


def _contract_hud_scene_config(
    *,
    scene: dict[str, Any],
    contract_scene: dict[str, Any],
    is_last_scene: bool,
) -> dict[str, Any]:
    template_type = str(contract_scene.get("template_type") or "")
    visual_template, layout_variant = _contract_template_visual(template_type)
    label_en, label_zh = HF_HUD_LABELS.get(visual_template, ("", ""))
    layout_family = str(contract_scene.get("layout_family") or "").strip()
    caption_mode = str(contract_scene.get("caption_mode") or "").strip()
    ending_variant = str(contract_scene.get("ending_variant") or "").strip()
    config = {
        **scene,
        "id": contract_scene.get("id") or scene.get("scene_id"),
        "scene_pack_role": contract_scene.get("role", scene.get("role", "method")),
        "contract_template_id": template_type,
        "contract_source": "slots_only",
        "visual_template": visual_template,
        "layout_variant": "end_score_goodbye" if template_type == "final_cta" and is_last_scene else layout_variant,
        "layout_family": layout_family or scene.get("layout_family") or layout_variant,
        "caption_mode": caption_mode or scene.get("caption_mode") or "standard_caption",
        "ending_variant": ending_variant or scene.get("ending_variant") or "",
        "display_headline": contract_scene.get("display_headline", ""),
        "display_subtitle": contract_scene.get("display_subtitle", ""),
        "visual_headline": contract_scene.get("visual_headline", ""),
        "memory_anchor": contract_scene.get("memory_anchor", ""),
        "save_reason": contract_scene.get("save_reason", ""),
        "headline": contract_scene.get("display_headline", ""),
        "subheadline": contract_scene.get("display_subtitle", ""),
        "display_conclusion": contract_scene.get("display_conclusion", ""),
        "slots": json.loads(json.dumps(contract_scene.get("slots", {}))),
        "hud_label_en": label_en or "",
        "hud_label_zh": label_zh or "",
    }
    contract, errors = require_contract_scene(config)
    config["template_contract_status"] = "FAIL" if errors else "PASS"
    config["template_contract_fallback_used"] = bool(errors)
    if contract is not None:
        config["template_contract_fallback"] = contract.fallback_template
    if errors:
        config["template_contract_errors"] = errors
    return config


# V3-P3.10A — Three light composition classes auto-picked by scene index % 3.
# Only adjusts padding-top on the section so the visual center-of-gravity
# shifts between adjacent scenes. No router / engine / role logic.
_COMPOSITIONS_BY_INDEX: list[str] = ["hf-comp-upper", "hf-comp-center", "hf-comp-lower"]


# V3-P3.9 — Per-template HUD label catalog. The 9 enhanced templates get
# rich English + Chinese labels.
# V3-P3.11A — 6 more templates get short labels, eliminating the fallback
# "ROLE / HUD SYSTEM" header for all 15 active templates.
HF_HUD_LABELS: dict[str, tuple[str, str]] = {
    "hook_big_claim":       ("LIVE TIMELINE · AI HOT",     "开场 · 第一印象"),
    "metric_dashboard":     ("DATA / DASHBOARD",           "数据 · 关键指标"),
    "case_study_card":      ("CASE / STUDY",                "真实案例 · 90 天实践"),
    "framework_quadrant":   ("FRAMEWORK / 2X2",             "四象限 · 概念分层"),
    "concept_layers":       ("LAYERS / CONCEPT",            "概念 · 底层到顶层"),
    "knowledge_graph":      ("GRAPH / NETWORK",             "知识图谱 · 节点与连接"),
    "tool_chain_three_cols":("STEP 1/3 · 流程",             "输入、链接、检索 · 闭环"),
    "step_ladder":          ("STEP 1/4 · 步骤",             "起步、串联、调用、输出"),
    "checklist_cta":        ("ACTION CLOSE · NEXT STEP",    "收束 · 下一步"),
    # V3-P3.11A — 6 unpolished templates now get short labels
    "tool_stack":           ("TOOL STACK · 3 LAYERS",      "三层工具栈"),
    "broken_chain":         ("CHAIN / BROKEN",             "断裂链路"),
    "keyword_punchline":    ("KEYWORD / PUNCH",            "关键词一击"),
    "myth_bust":            ("MYTH / BUST",                "破除迷思"),
    "progress_tracker":     ("PROGRESS / SCORE",           "进度追踪"),
    "before_after_compare":  ("BEFORE / AFTER",             "前后对比"),
    "pain_card_stack":      ("PAIN / CARD STACK",          "痛点 · 问题堆叠"),
}


def _scene_strategy_style(scene: dict[str, Any]) -> str:
    layout_family = str(scene.get("layout_family") or "hero_statement").strip() or "hero_statement"
    caption_mode = str(scene.get("caption_mode") or "standard_caption").strip() or "standard_caption"
    ending_variant = str(scene.get("ending_variant") or "").strip() or "none"
    layout_presets = {
        "hero_statement": {
            "--vf-main-top": "260px",
            "--vf-main-bottom": "300px",
            "--vf-center-gap": "24px",
            "--vf-safe-top": "150px",
            "--vf-safe-left": "72px",
            "--vf-safe-right": "72px",
            "--vf-safe-bottom": "310px",
            "--vf-meta-top": "124px",
            "--vf-meta-right": "72px",
            "--vf-meta-width": "280px",
            "--vf-ending-bottom": "180px",
            "--vf-ending-left": "72px",
            "--vf-ending-right": "72px",
        },
        "hero_metric": {
            "--vf-main-top": "286px",
            "--vf-main-bottom": "280px",
            "--vf-center-gap": "24px",
            "--vf-safe-top": "180px",
            "--vf-safe-left": "72px",
            "--vf-safe-right": "72px",
            "--vf-safe-bottom": "360px",
            "--vf-meta-top": "130px",
            "--vf-meta-left": "72px",
            "--vf-meta-width": "320px",
            "--vf-ending-bottom": "170px",
        },
        "process_ladder": {
            "--vf-main-top": "284px",
            "--vf-main-bottom": "286px",
            "--vf-center-gap": "22px",
            "--vf-safe-top": "148px",
            "--vf-safe-left": "56px",
            "--vf-safe-right": "56px",
            "--vf-safe-bottom": "322px",
            "--vf-meta-top": "112px",
            "--vf-meta-right": "72px",
            "--vf-meta-width": "260px",
            "--vf-ending-bottom": "164px",
        },
        "tool_pipeline": {
            "--vf-main-top": "292px",
            "--vf-main-bottom": "262px",
            "--vf-center-gap": "24px",
            "--vf-safe-top": "146px",
            "--vf-safe-left": "52px",
            "--vf-safe-right": "52px",
            "--vf-safe-bottom": "372px",
            "--vf-meta-top": "108px",
            "--vf-meta-left": "72px",
            "--vf-meta-width": "300px",
            "--vf-ending-bottom": "164px",
        },
        "config_panel": {
            "--vf-main-top": "286px",
            "--vf-main-bottom": "290px",
            "--vf-center-gap": "22px",
            "--vf-safe-top": "142px",
            "--vf-safe-left": "56px",
            "--vf-safe-right": "56px",
            "--vf-safe-bottom": "326px",
            "--vf-meta-top": "116px",
            "--vf-meta-right": "72px",
            "--vf-meta-width": "280px",
            "--vf-ending-bottom": "164px",
        },
        "file_tree": {
            "--vf-main-top": "286px",
            "--vf-main-bottom": "290px",
            "--vf-center-gap": "22px",
            "--vf-safe-top": "142px",
            "--vf-safe-left": "56px",
            "--vf-safe-right": "56px",
            "--vf-safe-bottom": "320px",
            "--vf-meta-top": "116px",
            "--vf-meta-left": "72px",
            "--vf-meta-width": "280px",
            "--vf-ending-bottom": "166px",
        },
        "comparison_board": {
            "--vf-main-top": "284px",
            "--vf-main-bottom": "284px",
            "--vf-center-gap": "24px",
            "--vf-safe-top": "174px",
            "--vf-safe-left": "64px",
            "--vf-safe-right": "64px",
            "--vf-safe-bottom": "314px",
            "--vf-meta-top": "122px",
            "--vf-meta-right": "72px",
            "--vf-meta-width": "286px",
            "--vf-ending-bottom": "174px",
        },
        "proof_matrix": {
            "--vf-main-top": "288px",
            "--vf-main-bottom": "290px",
            "--vf-center-gap": "24px",
            "--vf-safe-top": "174px",
            "--vf-safe-left": "64px",
            "--vf-safe-right": "64px",
            "--vf-safe-bottom": "356px",
            "--vf-meta-top": "122px",
            "--vf-meta-left": "72px",
            "--vf-meta-width": "300px",
            "--vf-ending-bottom": "174px",
        },
        "framework_map": {
            "--vf-main-top": "288px",
            "--vf-main-bottom": "290px",
            "--vf-center-gap": "24px",
            "--vf-safe-top": "160px",
            "--vf-safe-left": "64px",
            "--vf-safe-right": "64px",
            "--vf-safe-bottom": "360px",
            "--vf-meta-top": "112px",
            "--vf-meta-right": "72px",
            "--vf-meta-width": "280px",
            "--vf-ending-bottom": "170px",
        },
        "decision_fork": {
            "--vf-main-top": "286px",
            "--vf-main-bottom": "286px",
            "--vf-center-gap": "24px",
            "--vf-safe-top": "160px",
            "--vf-safe-left": "64px",
            "--vf-safe-right": "64px",
            "--vf-safe-bottom": "316px",
            "--vf-meta-top": "112px",
            "--vf-meta-left": "72px",
            "--vf-meta-width": "280px",
            "--vf-ending-bottom": "170px",
        },
        "opportunity_map": {
            "--vf-main-top": "286px",
            "--vf-main-bottom": "286px",
            "--vf-center-gap": "24px",
            "--vf-safe-top": "160px",
            "--vf-safe-left": "64px",
            "--vf-safe-right": "64px",
            "--vf-safe-bottom": "316px",
            "--vf-meta-top": "112px",
            "--vf-meta-right": "72px",
            "--vf-meta-width": "280px",
            "--vf-ending-bottom": "170px",
        },
        "action_close": {
            "--vf-main-top": "292px",
            "--vf-main-bottom": "276px",
            "--vf-center-gap": "22px",
            "--vf-safe-top": "168px",
            "--vf-safe-left": "72px",
            "--vf-safe-right": "72px",
            "--vf-safe-bottom": "356px",
            "--vf-meta-top": "116px",
            "--vf-meta-right": "72px",
            "--vf-meta-width": "270px",
            "--vf-ending-bottom": "136px",
        },
        "insight_close": {
            "--vf-main-top": "292px",
            "--vf-main-bottom": "276px",
            "--vf-center-gap": "22px",
            "--vf-safe-top": "168px",
            "--vf-safe-left": "72px",
            "--vf-safe-right": "72px",
            "--vf-safe-bottom": "356px",
            "--vf-meta-top": "116px",
            "--vf-meta-left": "72px",
            "--vf-meta-width": "270px",
            "--vf-ending-bottom": "136px",
        },
        "checklist_close": {
            "--vf-main-top": "290px",
            "--vf-main-bottom": "276px",
            "--vf-center-gap": "22px",
            "--vf-safe-top": "166px",
            "--vf-safe-left": "72px",
            "--vf-safe-right": "72px",
            "--vf-safe-bottom": "356px",
            "--vf-meta-top": "112px",
            "--vf-meta-right": "72px",
            "--vf-meta-width": "290px",
            "--vf-ending-bottom": "142px",
        },
        "offer_close": {
            "--vf-main-top": "292px",
            "--vf-main-bottom": "276px",
            "--vf-center-gap": "22px",
            "--vf-safe-top": "168px",
            "--vf-safe-left": "72px",
            "--vf-safe-right": "72px",
            "--vf-safe-bottom": "356px",
            "--vf-meta-top": "112px",
            "--vf-meta-right": "72px",
            "--vf-meta-width": "300px",
            "--vf-ending-bottom": "138px",
        },
    }
    caption_presets = {
        "standard_caption": {
            "--vf-caption-left": "54px",
            "--vf-caption-right": "54px",
            "--vf-caption-bottom": "52px",
            "--vf-caption-padding": "18px 26px",
            "--vf-caption-size": "34px",
            "--vf-caption-bg": "rgba(2,4,12,0.82)",
            "--vf-caption-border": "rgba(56,225,255,0.55)",
        },
        "minimal_caption": {
            "--vf-caption-left": "72px",
            "--vf-caption-right": "72px",
            "--vf-caption-bottom": "56px",
            "--vf-caption-padding": "16px 22px",
            "--vf-caption-size": "30px",
            "--vf-caption-bg": "rgba(2,4,12,0.74)",
            "--vf-caption-border": "rgba(56,225,255,0.38)",
        },
        "emphasis_caption": {
            "--vf-caption-left": "48px",
            "--vf-caption-right": "48px",
            "--vf-caption-bottom": "60px",
            "--vf-caption-padding": "18px 26px",
            "--vf-caption-size": "34px",
            "--vf-caption-bg": "rgba(16,24,48,0.86)",
            "--vf-caption-border": "rgba(255,107,53,0.72)",
        },
        "quote_caption": {
            "--vf-caption-left": "66px",
            "--vf-caption-right": "66px",
            "--vf-caption-bottom": "58px",
            "--vf-caption-padding": "18px 24px",
            "--vf-caption-size": "32px",
            "--vf-caption-bg": "rgba(10,16,32,0.86)",
            "--vf-caption-border": "rgba(199,125,255,0.62)",
        },
        "action_caption": {
            "--vf-caption-left": "60px",
            "--vf-caption-right": "60px",
            "--vf-caption-bottom": "52px",
            "--vf-caption-padding": "18px 24px",
            "--vf-caption-size": "32px",
            "--vf-caption-bg": "rgba(12,32,24,0.88)",
            "--vf-caption-border": "rgba(46,232,116,0.74)",
        },
    }
    style = {
        **layout_presets.get(layout_family, layout_presets["hero_statement"]),
        **caption_presets.get(caption_mode, caption_presets["standard_caption"]),
        "--vf-ending-variant": ending_variant,
    }
    layout_box = scene.get("layout_box")
    if isinstance(layout_box, dict):
        if "main_top" in layout_box:
            style["--vf-main-top"] = f"{int(layout_box['main_top'])}px"
        if "main_bottom" in layout_box:
            style["--vf-main-bottom"] = f"{int(layout_box['main_bottom'])}px"
        if "support_top" in layout_box:
            style["--vf-support-top"] = f"{int(layout_box['support_top'])}px"
        if "support_bottom" in layout_box:
            style["--vf-support-bottom"] = f"{int(layout_box['support_bottom'])}px"
        if "caption_top" in layout_box:
            style["--vf-caption-top"] = f"{int(layout_box['caption_top'])}px"
        if "header_bottom" in layout_box:
            style["--vf-safe-top"] = f"{int(layout_box['header_bottom'])}px"
    return "; ".join(f"{key}:{value}" for key, value in style.items())


def _hud_scene_config(scene: dict[str, Any], index: int, narration: str) -> dict[str, Any]:
    template = scene.get("visual_template", "hook_big_claim")
    # V3-P3.11A — headline length depends on scene role, not global 24 char truncation.
    # S01 (index 0) gets 32-38 chars as main visual title.
    # Other scenes get 12-20 char short topic keyword only (no duplicate sentence).
    if index == 0:
        headline = narration[:38]
    else:
        # Take first segment before 句号/逗号/问号, capped at 18 chars
        brief = narration.split("。")[0].split("，")[0].split("？")[0]
        headline = brief[:18] if len(brief) > 18 else brief
    config = {**scene, "visual_template": template, "headline": headline}
    contract_scene = scene.get("scene_pack_scene")
    if isinstance(contract_scene, dict):
        for key in (
            "layout_family",
            "caption_mode",
            "ending_variant",
            "display_headline",
            "display_subtitle",
            "visual_headline",
            "display_conclusion",
            "visual_object",
            "memory_anchor",
            "save_reason",
            "offer_profile_ref",
            "proof_asset_ref",
            "cta_policy_ref",
            "cta_stage",
            "cta_strength",
        ):
            value = contract_scene.get(key)
            if value not in (None, ""):
                config[key] = value
    # V3-P3.9 — inject role-aware HUD label from HF_HUD_LABELS catalog.
    # V3-P3.10A-R2 — unmatched templates get empty zh label (no fallback "OBSIDIAN SECOND BRAIN").
    label_en, label_zh = HF_HUD_LABELS.get(template, (None, None))
    if label_en is not None:
        config["hud_label_en"] = label_en
    else:
        config["hud_label_en"] = ""
    if label_zh is not None:
        config["hud_label_zh"] = label_zh
    else:
        config["hud_label_zh"] = ""
    if template == "hook_big_claim":
        config.setdefault("headline", narration[:38] or "读了很多书，为什么还是记不住？")
        config.setdefault("keyword", "记不住" if "记不住" in narration else "")
        config.setdefault("subheadline", "真正缺的不是努力，而是一个可检索的第二大脑")
        config.setdefault("layout_variant", _hook_layout_variant_from_narration(narration))
    elif template == "pain_card_stack":
        config.setdefault("headline", narration[:28] or "素材越存越多，输出反而越来越慢")
        config.setdefault("cards", _pain_cards_from_narration(narration))
        config.setdefault("conclusion", _pain_conclusion_from_narration(narration))
    elif template == "broken_chain":
        config.setdefault("headline", narration[:28] or "把知识从收藏夹，接入可检索的系统")
        config.setdefault("chain_nodes", _chain_nodes_from_narration(narration))
        config.setdefault("broken_slots", _broken_slots_from_narration(narration))
        config.setdefault("layout_variant", _broken_layout_variant_from_narration(narration, index))
        left_panel, right_panel, footer_note = _broken_panels_from_narration(narration)
        config.setdefault("left_panel", left_panel)
        config.setdefault("right_panel", right_panel)
        config.setdefault("footer_note", footer_note)
        if config["layout_variant"] == "responsibility_split":
            config.setdefault("bridge_label", "职责分工")
        if config["layout_variant"] == "binary_choice_split":
            config.setdefault("left_choice", left_panel)
            config.setdefault("right_choice", right_panel)
    elif template == "tool_chain_three_cols":
        config.setdefault("headline", narration[:30] or "输入、链接、检索，形成最小工作流")
        config.setdefault("three_cols", _three_cols_from_narration(narration))
        config["layout_variant"] = _tool_layout_variant_from_narration(narration)
    elif template == "before_after_compare":
        config.setdefault("headline", narration[:30] or "找素材，从翻遍 App 到 30 秒拿到素材包")
        config["layout_variant"] = _compare_layout_variant_from_narration(narration)
        left_items, right_items = _compare_items_from_narration(narration)
        config.setdefault("left_items", left_items)
        config.setdefault("right_items", right_items)
        config.setdefault("dashboard_metrics", _dashboard_metrics_from_narration(narration))
        config.setdefault("parallel_lanes", _parallel_lanes_from_narration(narration))
        left_panel, right_panel, summary_badge = _proof_panels_from_narration(narration)
        config.setdefault("left_panel", left_panel)
        config.setdefault("right_panel", right_panel)
        config.setdefault("summary_badge", summary_badge)
    elif template == "checklist_cta":
        config.setdefault("headline", narration[:30] or "先收藏，再跑通最小闭环")
        layout_variant = _cta_layout_variant_from_narration(narration)
        config["layout_variant"] = layout_variant
        checklist, final_message = _checklist_from_narration(narration)
        config.setdefault("checklist", checklist)
        config.setdefault("final_message", final_message)
        if layout_variant == "button_banner":
            config.setdefault("button_label", _cta_button_label_from_narration(narration))
            config.setdefault("hint", "滑动看完 → 马上动手")
        elif layout_variant == "end_score_goodbye":
            config.setdefault("score", "100")
            config.setdefault("score_label", "本章掌握度")
            config.setdefault("next_teaser", "下期讲：把检索真正接进 AI 流程")
        elif layout_variant == "scorecard":
            config.setdefault("scorecard_metrics", _cta_scorecard_metrics_from_narration(narration))
    elif template == "framework_quadrant":
        config.setdefault("headline", narration[:30] or "知识管理的四象限")
        config.setdefault("quadrants", _framework_quadrant_data_from_narration(narration))
        config.setdefault("center_label", _framework_quadrant_center_from_narration(narration))
    elif template == "decision_tree":
        config.setdefault("headline", narration[:30] or "你要不要用 Obsidian")
        config.setdefault("root_question", _decision_root_from_narration(narration))
        config.setdefault("branches", _decision_branches_from_narration(narration))
        config.setdefault("outcomes", _decision_outcomes_from_narration(narration))
    elif template == "metric_dashboard":
        config.setdefault("headline", narration[:30] or "三个月后的实际数据")
        config.setdefault("metrics", _metric_dashboard_data_from_narration(narration))
        config.setdefault("trend_caption", "持续跑通最小闭环后，看实际数字")
    elif template == "case_study_card":
        config.setdefault("headline", narration[:30] or "真实案例")
        config.setdefault("case_subject", _case_subject_from_narration(narration))
        config.setdefault("before", _case_before_from_narration(narration))
        config.setdefault("after", _case_after_from_narration(narration))
        config.setdefault("highlights", _case_highlights_from_narration(narration))
    elif template == "section_board":
        config.setdefault("headline", narration[:30] or "四个判断维度")
        config.setdefault("sections", _section_board_data_from_narration(narration))
    elif template == "comment_question":
        config.setdefault("headline", narration[:30] or "你想先跑通哪一步？")
        config.setdefault("fake_comment", _comment_question_fake_comment(narration))
        config.setdefault("guide_question", _comment_question_guide_question(narration))
    elif template == "countdown_strike":
        config.setdefault("headline", narration[:30] or "你只剩 3 天")
        config.setdefault("countdown_steps", _countdown_steps_from_narration(narration))
        config.setdefault("final_label", "GO / NOW")
    elif template == "keyword_punchline":
        kw, pl = _keyword_punchline_from_narration(narration)
        config.setdefault("keyword", kw)
        config.setdefault("punchline", pl)
    elif template == "data_dense_table":
        config.setdefault("headline", narration[:30] or "输入流汇聚状态")
        config.setdefault("rows", _data_dense_rows_from_narration(narration))
        config.setdefault("summary", "数据已结构化，等待调用")
    elif template == "step_ladder":
        config.setdefault("headline", narration[:30] or "从 0 到可用")
        config.setdefault("steps", _step_ladder_data_from_narration(narration))
        config.setdefault("top_label", "MILESTONE")
    elif template == "concept_layers":
        config.setdefault("headline", narration[:30] or "三个层次递进")
        config.setdefault("layers", _concept_layers_data_from_narration(narration))
    elif template == "progress_tracker":
        config.setdefault("headline", narration[:30] or "8 周能力曲线")
        config.setdefault("tracks", _progress_tracker_tracks_from_narration(narration))
        config.setdefault("caption", "持续跑通后，三条曲线同步进入加速段")
    elif template == "knowledge_graph":
        config.setdefault("headline", narration[:30] or "你的知识网络")
        config.setdefault("nodes", _knowledge_graph_nodes_from_narration(narration))
        config.setdefault("edges", _knowledge_graph_edges_from_narration(narration))
        config.setdefault("central_node", "N1")
    elif template == "quote_close":
        config.setdefault("quote", narration[:30] or "记住，是把素材变成自己的过程")
        config.setdefault("attribution", "— 第二大脑实践 90 天")
        config.setdefault("action", "先跑通最小闭环，评论区告诉我你的第一步")
    elif template == "myth_bust":
        config.setdefault("headline", narration[:30] or "大部分人都搞错了")
        myth, truth = _myth_bust_pair_from_narration(narration)
        config.setdefault("myth", myth)
        config.setdefault("truth", truth)
        # V3-P3.11C — alternate glass color for adjacent myth_bust scenes
        config.setdefault("color_variant", "alt" if index % 2 == 1 else "default")
    elif template == "before_after_flash":
        before_m, after_m, label = _flash_metrics_from_narration(narration)
        config.setdefault("before_metric", before_m)
        config.setdefault("after_metric", after_m)
        config.setdefault("metric_label", label)
    elif template == "timeline_pain":
        config.setdefault("headline", narration[:30] or "三个月没整理的代价")
        config.setdefault("events", _timeline_pain_events_from_narration(narration))
        config.setdefault("conclusion", "信息过载不是记不住，是没结构")
    elif template == "timeline_path":
        config.setdefault("headline", narration[:30] or "90 天建立第二大脑")
        config.setdefault("milestones", _timeline_path_milestones_from_narration(narration))
        config.setdefault("top_label", "ROADMAP")
    elif template == "tool_stack":
        config.setdefault("headline", narration[:30] or "三件套搭起来")
        config.setdefault("stack_layers", _tool_stack_layers_from_narration(narration))
    elif template == "case_study":
        config.setdefault("headline", narration[:30] or "真实案例")
        config.setdefault("case_label", _case_study_label_from_narration(narration))
        config.setdefault("metrics", _case_study_metrics_from_narration(narration))
        config.setdefault("outcome", _case_study_outcome_from_narration(narration))
    elif template == "evidence_cards":
        config.setdefault("headline", narration[:30] or "四项独立证据")
        config.setdefault("cards", _evidence_cards_data_from_narration(narration))
        config.setdefault("caption", "三个独立测试都指向同一结论")
    elif template == "score_panel":
        config.setdefault("headline", narration[:30] or "这一轮的得分")
        config.setdefault("criteria", _score_panel_criteria_from_narration(narration))
        config.setdefault("verdict", "PASS / 已可发布")
    elif template == "next_step_board":
        config.setdefault("headline", narration[:30] or "下一步你做哪一步？")
        config.setdefault("next_steps", _next_step_board_steps_from_narration(narration))
    elif template == "comment_invite":
        config.setdefault("headline", narration[:30] or "评论区告诉我")
        config.setdefault("question", _comment_invite_question_from_narration(narration))
        config.setdefault("action", "评论 / 点赞 / 收藏 / 转发")
    return config


def _pain_cards_from_narration(narration: str) -> list[dict[str, str]]:
    cards = [
        {"icon": "📚", "text": "读了很多书", "sub": "信息进脑很快"},
        {"icon": "🧠", "text": "真正要用时", "sub": "一句都想不起来"},
        {"icon": "📉", "text": "记住的很少", "sub": "能调用的更少"},
    ]
    if "100 本书" in narration:
        cards.append({"icon": "📊", "text": "读了 100 本书", "sub": "能记住不到 10 本"})
    else:
        cards.append({"icon": "🗂️", "text": "素材越积越多", "sub": "输出反而更慢"})
    return cards


def _pain_conclusion_from_narration(narration: str) -> str:
    if "想不起来" in narration:
        return "真正要输出时，脑子里还是一片空白"
    if "插件" in narration:
        return "问题不是工具不够，而是系统没有先跑通"
    return "信息收集很多，不等于需要时能拿出来用"


def _hook_layout_variant_from_narration(narration: str) -> str:
    if "你有没有" in narration or "感觉" in narration or "?" in narration:
        return "quote_punch"
    if any(token in narration for token in ("很多", "100", "999", "30h")):
        return "big_number_left"
    return "center_claim"


def _chain_nodes_from_narration(narration: str) -> list[str]:
    if "思考" in narration and "创造" in narration:
        return ["思考", "创造", "存储", "检索"]
    if "输入" in narration and "输出" in narration:
        return ["输入", "存储", "检索", "输出"]
    return ["素材", "结构", "检索", "输出"]


def _broken_slots_from_narration(narration: str) -> list[int]:
    if "负责" in narration:
        return [1]
    if "插件" in narration or "分类" in narration:
        return [0, 2]
    return [1, 2]


def _broken_layout_variant_from_narration(narration: str, scene_index: int = 0) -> str:
    if "负责" in narration or ("第二大脑" in narration and "思考" in narration):
        return "responsibility_split"
    if "别" in narration or "不要" in narration:
        return "binary_choice_split"
    # V3-P3.8: rotate through the general "explain" variants by scene
    # index so consecutive `broken_chain` scenes don't all collapse to
    # the same horizontal chain_flow layout. P2-2 added vertical_flow
    # and knowledge_triangle to publish_templates._render_broken_chain_layout.
    _DEFAULT_BROKEN_VARIANTS = ("chain_flow", "vertical_flow", "knowledge_triangle")
    return _DEFAULT_BROKEN_VARIANTS[scene_index % len(_DEFAULT_BROKEN_VARIANTS)]


def _broken_panels_from_narration(
    narration: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    if "负责" in narration or ("第二大脑" in narration and "思考" in narration):
        return (
            {
                "label": "大脑",
                "title": "思考与创造",
                "items": ["判断重点", "提出观点", "做最终决策"],
            },
            {
                "label": "第二大脑",
                "title": "存储与检索",
                "items": ["统一收纳素材", "需要时随时回查", "给 AI 稳定上下文"],
            },
            "把记忆负担迁出去，让创造力留在脑内",
        )
    if "插件" in narration or "分类" in narration or "别" in narration:
        return (
            {
                "label": "不要",
                "title": "一上来堆复杂度",
                "items": ["装太多插件", "先设计完美分类", "系统迟迟不开始工作"],
            },
            {
                "label": "先做",
                "title": "跑通最小闭环",
                "items": ["统一输入", "补上检索", "用一次真实输出验证"],
            },
            "先让系统跑起来，再决定哪里该加复杂度",
        )
    return (
        {
            "label": "断点",
            "title": "知识链条断开",
            "items": ["收集很多", "回查很慢", "输出时还得重找"],
        },
        {
            "label": "目标",
            "title": "形成可检索系统",
            "items": ["统一入口", "链接上下文", "需要时直接调用"],
        },
        "不是多一个工具，而是把链路接通。",
    )


def _three_cols_from_narration(narration: str) -> list[dict[str, str]]:
    if "输入汇聚" in narration or "进入 Obsidian" in narration:
        return [
            {"name": "微信读书", "func": "摘录同步", "icon": "RD", "detail": "高亮和笔记汇进同一库"},
            {"name": "网页剪藏", "func": "素材归档", "icon": "WEB", "detail": "文章和片段不再散落"},
            {"name": "语音视频", "func": "转写入库", "icon": "AV", "detail": "口述与视频笔记统一检索"},
        ]
    if "双向链接" in narration:
        return [
            {"name": "主题页", "func": "集中观点", "icon": "MAP", "detail": "把分散笔记挂到同一主题"},
            {"name": "双向链接", "func": "形成网络", "icon": "LINK", "detail": "相关卡片自动互相指向"},
            {"name": "关系回查", "func": "追踪上下文", "icon": "TRACE", "detail": "例子、方法、结论能串起来"},
        ]
    if "直接问 AI" in narration or "找到观点和例子" in narration:
        return [
            {"name": "自然提问", "func": "先问问题", "icon": "ASK", "detail": "按主题或场景提需求"},
            {"name": "检索笔记", "func": "定位观点", "icon": "FIND", "detail": "从个人知识库里找材料"},
            {"name": "整理输出", "func": "拼成答案", "icon": "OUT", "detail": "把观点、例子、结构拉成草稿"},
        ]
    if "第二大脑" in narration and "AI" in narration:
        return [
            {"name": "Obsidian", "func": "存储知识", "icon": "OBS", "detail": "做你的外部记忆"},
            {"name": "AI", "func": "检索整理", "icon": "AI", "detail": "把笔记转成可用素材"},
            {"name": "输出", "func": "写作复盘", "icon": "GO", "detail": "把知识重新变成作品"},
        ]
    return [
        {"name": "统一输入", "func": "汇聚素材", "icon": "IN", "detail": "读书·网页·语音·视频"},
        {"name": "双向链接", "func": "形成网络", "icon": "LINK", "detail": "相关观点自动连接"},
        {"name": "AI 检索", "func": "随问随取", "icon": "AI", "detail": "整理观点和例子"},
    ]


def _tool_layout_variant_from_narration(narration: str) -> str:
    if "输入汇聚" in narration or "进入 Obsidian" in narration:
        return "source_ingest"
    if "双向链接" in narration:
        return "knowledge_triangle"
    if "术语" in narration or "概念" in narration or "关系" in narration:
        return "matrix_glossary_wall"
    if "直接问 AI" in narration or "找到观点和例子" in narration:
        return "vertical_flow"
    if "后来" in narration or "第二大脑" in narration:
        return "intro_offset"
    return "three_col_row"


def _compare_items_from_narration(narration: str) -> tuple[list[str], list[str]]:
    if "30 秒" in narration:
        return (
            ["翻遍多个 App", "素材散在各处", "写作前先找半天"],
            ["统一入口检索", "结构先出来", "30 秒拿到素材包"],
        )
    if "你才能" in narration or "真正的创造" in narration:
        return (
            ["大脑忙着记忆", "创作被琐事挤占", "每次都从头拼"],
            ["记忆外包出去", "精力回到判断", "把时间留给创造"],
        )
    return (
        ["到处找资料", "从空白文档开始", "写一半卡住"],
        ["统一入口", "先有结构", "拿到可改草稿"],
    )


def _compare_layout_variant_from_narration(narration: str) -> str:
    if "30 秒" in narration or "素材包" in narration:
        return "dashboard_mobile"
    if "以前" in narration and "现在" in narration:
        return "parallel_lanes"
    if "你才能" in narration or "交给第二大脑" in narration:
        return "symptom_panel"
    return "compare_columns"


def _dashboard_metrics_from_narration(narration: str) -> list[dict[str, str]]:
    if "30 秒" in narration:
        return [
            {"label": "取材时间", "value": "30s"},
            {"label": "入口数量", "value": "1"},
            {"label": "素材包", "value": "READY"},
        ]
    return [
        {"label": "入口数量", "value": "1"},
        {"label": "结构状态", "value": "READY"},
        {"label": "输出速度", "value": "FAST"},
    ]


def _parallel_lanes_from_narration(narration: str) -> list[dict[str, Any]]:
    if "以前" in narration and "现在" in narration:
        return [
            {"label": "旧路径", "color": "#FF4757", "steps": ["翻找素材", "手动拼接", "从零开写"]},
            {"label": "新路径", "color": "#4D9FFF", "steps": ["直接提问", "检索笔记", "拿到素材包"]},
        ]
    return [
        {"label": "旧路径", "color": "#FF4757", "steps": ["到处找资料", "重新组织", "写一半卡住"]},
        {"label": "新路径", "color": "#4D9FFF", "steps": ["统一入口", "直接回查", "继续输出"]},
    ]


def _proof_panels_from_narration(
    narration: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    if "你才能" in narration or "交给第二大脑" in narration:
        return (
            {
                "label": "交给第二大脑",
                "title": "记忆负担下降",
                "items": ["不用强记细节", "素材随时能回查", "例子和观点更好找"],
            },
            {
                "label": "留给自己",
                "title": "创造空间上升",
                "items": ["注意力回到判断", "把精力放在表达", "真正去做创造"],
            },
            "记忆外包，不等于放弃思考；而是把大脑还给创造。",
        )
    return (
        {
            "label": "旧方式",
            "title": "信息在脑里堵住",
            "items": ["想用时找不到", "每次都从零开始"],
        },
        {
            "label": "新方式",
            "title": "知识在系统里流动",
            "items": ["需要时直接调用", "输出前先拿到结构"],
        },
        "让知识可检索，输出才会持续发生。",
    )


def _checklist_from_narration(narration: str) -> tuple[list[str], str]:
    if "最小闭环" in narration:
        return (
            ["输入统一到一个库", "把相关笔记连起来", "需要时直接问 AI"],
            "先把闭环跑通，再决定要不要加插件",
        )
    if "收藏" in narration:
        return (
            ["先收藏这套流程", "照着搭一遍最小版本", "用一次真实输出验证它"],
            "先用起来，比继续囤工具更重要",
        )
    return (
        ["统一输入到 Obsidian", "用双向链接组织笔记", "需要素材时直接问 AI"],
        "把记住外包出去，把精力留给创造",
    )


def _cta_layout_variant_from_narration(narration: str) -> str:
    """Route CTA scene to a layout variant based on sentence semantics.

    Rules:
      - Strong single action verb → button_banner (大按钮式行动号召)
      - Chapter close / 下期 / 完结 / 收束 → end_score_goodbye (大分数收束)
      - Score / 状态 / 评估 / 指标 → scorecard (多指标得分卡)
      - Else → checklist_steps (default, 3-step action)
    """
    if any(token in narration for token in ("完结", "收束", "下期", "再见", "下章", "合上", "结业", "系列")):
        return "end_score_goodbye"
    if any(token in narration for token in ("得分", "评分", "评级", "状态", "指标", "就绪", "READY", "GO", "PASS")):
        return "scorecard"
    if any(token in narration for token in ("立即", "马上", "现在", "现在就开始", "今晚", "明天", "下一步") ):
        return "button_banner"
    return "checklist_steps"


def _cta_button_label_from_narration(narration: str) -> str:
    if "最小闭环" in narration:
        return "先搭最小闭环"
    if "收藏" in narration:
        return "照着搭一遍"
    if "下一步" in narration:
        return "马上去做"
    if "跑通" in narration:
        return "立即跑一遍"
    return "开始第一步"


def _cta_scorecard_metrics_from_narration(narration: str) -> list[dict[str, str]]:
    if "最小闭环" in narration:
        return [
            {"label": "输入已统一", "value": "READY", "color": "#2ED573"},
            {"label": "检索已接入", "value": "OK", "color": "#4D9FFF"},
            {"label": "已生成草稿", "value": "GO", "color": "#FF6B35"},
        ]
    if "收藏" in narration:
        return [
            {"label": "流程已收藏", "value": "DONE", "color": "#2ED573"},
            {"label": "最小版本已搭", "value": "OK", "color": "#4D9FFF"},
            {"label": "第一次输出", "value": "GO", "color": "#FF6B35"},
        ]
    return [
        {"label": "系统就绪", "value": "READY", "color": "#2ED573"},
        {"label": "结构成立", "value": "OK", "color": "#4D9FFF"},
        {"label": "下一步", "value": "GO", "color": "#FF6B35"},
    ]


# ─── P3.3 — 6 new seed template data helpers ──────────────────────────

def _framework_quadrant_data_from_narration(narration: str) -> list[dict[str, str]]:
    if "四象限" in narration or "收集" in narration:
        return [
            {"label": "Q1 收集", "text": "微信 / 网页 / 语音", "color": "#4D9FFF"},
            {"label": "Q2 整理", "text": "双向链接 / 主题页", "color": "#2ED573"},
            {"label": "Q3 检索", "text": "直接问 AI", "color": "#FF6B35"},
            {"label": "Q4 输出", "text": "写作 / 复盘", "color": "#A855F7"},
        ]
    return [
        {"label": "Q1 输入", "text": "统一入口", "color": "#4D9FFF"},
        {"label": "Q2 结构", "text": "组织整理", "color": "#2ED573"},
        {"label": "Q3 检索", "text": "按需调用", "color": "#FF6B35"},
        {"label": "Q4 输出", "text": "持续产出", "color": "#A855F7"},
    ]


def _framework_quadrant_center_from_narration(narration: str) -> str:
    if "Obsidian" in narration:
        return "Obsidian"
    if "AI" in narration:
        return "AI"
    return "Hub"


def _decision_root_from_narration(narration: str) -> str:
    if "Obsidian" in narration:
        return "你素材 > 1000 条？"
    if "笔记" in narration:
        return "你现在有统一入口吗？"
    return "值得现在就开始吗？"


def _decision_branches_from_narration(narration: str) -> list[dict[str, str]]:
    if "Obsidian" in narration:
        return [
            {"label": "是", "leads_to": "用 Obsidian 双链管理"},
            {"label": "否", "leads_to": "先用笔记 App 足够"},
        ]
    return [
        {"label": "是", "leads_to": "先搭最小闭环"},
        {"label": "否", "leads_to": "保持现状就行"},
    ]


def _decision_outcomes_from_narration(narration: str) -> list[dict[str, str]]:
    if "Obsidian" in narration:
        return [
            {"label": "是", "text": "先搭最小闭环", "color": "#2ED573"},
            {"label": "否", "text": "先别上系统", "color": "#FF6B35"},
        ]
    return [
        {"label": "是", "text": "开始动手", "color": "#2ED573"},
        {"label": "否", "text": "继续观察", "color": "#FF6B35"},
    ]


def _metric_dashboard_data_from_narration(narration: str) -> list[dict[str, str]]:
    if "40%" in narration or "提升" in narration:
        return [
            {"label": "日均输出", "value": "3.2 篇", "delta": "+40%"},
            {"label": "素材利用率", "value": "78%", "delta": "+52%"},
            {"label": "检索响应", "value": "12s", "delta": "-65%"},
            {"label": "完播率", "value": "61%", "delta": "+18%"},
        ]
    return [
        {"label": "启动", "value": "READY", "delta": "+OK"},
        {"label": "闭环", "value": "RUN", "delta": "+OK"},
        {"label": "输出", "value": "ON", "delta": "+GO"},
        {"label": "复盘", "value": "DAILY", "delta": "+GO"},
    ]


def _case_subject_from_narration(narration: str) -> str:
    if "同学" in narration:
        return "李同学 · 知识管理 90 天"
    if "博主" in narration:
        return "某博主 · 内容生产 30 天"
    return "真实案例 · 90 天实践"


def _case_before_from_narration(narration: str) -> str:
    if "笔记" in narration or "App" in narration:
        return "笔记散 5 个 App，写一篇要 6 小时"
    if "素材" in narration:
        return "素材散在多个 App，写作前先找半天"
    return "旧流程：信息散落，输出靠人肉拼接"


def _case_after_from_narration(narration: str) -> str:
    if "笔记" in narration or "App" in narration:
        return "统一到 Obsidian + AI，1.5 小时成稿"
    if "素材" in narration:
        return "30 秒拿到素材包，输出可复用"
    return "新流程：统一入口，结构先出来"


def _case_highlights_from_narration(narration: str) -> list[str]:
    if "笔记" in narration or "App" in narration:
        return ["整理耗时下降 75%", "素材复用率 3.4×", "AI 草稿接受率 80%"]
    return ["找到素材更快", "草稿质量提升", "复盘变得简单"]


def _section_board_data_from_narration(narration: str) -> list[dict[str, str]]:
    if "维度" in narration or "判断" in narration:
        return [
            {"label": "获得感", "text": "学到至少 1 个能用的方法"},
            {"label": "收藏价值", "text": "可以复用的检查清单"},
            {"label": "评论触发", "text": "可执行的下一步动作"},
            {"label": "复看理由", "text": "信息密度足够高"},
        ]
    return [
        {"label": "内容", "text": "是否提供真实可复用的东西"},
        {"label": "节奏", "text": "前 6 秒是否命中 Hook"},
        {"label": "互动", "text": "是否有自然的评论问题"},
        {"label": "结构", "text": "分镜是否服务于信息表达"},
    ]


def _comment_question_fake_comment(narration: str) -> str:
    if "笔记" in narration or "App" in narration:
        return "“我之前用过 3 个笔记 App，最后都放弃了”"
    if "素材" in narration:
        return "“我素材都在 5 个 App，每次找半天”"
    return "“听起来很好，但真的能跑通吗？”"


def _comment_question_guide_question(narration: str) -> str:
    if "笔记" in narration or "App" in narration:
        return "你愿意先只保留一个入口吗？评论区告诉我"
    return "你打算先做哪一步？评论区说说你现在的状态"


# ─── P3.4 — 8 new seed template data helpers ──────────────────────────

def _countdown_steps_from_narration(narration: str) -> list[dict[str, str]]:
    if "笔记" in narration or "App" in narration:
        return [
            {"num": "03", "label": "选一个入口"},
            {"num": "02", "label": "把 10 条素材搬进去"},
            {"num": "01", "label": "写第一篇草稿"},
        ]
    if "素材" in narration:
        return [
            {"num": "03", "label": "统一到一处"},
            {"num": "02", "label": "标好标签"},
            {"num": "01", "label": "调出第一份"},
        ]
    return [
        {"num": "03", "label": "搭好入口"},
        {"num": "02", "label": "跑通最小"},
        {"num": "01", "label": "开始输出"},
    ]


def _keyword_punchline_from_narration(narration: str) -> tuple[str, str]:
    if "记住" in narration:
        return ("记住", narration[:30] or "不是多一个工具，而是把链路接通")
    if "创造" in narration:
        return ("创造", narration[:30] or "把精力留给真正的判断")
    if "检索" in narration:
        return ("检索", narration[:30] or "需要时直接调用，比记得更快")
    return ("重点", narration[:30] or "把链路接通，比再多一个工具更值")


def _data_dense_rows_from_narration(narration: str) -> list[dict[str, str]]:
    if "素材" in narration or "笔记" in narration:
        return [
            {"label": "微信读书笔记", "status": "SYNC", "value": "1,234"},
            {"label": "网页剪藏", "status": "SYNC", "value": "568"},
            {"label": "语音转写", "status": "PENDING", "value": "21"},
            {"label": "视频笔记", "status": "STALE", "value": "12"},
        ]
    if "AI" in narration or "工作流" in narration:
        return [
            {"label": "AI 提问入口", "status": "OK", "value": "1"},
            {"label": "笔记库", "status": "SYNC", "value": "1,892"},
            {"label": "草稿生成", "status": "READY", "value": "12"},
            {"label": "复盘面板", "status": "PENDING", "value": "0"},
        ]
    return [
        {"label": "输入流", "status": "SYNC", "value": "1,234"},
        {"label": "结构化", "status": "OK", "value": "78%"},
        {"label": "调用", "status": "READY", "value": "12"},
        {"label": "输出", "status": "PENDING", "value": "0"},
    ]


def _step_ladder_data_from_narration(narration: str) -> list[dict[str, str]]:
    if "Obsidian" in narration or "笔记" in narration:
        return [
            {"label": "1. 入口", "text": "Obsidian 库"},
            {"label": "2. 链接", "text": "双向链接"},
            {"label": "3. 检索", "text": "AI 提问"},
            {"label": "4. 输出", "text": "草稿 + 复盘"},
        ]
    if "AI" in narration:
        return [
            {"label": "1. 提需求", "text": "自然语言"},
            {"label": "2. 检索", "text": "找素材"},
            {"label": "3. 整理", "text": "拼草稿"},
            {"label": "4. 复盘", "text": "改稿子"},
        ]
    return [
        {"label": "1. 起步", "text": "建立入口"},
        {"label": "2. 串联", "text": "链接结构"},
        {"label": "3. 调用", "text": "随时提问"},
        {"label": "4. 产出", "text": "持续输出"},
    ]


def _concept_layers_data_from_narration(narration: str) -> list[dict[str, str]]:
    if "Obsidian" in narration or "AI" in narration:
        return [
            {"level": "L1", "text": "收集：素材进库"},
            {"level": "L2", "text": "结构：双向链接"},
            {"level": "L3", "text": "调用：AI 提问"},
        ]
    return [
        {"level": "L1", "text": "现象：散落"},
        {"level": "L2", "text": "结构：可检索"},
        {"level": "L3", "text": "调用：随用随取"},
    ]


def _progress_tracker_tracks_from_narration(narration: str) -> list[dict[str, Any]]:
    if "笔记" in narration or "App" in narration:
        return [
            {"label": "输入", "weeks": [20, 35, 50, 60, 70, 78, 85, 90]},
            {"label": "检索", "weeks": [10, 25, 45, 60, 72, 80, 88, 93]},
            {"label": "输出", "weeks": [5, 18, 35, 50, 62, 75, 85, 92]},
        ]
    if "完播" in narration or "效率" in narration:
        return [
            {"label": "留存", "weeks": [25, 38, 52, 65, 74, 82, 88, 92]},
            {"label": "互动", "weeks": [12, 22, 38, 50, 64, 74, 84, 90]},
            {"label": "收藏", "weeks": [8, 18, 32, 45, 58, 70, 80, 88]},
        ]
    return [
        {"label": "能力 A", "weeks": [15, 30, 45, 58, 68, 76, 84, 90]},
        {"label": "能力 B", "weeks": [10, 22, 38, 50, 62, 72, 82, 88]},
        {"label": "能力 C", "weeks": [5, 15, 30, 45, 58, 70, 80, 86]},
    ]


def _knowledge_graph_nodes_from_narration(narration: str) -> list[dict[str, Any]]:
    if "笔记" in narration or "Obsidian" in narration:
        return [
            {"id": "N1", "label": "时间管理", "x": 540, "y": 800},
            {"id": "N2", "label": "GTD", "x": 250, "y": 500},
            {"id": "N3", "label": "番茄钟", "x": 830, "y": 500},
            {"id": "N4", "label": "Obsidian", "x": 540, "y": 400},
            {"id": "N5", "label": "AI 提问", "x": 250, "y": 1100},
            {"id": "N6", "label": "写作复盘", "x": 830, "y": 1100},
        ]
    return [
        {"id": "N1", "label": "核心概念", "x": 540, "y": 800},
        {"id": "N2", "label": "方法 A", "x": 250, "y": 500},
        {"id": "N3", "label": "方法 B", "x": 830, "y": 500},
        {"id": "N4", "label": "案例 1", "x": 540, "y": 400},
        {"id": "N5", "label": "案例 2", "x": 250, "y": 1100},
        {"id": "N6", "label": "输出", "x": 830, "y": 1100},
    ]


def _knowledge_graph_edges_from_narration(narration: str) -> list[tuple[str, str]]:
    if "笔记" in narration or "Obsidian" in narration:
        return [("N1","N2"), ("N1","N3"), ("N1","N4"), ("N2","N5"), ("N3","N6"), ("N4","N5"), ("N4","N6")]
    return [("N1","N2"), ("N1","N3"), ("N2","N4"), ("N3","N4"), ("N2","N5"), ("N3","N6"), ("N4","N6")]


# ─── P3.5 — 10 new seed template data helpers ──────────────────────────

def _myth_bust_pair_from_narration(narration: str) -> tuple[str, str]:
    if "插件" in narration or "工具" in narration:
        return ("多装插件就能提高效率", "先跑通最小闭环再说")
    if "分类" in narration:
        return ("一开始就设计完美分类", "先粗糙再用，迭代优化")
    if "记笔记" in narration:
        return ("记得多就是记得好", "用得到的才算")
    return ("多就是好", "对才是好")


def _flash_metrics_from_narration(narration: str) -> tuple[str, str, str]:
    if "5h" in narration or "5 小时" in narration or "素材" in narration:
        return ("5h", "40m", "找素材时间")
    if "30 秒" in narration:
        return ("10min", "30s", "写作起步")
    if "1 周" in narration or "一周" in narration:
        return ("1 周", "2 天", "上手时间")
    return ("5h", "40m", "执行时间")


def _timeline_pain_events_from_narration(narration: str) -> list[dict[str, str]]:
    if "笔记" in narration or "App" in narration:
        return [
            {"week": "W1", "text": "笔记散 5 个 App", "severity": "LOW"},
            {"week": "W4", "text": "素材找不到", "severity": "MID"},
            {"week": "W8", "text": "怀疑记笔记的意义", "severity": "HIGH"},
            {"week": "W12", "text": "放弃，靠脑子", "severity": "CRIT"},
        ]
    return [
        {"week": "W1", "text": "开始有想法", "severity": "LOW"},
        {"week": "W4", "text": "执行力下降", "severity": "MID"},
        {"week": "W8", "text": "出现明显损耗", "severity": "HIGH"},
        {"week": "W12", "text": "复盘成本陡增", "severity": "CRIT"},
    ]


def _timeline_path_milestones_from_narration(narration: str) -> list[dict[str, str]]:
    if "Obsidian" in narration or "笔记" in narration:
        return [
            {"week": "W1-W2", "text": "统一入口"},
            {"week": "W3-W4", "text": "建结构"},
            {"week": "W5-W8", "text": "跑通检索"},
            {"week": "W9-W12", "text": "持续输出"},
        ]
    return [
        {"week": "P1", "text": "准备阶段"},
        {"week": "P2", "text": "执行阶段"},
        {"week": "P3", "text": "稳定阶段"},
        {"week": "P4", "text": "扩展阶段"},
    ]


def _tool_stack_layers_from_narration(narration: str) -> list[dict[str, str]]:
    if "Obsidian" in narration or "AI" in narration:
        return [
            {"name": "Obsidian", "role": "存储", "color": "#7C3AED"},
            {"name": "Codex", "role": "整理", "color": "#4D9FFF"},
            {"name": "Hermes", "role": "复盘", "color": "#2ED573"},
        ]
    return [
        {"name": "Layer 1", "role": "采集", "color": "#7C3AED"},
        {"name": "Layer 2", "role": "加工", "color": "#4D9FFF"},
        {"name": "Layer 3", "role": "输出", "color": "#2ED573"},
    ]


def _case_study_label_from_narration(narration: str) -> str:
    if "同学" in narration:
        return "李同学 / 设计师 / 自由职业"
    if "博主" in narration:
        return "某博主 / 5 万粉 / 自媒体"
    return "真实用户 / 90 天实践"


def _case_study_metrics_from_narration(narration: str) -> list[dict[str, str]]:
    if "笔记" in narration or "App" in narration:
        return [
            {"label": "整理耗时", "value": "-75%"},
            {"label": "素材复用", "value": "3.4×"},
            {"label": "完稿速度", "value": "+200%"},
        ]
    return [
        {"label": "效率", "value": "+60%"},
        {"label": "复用", "value": "2.5×"},
        {"label": "产出", "value": "+120%"},
    ]


def _case_study_outcome_from_narration(narration: str) -> str:
    if "笔记" in narration or "App" in narration:
        return "从 1 篇/周到 3 篇/周，质量反而更稳"
    return "持续输出变得可预期，不再靠灵感"


def _evidence_cards_data_from_narration(narration: str) -> list[dict[str, str]]:
    if "完播" in narration or "效率" in narration:
        return [
            {"label": "测试 1", "text": "素材利用率 ↑ 78%"},
            {"label": "测试 2", "text": "完播率 ↑ 61%"},
            {"label": "测试 3", "text": "复盘耗时 ↓ 65%"},
            {"label": "测试 4", "text": "草稿接受率 80%"},
        ]
    return [
        {"label": "指标 A", "text": "覆盖率 ↑ 70%"},
        {"label": "指标 B", "text": "满意度 ↑ 50%"},
        {"label": "指标 C", "text": "留存 ↑ 40%"},
        {"label": "指标 D", "text": "推荐率 ↑ 30%"},
    ]


def _score_panel_criteria_from_narration(narration: str) -> list[dict[str, Any]]:
    if "内容" in narration or "节奏" in narration:
        return [
            {"name": "内容", "score": 9, "max": 10},
            {"name": "节奏", "score": 8, "max": 10},
            {"name": "结构", "score": 9, "max": 10},
            {"name": "互动", "score": 7, "max": 10},
        ]
    return [
        {"name": "指标 A", "score": 8, "max": 10},
        {"name": "指标 B", "score": 9, "max": 10},
        {"name": "指标 C", "score": 7, "max": 10},
        {"name": "指标 D", "score": 8, "max": 10},
    ]


def _next_step_board_steps_from_narration(narration: str) -> list[dict[str, str]]:
    if "入口" in narration or "素材" in narration:
        return [
            {"label": "1", "text": "选一个入口 App"},
            {"label": "2", "text": "把 10 条素材搬进去"},
            {"label": "3", "text": "建立 3 个主题页"},
            {"label": "4", "text": "问 AI 一个真实问题"},
        ]
    return [
        {"label": "1", "text": "明确你的目标"},
        {"label": "2", "text": "拆出第一个动作"},
        {"label": "3", "text": "今天就做完"},
        {"label": "4", "text": "复盘 + 调整"},
    ]


def _comment_invite_question_from_narration(narration: str) -> str:
    if "笔记" in narration or "App" in narration:
        return "你愿意先只保留一个入口吗？"
    if "下一步" in narration:
        return "下一步你打算先做哪一步？"
    return "你有什么想分享的实践经验？"


def capture_native_review_frames(timeline_dir: Path, frames: int = 7) -> dict[str, Any]:
    meta = json.loads((timeline_dir / "meta.json").read_text(encoding="utf-8"))
    duration = float(meta["audio_duration"])
    timestamps = [round(0.5 + index * max(duration - 1.0, 0) / max(frames - 1, 1), 3) for index in range(frames)]
    snapshots_dir = timeline_dir / "snapshots"
    if snapshots_dir.exists():
        shutil.rmtree(snapshots_dir)
    result = subprocess.run(
        ["npx", "hyperframes", "snapshot", str(timeline_dir), "--at", ",".join(map(str, timestamps)), "--describe", "false"],
        capture_output=True, text=True, timeout=180,
    )
    pngs = sorted(snapshots_dir.glob("frame-*.png"))
    review_frames_dir = timeline_dir.parent / "review_frames"
    review_frames_dir.mkdir(parents=True, exist_ok=True)
    for old_frame in review_frames_dir.glob("*"):
        if old_frame.is_file():
            old_frame.unlink()
    for snapshot in pngs:
        shutil.copy2(snapshot, review_frames_dir / snapshot.name)
    contact_sheet = snapshots_dir / "contact-sheet.jpg"
    if contact_sheet.exists():
        shutil.copy2(contact_sheet, review_frames_dir / contact_sheet.name)
    return {
        "status": "PASS" if result.returncode == 0 and len(pngs) >= frames else "FAIL",
        "ok_count": len(pngs), "snapshots_dir": str(snapshots_dir),
        "review_frames_dir": str(review_frames_dir),
        "stdout": result.stdout[-1000:], "stderr": result.stderr[-1000:],
    }
