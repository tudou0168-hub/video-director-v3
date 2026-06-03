"""Semantic quality gate for contract-driven preview validation."""
from __future__ import annotations

import json
import re
from pathlib import Path
from statistics import mean
from typing import Any


CTA_TEMPLATE_HINTS = {
    "button_banner",
    "checklist_cta",
    "end_score_goodbye",
    "final_cta",
    "scorecard",
}
PROOF_TEMPLATES = {"proof", "progress_tracker", "case_study_card", "knowledge_graph"}
GENERIC_PROOF_PHRASES = {
    "真实案例",
    "已验证",
    "可复用",
    "经验",
    "结果看得见",
    "已经跑通",
    "已经跑通过",
    "案例",
    "实例",
}
CONCRETE_PROOF_MARKERS = {
    "截图",
    "日志",
    "记录",
    "前后",
    "对比",
    "来源",
    "步骤",
    "场景",
    "过程",
    "时间",
    "分钟",
    "小时",
    "天",
    "周",
    "%",
    "S01",
    "S02",
    "S03",
    "S04",
    "S05",
    "S06",
    "S07",
    "S08",
    "S09",
    "S10",
    "S11",
    "S12",
    "S13",
    "S14",
}
WEAK_HOOK_GENERIC_PHRASES = {
    "开始",
    "流程",
    "方法",
    "总结",
    "第一步",
    "第二步",
    "下一步",
    "现在开始",
    "先跑一遍",
    "先跑通",
    "先做一版",
    "先把",
}
WEAK_HOOK_STRONG_MARKERS = {
    "为什么",
    "你有没有",
    "很多人",
    "不是",
    "而是",
    "真正",
    "结果",
    "但是",
    "但",
    "怎么办",
    "怎么",
}


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
        try:
            director_scenes = json.loads(timeline_path.read_text(encoding="utf-8")).get("scenes", [])
        except Exception:
            director_scenes = []

    merged_scenes = _merge_scene_views(scenes, director_scenes)
    director_by_id = {scene.get("id"): scene for scene in director_scenes}

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
    cta_info = _analyze_cta_distribution(merged_scenes)
    proof_info = _analyze_proof_strength(merged_scenes)
    repetition_info = _analyze_scene_repetition(merged_scenes)
    hook_info = _analyze_hook_strength(merged_scenes)
    chinese_dominance_score = round(_chinese_dominance_score(merged_scenes), 3)

    per_scene_scores = []
    for index, scene in enumerate(merged_scenes):
        score, issues, structural_risks = _scene_quality_score(
            scene,
            director_by_id.get(scene.get("id")),
            index=index,
            total_scenes=len(merged_scenes),
            cta_info=cta_info,
            proof_info=proof_info,
            repetition_info=repetition_info,
            hook_info=hook_info,
        )
        per_scene_scores.append(
            {
                "id": scene.get("id"),
                "template_type": scene.get("template_type"),
                "score": round(score, 3),
                "issues": issues,
                "structural_risks": structural_risks,
            }
        )

    worst_3_scenes = sorted(per_scene_scores, key=lambda item: item["score"])[:3]

    contact_sheet_exists = (project_dir / "review_frames" / "contact-sheet.jpg").exists()
    total_scenes = len(merged_scenes)
    fallback_ratio = fallback_count / total_scenes if total_scenes else 1.0
    worst_scene_score = worst_3_scenes[0]["score"] if worst_3_scenes else 0.0

    hard_fail_reasons: list[str] = []
    if placeholder_count > 0:
        hard_fail_reasons.append("placeholder_count > 0")
    if raw_text_dependency_count > 0:
        hard_fail_reasons.append("raw_text_dependency_count > 0")
    if slot_missing_count > 0:
        hard_fail_reasons.append("required slot missing without fallback")
    if cta_info["cta_scene_count"] == 0:
        hard_fail_reasons.append("cta_scene_count = 0")
    if proof_info["proof_scene_count"] == 0:
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

    average_scene_score = mean(item["score"] for item in per_scene_scores) if per_scene_scores else 0.0
    semantic_quality_score = _overall_quality_score(
        average_scene_score=average_scene_score,
        fallback_ratio=fallback_ratio,
        placeholder_count=placeholder_count,
        raw_text_dependency_count=raw_text_dependency_count,
        role_template_mismatch_count=role_template_mismatch_count,
        chinese_dominance_score=chinese_dominance_score,
        worst_scene_score=worst_scene_score,
        cta_distribution_risk=cta_info["cta_distribution_risk"],
        proof_strength_risk=proof_info["proof_strength_risk"],
        scene_repetition_risk=repetition_info["repetition_risk"],
        hook_strength_risk=hook_info["hook_strength_risk"],
    )

    gate_status = "FAIL" if hard_fail_reasons else "PASS"
    score_band = "FAIL" if hard_fail_reasons else _score_band(semantic_quality_score)
    publish_candidate_readiness = _publish_candidate_readiness(
        gate_status=gate_status,
        semantic_quality_score=semantic_quality_score,
        cta_distribution_risk=cta_info["cta_distribution_risk"],
        proof_strength_risk=proof_info["proof_strength_risk"],
        worst_scene_score=worst_scene_score,
        fallback_count=fallback_count,
        raw_text_dependency_count=raw_text_dependency_count,
        placeholder_count=placeholder_count,
        role_template_mismatch_count=role_template_mismatch_count,
    )

    preview_ready = (
        stage_status.get("studio_native_preview") == "PASS"
        and (review_frames_data or {}).get("status") == "PASS"
        and contact_sheet_exists
        and not hard_fail_reasons
    )

    return {
        "status": gate_status,
        "gate_status": gate_status,
        "preview_status": "READY" if preview_ready else "FAILED",
        "can_approve_preview": preview_ready,
        "score_band": score_band,
        "publish_candidate_readiness": publish_candidate_readiness,
        "total_scenes": total_scenes,
        "contract_templates_used": sorted({scene.get("template_type") for scene in merged_scenes if scene.get("template_type")}),
        "fallback_count": fallback_count,
        "slot_missing_count": slot_missing_count,
        "placeholder_count": placeholder_count,
        "raw_text_dependency_count": raw_text_dependency_count,
        "role_template_mismatch_count": role_template_mismatch_count,
        "cta_scene_count": cta_info["cta_scene_count"],
        "proof_scene_count": proof_info["proof_scene_count"],
        "chinese_dominance_score": chinese_dominance_score,
        "semantic_quality_score": semantic_quality_score,
        "cta_distribution": cta_info,
        "proof_strength": proof_info,
        "scene_repetition": repetition_info,
        "hook_strength": hook_info,
        "worst_3_scenes": worst_3_scenes,
        "hard_fail_reasons": hard_fail_reasons,
        "contact_sheet_exists": contact_sheet_exists,
        "scene_pack_status": scene_pack.get("lint", {}).get("scene_pack_status", "UNKNOWN"),
        "template_contracts_status": scene_pack.get("lint", {}).get("template_contracts_status", "UNKNOWN"),
    }


