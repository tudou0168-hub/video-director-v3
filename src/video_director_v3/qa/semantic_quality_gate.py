"""Semantic quality gate for contract-driven preview validation."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PROOF_TEMPLATES = {"proof", "progress_tracker", "case_study_card", "knowledge_graph"}


def build_semantic_quality_report(
    *,
    project_dir: Path,
    scene_pack: dict[str, Any] | None,
    review_frames_data: dict[str, Any] | None,
    stage_status: dict[str, str],
) -> dict[str, Any]:
    scene_pack = scene_pack or {"scenes": [], "lint": {}}
    scenes = scene_pack.get("scenes", [])
    timeline_path = project_dir / "hyperframes_timeline" / "data" / "director_timeline.json"
    director_scenes = []
    if timeline_path.exists():
        director_scenes = json.loads(timeline_path.read_text(encoding="utf-8")).get("scenes", [])
    by_id = {scene.get("id"): scene for scene in director_scenes}

    contract_errors = list(scene_pack.get("lint", {}).get("contract_errors", []))
    slot_missing_count = sum(1 for item in contract_errors if "missing required slot" in item)
    placeholder_count = sum(1 for item in contract_errors if "placeholder/empty" in item)
    role_template_mismatch_count = sum(1 for item in contract_errors if "not compatible" in item)
    fallback_count = sum(1 for item in director_scenes if item.get("template_contract_fallback_used"))
    raw_text_dependency_count = sum(
        1
        for item in director_scenes
        if item.get("contract_template_id") and item.get("contract_source") != "slots_only"
    )
    cta_scene_count = sum(1 for scene in scenes if scene.get("role") == "cta" or scene.get("template_type") == "final_cta")
    proof_scene_count = sum(1 for scene in scenes if scene.get("role") == "proof" or scene.get("template_type") in PROOF_TEMPLATES)
    chinese_dominance_score = round(_chinese_dominance_score(scenes), 3)

    per_scene_scores = []
    for scene in scenes:
        score, issues = _scene_quality_score(scene, by_id.get(scene.get("id")))
        per_scene_scores.append({
            "id": scene.get("id"),
            "template_type": scene.get("template_type"),
            "score": round(score, 3),
            "issues": issues,
        })
    worst_3_scenes = sorted(per_scene_scores, key=lambda item: item["score"])[:3]

    contact_sheet_exists = (project_dir / "review_frames" / "contact-sheet.jpg").exists()
    total_scenes = len(scenes)
    fallback_ratio = fallback_count / total_scenes if total_scenes else 1.0

    hard_fail_reasons: list[str] = []
    if placeholder_count > 0:
        hard_fail_reasons.append("placeholder_count > 0")
    if raw_text_dependency_count > 0:
        hard_fail_reasons.append("raw_text_dependency_count > 0")
    if slot_missing_count > 0:
        hard_fail_reasons.append("required slot missing without fallback")
    if cta_scene_count == 0:
        hard_fail_reasons.append("cta_scene_count = 0")
    if proof_scene_count == 0:
        hard_fail_reasons.append("proof_scene_count = 0")
    if fallback_ratio > 0.3:
        hard_fail_reasons.append("fallback_count > 30%")
    if chinese_dominance_score < 0.55:
        hard_fail_reasons.append("Chinese dominance too low")
    if role_template_mismatch_count > 0:
        hard_fail_reasons.append("role/template contract mismatch")
    if not contact_sheet_exists:
        hard_fail_reasons.append("contact sheet missing")
    if stage_status.get("studio_native_preview") != "PASS" or (review_frames_data or {}).get("status") != "PASS":
        hard_fail_reasons.append("preview not READY")

    semantic_quality_score = _overall_quality_score(
        total_scenes=total_scenes,
        fallback_ratio=fallback_ratio,
        placeholder_count=placeholder_count,
        raw_text_dependency_count=raw_text_dependency_count,
        role_template_mismatch_count=role_template_mismatch_count,
        chinese_dominance_score=chinese_dominance_score,
        worst_scene_score=worst_3_scenes[0]["score"] if worst_3_scenes else 0.0,
    )

    return {
        "status": "PASS" if not hard_fail_reasons else "FAIL",
        "total_scenes": total_scenes,
        "contract_templates_used": sorted({scene.get("template_type") for scene in scenes if scene.get("template_type")}),
        "fallback_count": fallback_count,
        "slot_missing_count": slot_missing_count,
        "placeholder_count": placeholder_count,
        "raw_text_dependency_count": raw_text_dependency_count,
        "role_template_mismatch_count": role_template_mismatch_count,
        "cta_scene_count": cta_scene_count,
        "proof_scene_count": proof_scene_count,
        "chinese_dominance_score": chinese_dominance_score,
        "semantic_quality_score": semantic_quality_score,
        "worst_3_scenes": worst_3_scenes,
        "hard_fail_reasons": hard_fail_reasons,
        "contact_sheet_exists": contact_sheet_exists,
        "scene_pack_status": scene_pack.get("lint", {}).get("scene_pack_status", "UNKNOWN"),
        "template_contracts_status": scene_pack.get("lint", {}).get("template_contracts_status", "UNKNOWN"),
    }


def _scene_quality_score(scene: dict[str, Any], director_scene: dict[str, Any] | None) -> tuple[float, list[str]]:
    semantic_score = scene.get("semantic_score", {})
    issues: list[str] = []
    score = 1.0
    role_match = float(semantic_score.get("role_match", 0.5))
    completeness = float(semantic_score.get("slot_completeness", 0.5))
    readability_risk = float(semantic_score.get("visual_readability_risk", 0.5))
    score *= (0.55 + role_match * 0.25 + completeness * 0.20)
    score -= readability_risk * 0.25
    if director_scene and director_scene.get("template_contract_fallback_used"):
        issues.append("fallback_used")
        score -= 0.35
    if director_scene and director_scene.get("template_contract_status") != "PASS":
        issues.append("contract_not_pass")
        score -= 0.25
    if _has_placeholder(scene.get("slots", {})):
        issues.append("placeholder")
        score -= 0.4
    return max(score, 0.0), issues


def _has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip() in {"TODO", "placeholder", "待补充", "N/A", ""}
    if isinstance(value, list):
        return any(_has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_has_placeholder(item) for item in value.values())
    return False


def _chinese_dominance_score(scenes: list[dict[str, Any]]) -> float:
    chinese = 0
    visible = 0
    for scene in scenes:
        blob = " ".join(_slot_strings(scene.get("slots", {})))
        for ch in blob:
            if re.match(r"[\u4e00-\u9fff]", ch):
                chinese += 1
                visible += 1
            elif ch.isascii() and ch.isalpha():
                visible += 1
    return chinese / visible if visible else 1.0


def _slot_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_slot_strings(item))
        return result
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(_slot_strings(item))
        return result
    return [str(value)]


def _overall_quality_score(
    *,
    total_scenes: int,
    fallback_ratio: float,
    placeholder_count: int,
    raw_text_dependency_count: int,
    role_template_mismatch_count: int,
    chinese_dominance_score: float,
    worst_scene_score: float,
) -> float:
    score = 100.0
    score -= fallback_ratio * 25.0
    score -= placeholder_count * 20.0
    score -= raw_text_dependency_count * 25.0
    score -= role_template_mismatch_count * 20.0
    score -= max(0.0, 0.65 - chinese_dominance_score) * 40.0
    score -= max(0.0, 0.6 - worst_scene_score) * 30.0
    score += min(total_scenes, 12) * 0.5
    return round(max(score, 0.0), 2)