def _merge_scene_views(
    scenes: list[dict[str, Any]],
    director_scenes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {scene.get("id"): scene for scene in director_scenes}
    merged: list[dict[str, Any]] = []
    for scene in scenes:
        combined = dict(by_id.get(scene.get("id"), {}))
        combined.update(scene)
        merged.append(combined)
    return merged


def _analyze_cta_distribution(scenes: list[dict[str, Any]]) -> dict[str, Any]:
    cta_indices = [(index, scene) for index, scene in enumerate(scenes) if _is_cta_scene(scene)]
    cta_scene_ids = [scene.get("id") for _, scene in cta_indices if scene.get("id")]
    total_scenes = len(scenes)
    early_threshold = max(1, int(total_scenes * 0.3)) if total_scenes >= 8 else 0
    early_cta_indices = [index for index, _ in cta_indices if early_threshold and index < early_threshold]
    early_cta_ids = [scene.get("id") for index, scene in cta_indices if early_threshold and index < early_threshold and scene.get("id")]
    repeated_cta_ids = [scene.get("id") for i, (_, scene) in enumerate(cta_indices) if i > 0 and scene.get("id")]
    repeated_cta_count = max(0, len(cta_indices) - 1)

    if len(cta_indices) >= 4 or len(early_cta_indices) >= 2:
        risk = "high"
    elif len(cta_indices) >= 3 or len(early_cta_indices) > 0:
        risk = "medium"
    elif len(cta_indices) >= 2:
        risk = "medium"
    else:
        risk = "low"

    return {
        "cta_scene_count": len(cta_indices),
        "cta_scene_ids": cta_scene_ids,
        "early_cta_count": len(early_cta_indices),
        "early_cta_ids": early_cta_ids,
        "repeated_cta_count": repeated_cta_count,
        "repeated_cta_ids": repeated_cta_ids,
        "cta_distribution_risk": risk,
    }


def _analyze_proof_strength(scenes: list[dict[str, Any]]) -> dict[str, Any]:
    proof_indices = [(index, scene) for index, scene in enumerate(scenes) if _is_proof_scene(scene)]
    proof_scene_ids = [scene.get("id") for _, scene in proof_indices if scene.get("id")]
    abstract_proof_ids: list[str] = []
    for _, scene in proof_indices:
        blob = " ".join(_slot_strings(scene.get("slots", {})))
        if _is_abstract_proof(blob):
            if scene.get("id"):
                abstract_proof_ids.append(scene["id"])

    abstract_proof_count = len(abstract_proof_ids)
    if not proof_indices:
        risk = "high"
    elif abstract_proof_count >= len(proof_indices):
        risk = "high"
    elif abstract_proof_count > 0 or len(proof_indices) >= 2:
        risk = "medium"
    else:
        risk = "low"

    return {
        "proof_scene_count": len(proof_indices),
        "proof_scene_ids": proof_scene_ids,
        "abstract_proof_count": abstract_proof_count,
        "abstract_proof_ids": abstract_proof_ids,
        "proof_strength_risk": risk,
    }


def _analyze_scene_repetition(scenes: list[dict[str, Any]]) -> dict[str, Any]:
    repeated_template_runs = 0
    repeated_role_runs = 0
    repeated_template_ids: list[str] = []
    repeated_role_ids: list[str] = []
    template_run: list[dict[str, Any]] = []
    role_run: list[dict[str, Any]] = []
    template_risk = "low"
    role_risk = "low"

    def flush_template_run(run: list[dict[str, Any]]) -> None:
        nonlocal repeated_template_runs, template_risk
        if len(run) >= 2:
            repeated_template_runs += len(run) - 1
            repeated_template_ids.extend(scene.get("id") for scene in run if scene.get("id"))
            template_risk = "high" if len(run) >= 3 else max_risk(template_risk, "medium")

    def flush_role_run(run: list[dict[str, Any]]) -> None:
        nonlocal repeated_role_runs, role_risk
        if len(run) >= 2:
            repeated_role_runs += len(run) - 1
            repeated_role_ids.extend(scene.get("id") for scene in run if scene.get("id"))
            role_risk = "high" if len(run) >= 3 else max_risk(role_risk, "medium")

    for scene in scenes:
        if not template_run:
            template_run = [scene]
        elif _normalized_template(scene) == _normalized_template(template_run[-1]):
            template_run.append(scene)
        else:
            flush_template_run(template_run)
            template_run = [scene]

        if not role_run:
            role_run = [scene]
        elif _normalized_role(scene) == _normalized_role(role_run[-1]):
            role_run.append(scene)
        else:
            flush_role_run(role_run)
            role_run = [scene]

    flush_template_run(template_run)
    flush_role_run(role_run)

    repetition_risk = max_risk(template_risk, role_risk)
    return {
        "repeated_template_runs": repeated_template_runs,
        "repeated_template_ids": repeated_template_ids,
        "repeated_role_runs": repeated_role_runs,
        "repeated_role_ids": repeated_role_ids,
        "repetition_risk": repetition_risk,
    }


def _analyze_hook_strength(scenes: list[dict[str, Any]]) -> dict[str, Any]:
    hook_scene = next((scene for scene in scenes if _normalized_role(scene) == "hook"), None)
    hook_scene_id = hook_scene.get("id") if hook_scene else None
    headline = _scene_headline(hook_scene) if hook_scene else ""
    if not hook_scene:
        risk = "high"
    elif _looks_like_weak_hook(headline):
        risk = "high"
    elif len(headline.strip()) <= 14:
        risk = "medium"
    else:
        risk = "low"
    return {
        "hook_scene_id": hook_scene_id,
        "hook_headline": headline,
        "hook_strength_risk": risk,
    }


def _scene_quality_score(
    scene: dict[str, Any],
    director_scene: dict[str, Any] | None,
    *,
    index: int,
    total_scenes: int,
    cta_info: dict[str, Any],
    proof_info: dict[str, Any],
    repetition_info: dict[str, Any],
    hook_info: dict[str, Any],
) -> tuple[float, list[str], list[str]]:
    semantic_score = scene.get("semantic_score", {})
    issues: list[str] = []
    structural_risks: list[str] = []
    role_match = float(semantic_score.get("role_match", 0.5))
    completeness = float(semantic_score.get("slot_completeness", 0.5))
    readability_risk = float(semantic_score.get("visual_readability_risk", 0.5))
    score = 0.55 + role_match * 0.25 + completeness * 0.20 - readability_risk * 0.20

    scene_id = scene.get("id")
    if scene_id in cta_info["early_cta_ids"]:
        issues.append("early_cta")
        structural_risks.append("early_cta")
        score -= 0.10
    if scene_id in cta_info["repeated_cta_ids"]:
        issues.append("repeated_cta")
        structural_risks.append("repeated_cta")
        score -= 0.08
    if scene_id in proof_info["abstract_proof_ids"]:
        issues.append("abstract_proof")
        structural_risks.append("abstract_proof")
        score -= 0.10
    if scene_id in repetition_info["repeated_template_ids"]:
        issues.append("repeated_template")
        structural_risks.append("repeated_template")
        score -= 0.08
    if scene_id in repetition_info["repeated_role_ids"]:
        issues.append("repeated_role")
        structural_risks.append("repeated_role")
        score -= 0.06
    if scene_id == hook_info["hook_scene_id"] and hook_info["hook_strength_risk"] in {"medium", "high"}:
        issues.append("weak_hook")
        structural_risks.append("weak_hook")
        score -= 0.12 if hook_info["hook_strength_risk"] == "medium" else 0.18
    if director_scene and director_scene.get("template_contract_fallback_used"):
        issues.append("fallback_used")
        structural_risks.append("fallback_used")
        score -= 0.30
    if director_scene and director_scene.get("template_contract_status") != "PASS":
        issues.append("contract_not_pass")
        structural_risks.append("contract_not_pass")
        score -= 0.20
    if _has_placeholder(scene.get("slots", {})):
        issues.append("placeholder")
        structural_risks.append("placeholder")
        score -= 0.25

    return max(score, 0.0), issues, structural_risks


def _publish_candidate_readiness(
    *,
    gate_status: str,
    semantic_quality_score: float,
    cta_distribution_risk: str,
    proof_strength_risk: str,
    worst_scene_score: float,
    fallback_count: int,
    raw_text_dependency_count: int,
    placeholder_count: int,
    role_template_mismatch_count: int,
) -> str:
    if gate_status == "FAIL":
        return "NO_GO"
    if (
        semantic_quality_score >= 90
        and cta_distribution_risk == "low"
        and proof_strength_risk == "low"
        and worst_scene_score >= 0.75
        and fallback_count == 0
        and raw_text_dependency_count == 0
        and placeholder_count == 0
        and role_template_mismatch_count == 0
    ):
        return "READY"
    if (
        cta_distribution_risk == "high"
        or proof_strength_risk == "high"
        or semantic_quality_score < 75
    ):
        return "NO_GO"
    return "REVIEW"


def _score_band(score: float) -> str:
    if score >= 90:
        return "READY"
    if score >= 75:
        return "REVIEW"
    return "FAIL"


def _overall_quality_score(
    *,
    average_scene_score: float,
    fallback_ratio: float,
    placeholder_count: int,
    raw_text_dependency_count: int,
    role_template_mismatch_count: int,
    chinese_dominance_score: float,
    worst_scene_score: float,
    cta_distribution_risk: str,
    proof_strength_risk: str,
    scene_repetition_risk: str,
    hook_strength_risk: str,
) -> float:
    score = average_scene_score * 100.0
    score -= _risk_penalty(cta_distribution_risk, low=0.0, medium=4.0, high=8.0)
    score -= _risk_penalty(proof_strength_risk, low=0.0, medium=3.0, high=6.0)
    score -= _risk_penalty(scene_repetition_risk, low=0.0, medium=3.0, high=6.0)
    score -= _risk_penalty(hook_strength_risk, low=0.0, medium=2.0, high=4.0)
    score -= fallback_ratio * 20.0
    score -= placeholder_count * 15.0
    score -= raw_text_dependency_count * 20.0
    score -= role_template_mismatch_count * 15.0
    score -= max(0.0, 0.78 - chinese_dominance_score) * 30.0
    score -= max(0.0, 0.85 - worst_scene_score) * 20.0
    return round(max(0.0, min(100.0, score)), 2)


def _risk_penalty(risk: str, *, low: float, medium: float, high: float) -> float:
    if risk == "high":
        return high
    if risk == "medium":
        return medium
    return low


def _is_cta_scene(scene: dict[str, Any]) -> bool:
    role = _normalized_role(scene)
    template_type = _normalized_template(scene)
    return role == "cta" or template_type in CTA_TEMPLATE_HINTS or "cta" in template_type


def _is_proof_scene(scene: dict[str, Any]) -> bool:
    role = _normalized_role(scene)
    template_type = _normalized_template(scene)
    return role == "proof" or template_type in PROOF_TEMPLATES


def _is_abstract_proof(blob: str) -> bool:
    blob = blob.strip()
    if not blob:
        return True
    has_generic = any(term in blob for term in GENERIC_PROOF_PHRASES)
    if not has_generic:
        return False
    has_concrete = any(marker in blob for marker in CONCRETE_PROOF_MARKERS)
    return not has_concrete


def _looks_like_weak_hook(headline: str) -> bool:
    normalized = headline.strip()
    if not normalized:
        return True
    if any(term in normalized for term in WEAK_HOOK_GENERIC_PHRASES) and not any(
        marker in normalized for marker in WEAK_HOOK_STRONG_MARKERS
    ):
        return True
    if len(normalized) <= 10:
        return True
    if not any(marker in normalized for marker in WEAK_HOOK_STRONG_MARKERS) and normalized in WEAK_HOOK_GENERIC_PHRASES:
        return True
    return False


def _scene_headline(scene: dict[str, Any] | None) -> str:
    if not scene:
        return ""
    for key in ("display_headline", "headline", "title", "main_claim"):
        value = scene.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    slots = scene.get("slots", {}) or {}
    for key in ("main_claim", "final_claim", "proof_title", "problem_title", "method_title", "concept_title", "result_title"):
        value = slots.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _normalized_role(scene: dict[str, Any] | None) -> str:
    if not scene:
        return ""
    return str(scene.get("role") or scene.get("scene_pack_role") or "").strip().lower()


def _normalized_template(scene: dict[str, Any] | None) -> str:
    if not scene:
        return ""
    return str(scene.get("template_type") or scene.get("contract_template_id") or "").strip().lower()


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


def max_risk(left: str, right: str) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    return left if order.get(left, 0) >= order.get(right, 0) else right
