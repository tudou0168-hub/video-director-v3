"""Semantic quality gate for contract-driven preview validation."""
from __future__ import annotations

import json
import re
from pathlib import Path
from statistics import mean
from typing import Any

from video_director_v3.director.cta_policy import load_default_cta_policy
from video_director_v3.director.offer_profile import load_default_offer_profile
from video_director_v3.director.proof_asset import load_default_proof_asset, proof_metric_is_suspicious


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
    offer_info = _analyze_offer_profile(scene_pack.get("scenes", []))
    proof_asset_info = _analyze_proof_asset(scene_pack.get("scenes", []))
    cta_policy_info = _analyze_cta_policy(scene_pack.get("scenes", []))
    visual_strategy_info = _analyze_visual_strategy_pack(scene_pack, merged_scenes, repetition_info)
    chinese_dominance_score = round(_chinese_dominance_score(merged_scenes), 3)
    layout_families = [str(scene.get("layout_family") or "").strip() for scene in merged_scenes]
    visual_objects = [str(scene.get("visual_object") or "").strip() for scene in merged_scenes]
    memory_anchors = [str(scene.get("memory_anchor") or "").strip() for scene in merged_scenes]
    ending_variants = [str(scene.get("ending_variant") or "").strip() for scene in merged_scenes]
    visual_strategy_enabled = bool(scene_pack.get("visual_strategy_id")) or any(
        any(str(scene.get(field) or "").strip() for field in ("layout_family", "visual_object", "memory_anchor", "save_reason"))
        for scene in merged_scenes
    )
    visual_strategy_scoring = visual_strategy_info
    if not visual_strategy_enabled:
        visual_strategy_scoring = {
            **visual_strategy_info,
            "visual_strategy_risk": "low",
            "same_video_risk": "low",
            "template_sequence_similarity_risk": "low",
            "ending_similarity_risk": "low",
            "caption_style_repetition_risk": "low",
            "differentiation_score": max(visual_strategy_info.get("differentiation_score", 100.0), 100.0),
            "layout_readability_score": max(visual_strategy_info.get("layout_readability_score", 100.0), 100.0),
            "repeated_opening_ids": [],
            "repeated_ending_ids": [],
            "caption_conflict_ids": [],
            "top_heavy_ids": [],
            "dense_readability_ids": [],
            "visual_object_missing_ids": [],
            "memory_anchor_missing_ids": [],
            "save_reason_missing_ids": [],
            "headline_fragment_ids": [],
        }

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
            offer_info=offer_info,
            proof_asset_info=proof_asset_info,
            cta_policy_info=cta_policy_info,
            visual_strategy_info=visual_strategy_scoring,
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
    unique_layout_families = len({item for item in layout_families if item}) or 1

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
    if visual_strategy_enabled and visual_strategy_info["visual_object_missing_count"] > 0:
        hard_fail_reasons.append("visual_object_missing_count > 0")
    if visual_strategy_enabled and visual_strategy_info["memory_anchor_missing_count"] > 0:
        hard_fail_reasons.append("memory_anchor_missing_count > 0")
    if visual_strategy_enabled and visual_strategy_info["save_reason_missing_count"] > 0:
        hard_fail_reasons.append("save_reason_missing_count > 0")
    if visual_strategy_enabled and visual_strategy_info["headline_fragment_risk_count"] > 0:
        hard_fail_reasons.append("headline_fragment_risk_count > 0")
    if visual_strategy_enabled and visual_strategy_info["same_video_risk"] == "high":
        if visual_strategy_info["differentiation_score"] < 25 or unique_layout_families <= 3:
            hard_fail_reasons.append("same_video_risk = high")
    hard_fail_reasons.extend(offer_info["hard_fail_reasons"])
    hard_fail_reasons.extend(proof_asset_info["hard_fail_reasons"])
    hard_fail_reasons.extend(cta_policy_info["hard_fail_reasons"])
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
        offer_profile_risk=offer_info["offer_profile_risk"],
        proof_asset_risk=proof_asset_info["proof_asset_risk"],
        cta_policy_risk=cta_policy_info["cta_policy_risk"],
        visual_strategy_risk=visual_strategy_scoring["visual_strategy_risk"],
        layout_readability_score=visual_strategy_scoring["layout_readability_score"],
        differentiation_score=visual_strategy_scoring["differentiation_score"],
    )

    gate_status = "FAIL" if hard_fail_reasons else "PASS"
    score_band = "FAIL" if hard_fail_reasons else _score_band(semantic_quality_score)
    publish_candidate_readiness = _publish_candidate_readiness(
        gate_status=gate_status,
        semantic_quality_score=semantic_quality_score,
        cta_distribution_risk=cta_info["cta_distribution_risk"],
        proof_strength_risk=proof_info["proof_strength_risk"],
        differentiation_score=visual_strategy_scoring["differentiation_score"],
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
        "offer_profile": offer_info,
        "proof_asset": proof_asset_info,
        "cta_policy": cta_policy_info,
        "visual_strategy": visual_strategy_info,
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


def _analyze_offer_profile(scenes: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(scene.get("offer_profile_ref") for scene in scenes)
    offer_profile = load_default_offer_profile()
    offer_scene_ids = [scene.get("id") for scene in scenes if _is_offer_scene(scene) and scene.get("id")]
    missing_offer_profile_ids = [scene.get("id") for scene in scenes if _is_offer_scene(scene) and not scene.get("offer_profile_ref") and scene.get("id")]
    missing_core_promise_ids: list[str] = []
    for scene in scenes:
        if _is_offer_scene(scene) and scene.get("offer_profile_ref") and not offer_profile.core_promise.strip() and scene.get("id"):
            missing_core_promise_ids.append(scene["id"])

    if not active:
        return {
            "offer_scene_count": len(offer_scene_ids),
            "offer_scene_ids": offer_scene_ids,
            "missing_offer_profile_count": 0,
            "missing_offer_profile_ids": [],
            "missing_core_promise_count": 0,
            "missing_core_promise_ids": [],
            "offer_profile_risk": "low" if offer_scene_ids else "skip",
            "hard_fail_reasons": [],
        }

    hard_fail_reasons: list[str] = []
    if missing_offer_profile_ids:
        hard_fail_reasons.append("offer_profile_ref missing on offer scenes")
    if missing_core_promise_ids or not offer_profile.core_promise.strip():
        hard_fail_reasons.append("offer core promise missing")

    if hard_fail_reasons:
        risk = "high"
    elif len(offer_scene_ids) >= 4:
        risk = "medium"
    else:
        risk = "low"

    return {
        "offer_scene_count": len(offer_scene_ids),
        "offer_scene_ids": offer_scene_ids,
        "missing_offer_profile_count": len(missing_offer_profile_ids),
        "missing_offer_profile_ids": missing_offer_profile_ids,
        "missing_core_promise_count": len(missing_core_promise_ids),
        "missing_core_promise_ids": missing_core_promise_ids,
        "offer_profile_risk": risk,
        "hard_fail_reasons": hard_fail_reasons,
    }


def _analyze_proof_asset(scenes: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(scene.get("proof_asset_ref") for scene in scenes)
    proof_asset = load_default_proof_asset()
    proof_scene_ids = [scene.get("id") for scene in scenes if _is_proof_scene(scene) and scene.get("id")]
    generic_proof_ids: list[str] = []
    fake_metric_ids: list[str] = []
    missing_proof_ref_ids: list[str] = []
    for scene in scenes:
        if not _is_proof_scene(scene):
            continue
        scene_id = scene.get("id")
        if scene_id and not scene.get("proof_asset_ref"):
            missing_proof_ref_ids.append(scene_id)
        blob = " ".join(_slot_strings(scene.get("slots", {})))
        if _is_abstract_proof(blob):
            if scene_id:
                generic_proof_ids.append(scene_id)
        metric = str(scene.get("slots", {}).get("metric_or_evidence", "")).strip()
        if metric and proof_metric_is_suspicious(metric):
            if scene_id:
                fake_metric_ids.append(scene_id)

    if not active:
        return {
            "proof_scene_count": len(proof_scene_ids),
            "proof_scene_ids": proof_scene_ids,
            "generic_proof_count": 0,
            "generic_proof_ids": [],
            "fake_metric_count": 0,
            "fake_metric_ids": [],
            "missing_proof_ref_count": 0,
            "missing_proof_ref_ids": [],
            "proof_asset_risk": "low" if proof_scene_ids else "skip",
            "hard_fail_reasons": [],
        }

    hard_fail_reasons: list[str] = []
    if missing_proof_ref_ids:
        hard_fail_reasons.append("proof_asset_ref missing on proof scenes")
    if fake_metric_ids:
        hard_fail_reasons.append("fake proof metric detected")

    if hard_fail_reasons:
        risk = "high"
    elif generic_proof_ids:
        risk = "medium"
    else:
        risk = "low"

    return {
        "proof_scene_count": len(proof_scene_ids),
        "proof_scene_ids": proof_scene_ids,
        "generic_proof_count": len(generic_proof_ids),
        "generic_proof_ids": generic_proof_ids,
        "fake_metric_count": len(fake_metric_ids),
        "fake_metric_ids": fake_metric_ids,
        "missing_proof_ref_count": len(missing_proof_ref_ids),
        "missing_proof_ref_ids": missing_proof_ref_ids,
        "proof_asset_risk": risk,
        "hard_fail_reasons": hard_fail_reasons,
    }


def _analyze_cta_policy(scenes: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(scene.get("cta_policy_ref") for scene in scenes)
    cta_policy = load_default_cta_policy()
    cta_scene_ids = [scene.get("id") for scene in scenes if _is_cta_scene(scene) and scene.get("id")]
    early_cta_ids: list[str] = []
    repeated_cta_ids: list[str] = []
    forbidden_cta_ids: list[str] = []

    cta_indices = [(index, scene) for index, scene in enumerate(scenes) if _is_cta_scene(scene)]
    early_threshold = max(1, int(len(scenes) * cta_policy.early_cta_ratio)) if len(scenes) >= 8 else 0
    seen_cta_texts: set[str] = set()
    for index, scene in cta_indices:
        scene_id = scene.get("id")
        stage = str(scene.get("cta_stage") or "").strip().lower()
        text = " ".join(
            item
            for item in [
                _scene_headline(scene),
                str(scene.get("display_subtitle") or "").strip(),
                str(scene.get("display_conclusion") or "").strip(),
                str(scene.get("voiceover") or "").strip(),
                str(scene.get("slots", {}).get("cta_text") or "").strip(),
                str(scene.get("slots", {}).get("next_step") or "").strip(),
            ]
            if item
        )
        if scene_id and text in seen_cta_texts:
            repeated_cta_ids.append(scene_id)
        seen_cta_texts.add(text)
        if early_threshold and index < early_threshold:
            if scene_id:
                early_cta_ids.append(scene_id)
        if stage == "opening" and scene_id:
            early_cta_ids.append(scene_id)
        proof_count_before_final_cta = sum(1 for prior in scenes[:index] if _is_proof_scene(prior))
        if stage == "final" and proof_count_before_final_cta < cta_policy.min_proof_scenes_before_final_cta:
            if scene_id:
                early_cta_ids.append(scene_id)
        for phrase in cta_policy.forbidden_phrases:
            if phrase and phrase in text and scene_id:
                forbidden_cta_ids.append(scene_id)

    missing_policy_ref_ids = [scene.get("id") for scene in scenes if _is_cta_scene(scene) and not scene.get("cta_policy_ref") and scene.get("id")]
    early_cta_ids = list(dict.fromkeys(early_cta_ids))
    repeated_cta_ids = list(dict.fromkeys(repeated_cta_ids))
    forbidden_cta_ids = list(dict.fromkeys(forbidden_cta_ids))

    if not active:
        return {
            "cta_scene_count": len(cta_scene_ids),
            "cta_scene_ids": cta_scene_ids,
            "early_cta_count": 0,
            "early_cta_ids": [],
            "repeated_cta_count": 0,
            "repeated_cta_ids": [],
            "forbidden_cta_count": 0,
            "forbidden_cta_ids": [],
            "missing_policy_ref_count": 0,
            "missing_policy_ref_ids": [],
            "cta_policy_risk": "low" if cta_scene_ids else "skip",
            "hard_fail_reasons": [],
        }

    hard_fail_reasons: list[str] = []
    if missing_policy_ref_ids:
        hard_fail_reasons.append("cta_policy_ref missing on CTA scenes")
    if forbidden_cta_ids:
        hard_fail_reasons.append("forbidden CTA phrase detected")

    if hard_fail_reasons:
        risk = "high"
    elif len(cta_scene_ids) > cta_policy.max_cta_scenes or len(early_cta_ids) > 1 or len(repeated_cta_ids) > cta_policy.repeated_cta_soft_limit:
        risk = "medium"
    else:
        risk = "low"

    return {
        "cta_scene_count": len(cta_scene_ids),
        "cta_scene_ids": cta_scene_ids,
        "early_cta_count": len(early_cta_ids),
        "early_cta_ids": early_cta_ids,
        "repeated_cta_count": len(repeated_cta_ids),
        "repeated_cta_ids": repeated_cta_ids,
        "forbidden_cta_count": len(forbidden_cta_ids),
        "forbidden_cta_ids": forbidden_cta_ids,
        "missing_policy_ref_count": len(missing_policy_ref_ids),
        "missing_policy_ref_ids": missing_policy_ref_ids,
        "cta_policy_risk": risk,
        "hard_fail_reasons": hard_fail_reasons,
    }


def _analyze_visual_strategy_pack(
    scene_pack: dict[str, Any],
    scenes: list[dict[str, Any]],
    repetition_info: dict[str, Any],
) -> dict[str, Any]:
    video_type = str(scene_pack.get("video_type") or "knowledge_method").strip() or "knowledge_method"
    visual_strategy_id = str(scene_pack.get("visual_strategy_id") or "").strip()
    opening_variant = str(scene_pack.get("opening_variant") or "").strip()
    ending_variant = str(scene_pack.get("ending_variant") or "").strip()
    template_sequence_signature = str(scene_pack.get("template_sequence_signature") or "").strip()
    template_sequence = [str(scene.get("template_type") or "").strip() for scene in scenes if scene.get("template_type")]
    caption_modes = [str(scene.get("caption_mode") or "standard_caption").strip() for scene in scenes]
    layout_families = [str(scene.get("layout_family") or "").strip() for scene in scenes]
    visual_objects = [str(scene.get("visual_object") or "").strip() for scene in scenes]
    memory_anchors = [str(scene.get("memory_anchor") or "").strip() for scene in scenes]
    save_reasons = [str(scene.get("save_reason") or "").strip() for scene in scenes]
    ending_variants = [str(scene.get("ending_variant") or "").strip() for scene in scenes]
    layout_bands = [str(scene.get("layout_band") or "middle").strip() for scene in scenes]
    headlines = [str(scene.get("visual_headline") or scene.get("headline_compact") or _scene_headline(scene)).strip() for scene in scenes]
    subtitle_similarities = [float(scene.get("title_caption_similarity") or 0.0) for scene in scenes]
    readability_risks = [float(scene.get("readability_risk") or 0.0) for scene in scenes]

    counts: dict[str, int] = {}
    for template_type in template_sequence:
        counts[template_type] = counts.get(template_type, 0) + 1
    dominant_template_count = max(counts.values()) if counts else 0
    dominant_template_ids = [scene.get("id") for scene in scenes if scene.get("template_type") and counts.get(str(scene.get("template_type")), 0) == dominant_template_count and scene.get("id")]

    opening_window = scenes[: min(3, len(scenes))]
    ending_window = scenes[max(0, len(scenes) - 3) :]
    opening_templates = [str(scene.get("template_type") or "") for scene in opening_window]
    ending_templates = [str(scene.get("template_type") or "") for scene in ending_window]
    opening_roles = [str(scene.get("role") or "") for scene in opening_window]
    ending_roles = [str(scene.get("role") or "") for scene in ending_window]
    repeated_opening_ids = [scene.get("id") for scene in opening_window if scene.get("id") and (opening_templates.count(str(scene.get("template_type") or "")) >= 2 or opening_roles.count(str(scene.get("role") or "")) >= 2)]
    repeated_ending_ids = [scene.get("id") for scene in ending_window if scene.get("id") and (ending_templates.count(str(scene.get("template_type") or "")) >= 2 or ending_roles.count(str(scene.get("role") or "")) >= 2)]

    caption_mode_runs = 0
    caption_mode_run: list[str] = []
    for mode in caption_modes:
        if not caption_mode_run or mode == caption_mode_run[-1]:
            caption_mode_run.append(mode)
        else:
            if len(caption_mode_run) >= 2:
                caption_mode_runs += len(caption_mode_run) - 1
            caption_mode_run = [mode]
    if len(caption_mode_run) >= 2:
        caption_mode_runs += len(caption_mode_run) - 1

    caption_conflict_ids = [
        scene.get("id")
        for scene in scenes
        if scene.get("id")
        and (
            float(scene.get("title_caption_similarity") or 0.0) > 0.68
            or (
                str(scene.get("caption_mode") or "") in {"minimal_caption", "standard_caption"}
                and float(scene.get("readability_risk") or 0.0) > 0.55
            )
        )
    ]
    top_third = scenes[: max(1, len(scenes) // 3)]
    top_heavy_ids = [
        scene.get("id")
        for scene in top_third
        if scene.get("id")
        and (
            str(scene.get("layout_band") or "") == "upper"
            or float(scene.get("readability_risk") or 0.0) > 0.5
            or len(str(scene.get("headline_compact") or _scene_headline(scene))) > 18
        )
    ]
    dense_readability_ids = [
        scene.get("id")
        for scene in scenes
        if scene.get("id") and float(scene.get("readability_risk") or 0.0) >= 0.55
    ]
    long_headline_ids = [
        scene.get("id")
        for scene in scenes
        if scene.get("id")
        and len(str(scene.get("visual_headline") or scene.get("headline_compact") or _scene_headline(scene))) > 18
    ]
    fragment_headline_ids = [
        scene.get("id")
        for scene in scenes
        if scene.get("id")
        and _is_fragment_headline(str(scene.get("visual_headline") or scene.get("headline_compact") or _scene_headline(scene)))
    ]
    visual_object_missing_ids = [scene.get("id") for scene in scenes if scene.get("id") and not str(scene.get("visual_object") or "").strip()]
    memory_anchor_missing_ids = [scene.get("id") for scene in scenes if scene.get("id") and not str(scene.get("memory_anchor") or "").strip()]
    save_reason_missing_ids = [scene.get("id") for scene in scenes if scene.get("id") and not str(scene.get("save_reason") or "").strip()]
    repeated_opening_ids = list(dict.fromkeys(repeated_opening_ids))
    repeated_ending_ids = list(dict.fromkeys(repeated_ending_ids))
    caption_conflict_ids = list(dict.fromkeys(caption_conflict_ids))
    top_heavy_ids = list(dict.fromkeys(top_heavy_ids))
    dense_readability_ids = list(dict.fromkeys(dense_readability_ids))
    long_headline_ids = list(dict.fromkeys(long_headline_ids))
    fragment_headline_ids = list(dict.fromkeys(fragment_headline_ids))
    visual_object_missing_ids = list(dict.fromkeys(visual_object_missing_ids))
    memory_anchor_missing_ids = list(dict.fromkeys(memory_anchor_missing_ids))
    save_reason_missing_ids = list(dict.fromkeys(save_reason_missing_ids))

    unique_caption_modes = len(set(caption_modes)) or 1
    unique_templates = len(set(template_sequence)) or 1
    unique_layout_families = len({item for item in layout_families if item}) or 1
    caption_conflict_count = len(caption_conflict_ids)
    title_caption_overlap_risk = "high" if sum(1 for value in subtitle_similarities if value > 0.68) >= max(2, len(scenes) // 3) else "medium" if any(value > 0.68 for value in subtitle_similarities) else "low"
    repeated_opening_risk = "high" if len(set(opening_templates)) <= 1 and len(opening_templates) >= 2 else "medium" if len(set(opening_templates)) <= 2 else "low"
    repeated_ending_risk = "high" if len(set(ending_templates)) <= 1 and len(ending_templates) >= 2 else "medium" if len(set(ending_templates)) <= 2 else "low"
    template_repetition_risk = max_risk(
        "high" if repetition_info.get("repetition_risk") == "high" or dominant_template_count >= max(4, len(scenes) // 2 + 1) else "medium" if repetition_info.get("repetition_risk") == "medium" or dominant_template_count >= 3 else "low",
        "medium" if unique_templates <= 2 and len(scenes) >= 4 else "low",
    )
    caption_mode_repetition_risk = "high" if unique_caption_modes <= 2 and caption_mode_runs >= max(2, len(scenes) // 2) else "medium" if unique_caption_modes <= 3 or caption_mode_runs >= 2 else "low"
    top_heavy_risk = "high" if len(top_heavy_ids) >= max(2, len(top_third) - 1) else "medium" if top_heavy_ids else "low"
    dense_scene_readability_risk = "high" if len(dense_readability_ids) >= max(3, len(scenes) // 2) else "medium" if dense_readability_ids else "low"
    differentiation_score = _differentiation_score(
        template_sequence=template_sequence,
        layout_families=layout_families,
        visual_objects=visual_objects,
        memory_anchors=memory_anchors,
        ending_variants=ending_variants,
        dominant_template_count=dominant_template_count,
        caption_mode_repetition_risk=caption_mode_repetition_risk,
        repeated_opening_risk=repeated_opening_risk,
        repeated_ending_risk=repeated_ending_risk,
        caption_conflict_count=caption_conflict_count,
        top_heavy_ids=top_heavy_ids,
        long_headline_ids=long_headline_ids,
        dense_readability_ids=dense_readability_ids,
        repetition_info=repetition_info,
    )
    template_sequence_similarity_risk = "high" if (unique_templates <= 3 and dominant_template_count >= max(3, len(scenes) // 2)) or repetition_info.get("repeated_template_runs", 0) >= 2 else "medium" if unique_templates <= 4 else "low"
    ending_similarity_risk = repeated_ending_risk
    caption_style_repetition_risk = caption_mode_repetition_risk
    headline_fragment_risk_count = len(fragment_headline_ids)
    same_video_risk = "high" if (
        differentiation_score < 70
        or template_sequence_similarity_risk == "high"
        or ending_similarity_risk == "high"
        or caption_style_repetition_risk == "high"
        or len(visual_object_missing_ids) > 0
    ) else "medium" if differentiation_score < 82 or unique_layout_families <= 3 else "low"
    layout_readability_score = _layout_readability_score(readability_risks, subtitle_similarities, dense_readability_ids, caption_conflict_ids)

    return {
        "video_type": video_type,
        "visual_strategy_id": visual_strategy_id,
        "opening_variant": opening_variant,
        "ending_variant": ending_variant,
        "template_sequence_signature": template_sequence_signature,
        "template_sequence": template_sequence,
        "layout_families": layout_families,
        "visual_objects": visual_objects,
        "memory_anchors": memory_anchors,
        "save_reasons": save_reasons,
        "dominant_template_count": dominant_template_count,
        "dominant_template_ids": dominant_template_ids,
        "repeated_opening_risk": repeated_opening_risk,
        "repeated_opening_count": len(repeated_opening_ids),
        "repeated_opening_ids": repeated_opening_ids,
        "repeated_ending_risk": repeated_ending_risk,
        "repeated_ending_count": len(repeated_ending_ids),
        "repeated_ending_ids": repeated_ending_ids,
        "template_repetition_risk": template_repetition_risk,
        "caption_mode_repetition_risk": caption_mode_repetition_risk,
        "caption_style_repetition_risk": caption_style_repetition_risk,
        "differentiation_score": differentiation_score,
        "top_heavy_risk": top_heavy_risk,
        "top_heavy_count": len(top_heavy_ids),
        "top_heavy_ids": top_heavy_ids,
        "title_caption_overlap_risk": title_caption_overlap_risk,
        "title_caption_overlap_count": sum(1 for value in subtitle_similarities if value > 0.68),
        "long_headline_count": len(long_headline_ids),
        "long_headline_ids": long_headline_ids,
        "headline_fragment_risk_count": headline_fragment_risk_count,
        "headline_fragment_ids": fragment_headline_ids,
        "dense_scene_readability_risk": dense_scene_readability_risk,
        "dense_scene_readability_count": len(dense_readability_ids),
        "dense_readability_ids": dense_readability_ids,
        "caption_conflict_count": caption_conflict_count,
        "caption_conflict_ids": caption_conflict_ids,
        "layout_readability_score": layout_readability_score,
        "same_video_risk": same_video_risk,
        "template_sequence_similarity_risk": template_sequence_similarity_risk,
        "ending_similarity_risk": ending_similarity_risk,
        "visual_object_missing_count": len(visual_object_missing_ids),
        "visual_object_missing_ids": visual_object_missing_ids,
        "memory_anchor_missing_count": len(memory_anchor_missing_ids),
        "memory_anchor_missing_ids": memory_anchor_missing_ids,
        "save_reason_missing_count": len(save_reason_missing_ids),
        "save_reason_missing_ids": save_reason_missing_ids,
        "visual_strategy_risk": max_risk(
            max_risk(
                max_risk(template_repetition_risk, caption_mode_repetition_risk),
                max_risk(top_heavy_risk, dense_scene_readability_risk),
            ),
            same_video_risk,
        ),
    }


def _is_offer_scene(scene: dict[str, Any]) -> bool:
    role = _normalized_role(scene)
    template_type = _normalized_template(scene)
    return role in {"offer", "verdict", "cta"} or template_type in {"result_summary", "final_cta"}


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
    offer_info: dict[str, Any],
    proof_asset_info: dict[str, Any],
    cta_policy_info: dict[str, Any],
    visual_strategy_info: dict[str, Any],
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
    if scene_id in offer_info["missing_offer_profile_ids"]:
        issues.append("missing_offer_profile_ref")
        structural_risks.append("missing_offer_profile_ref")
        score -= 0.08
    if scene_id in offer_info["missing_core_promise_ids"]:
        issues.append("missing_core_promise")
        structural_risks.append("missing_core_promise")
        score -= 0.12
    if scene_id in proof_asset_info["missing_proof_ref_ids"]:
        issues.append("missing_proof_asset_ref")
        structural_risks.append("missing_proof_asset_ref")
        score -= 0.08
    if scene_id in proof_asset_info["generic_proof_ids"]:
        issues.append("generic_proof")
        structural_risks.append("generic_proof")
        score -= 0.10
    if scene_id in proof_asset_info["fake_metric_ids"]:
        issues.append("fake_proof_metric")
        structural_risks.append("fake_proof_metric")
        score -= 0.18
    if scene_id in cta_policy_info["missing_policy_ref_ids"]:
        issues.append("missing_cta_policy_ref")
        structural_risks.append("missing_cta_policy_ref")
        score -= 0.08
    if scene_id in cta_policy_info["forbidden_cta_ids"]:
        issues.append("forbidden_cta_phrase")
        structural_risks.append("forbidden_cta_phrase")
        score -= 0.20
    if scene_id in cta_policy_info["early_cta_ids"]:
        issues.append("early_cta_policy")
        structural_risks.append("early_cta_policy")
        score -= 0.06
    if scene_id in cta_policy_info["repeated_cta_ids"]:
        issues.append("repeated_cta_policy")
        structural_risks.append("repeated_cta_policy")
        score -= 0.05
    if scene_id in visual_strategy_info["repeated_opening_ids"]:
        issues.append("repeated_opening")
        structural_risks.append("repeated_opening")
        score -= 0.07
    if scene_id in visual_strategy_info["repeated_ending_ids"]:
        issues.append("repeated_ending")
        structural_risks.append("repeated_ending")
        score -= 0.06
    if scene_id in visual_strategy_info["caption_conflict_ids"]:
        issues.append("caption_conflict")
        structural_risks.append("caption_conflict")
        score -= 0.08
    if scene_id in visual_strategy_info["top_heavy_ids"]:
        issues.append("top_heavy")
        structural_risks.append("top_heavy")
        score -= 0.05
    if scene_id in visual_strategy_info["dense_readability_ids"]:
        issues.append("dense_readability")
        structural_risks.append("dense_readability")
        score -= 0.05
    if scene_id in visual_strategy_info.get("visual_object_missing_ids", []):
        issues.append("missing_visual_object")
        structural_risks.append("missing_visual_object")
        score -= 0.05
    if scene_id in visual_strategy_info.get("memory_anchor_missing_ids", []):
        issues.append("missing_memory_anchor")
        structural_risks.append("missing_memory_anchor")
        score -= 0.05
    if scene_id in visual_strategy_info.get("save_reason_missing_ids", []):
        issues.append("missing_save_reason")
        structural_risks.append("missing_save_reason")
        score -= 0.04
    if scene_id in visual_strategy_info.get("headline_fragment_ids", []):
        issues.append("headline_fragment")
        structural_risks.append("headline_fragment")
        score -= 0.06
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
    differentiation_score: float,
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
        and differentiation_score >= 80
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
        or differentiation_score < 55
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
    offer_profile_risk: str,
    proof_asset_risk: str,
    cta_policy_risk: str,
    visual_strategy_risk: str,
    layout_readability_score: float,
    differentiation_score: float,
) -> float:
    score = average_scene_score * 100.0
    score -= _risk_penalty(cta_distribution_risk, low=0.0, medium=4.0, high=8.0)
    score -= _risk_penalty(proof_strength_risk, low=0.0, medium=3.0, high=6.0)
    score -= _risk_penalty(scene_repetition_risk, low=0.0, medium=3.0, high=6.0)
    score -= _risk_penalty(hook_strength_risk, low=0.0, medium=2.0, high=4.0)
    score -= _risk_penalty(offer_profile_risk, low=0.0, medium=2.0, high=5.0)
    score -= _risk_penalty(proof_asset_risk, low=0.0, medium=2.0, high=5.0)
    score -= _risk_penalty(cta_policy_risk, low=0.0, medium=3.0, high=7.0)
    score -= _risk_penalty(visual_strategy_risk, low=0.0, medium=2.0, high=6.0)
    score -= fallback_ratio * 20.0
    score -= placeholder_count * 15.0
    score -= raw_text_dependency_count * 20.0
    score -= role_template_mismatch_count * 15.0
    score -= max(0.0, 0.78 - chinese_dominance_score) * 30.0
    score -= max(0.0, 0.85 - worst_scene_score) * 20.0
    score -= max(0.0, 70.0 - layout_readability_score) * 0.35
    score -= max(0.0, 80.0 - differentiation_score) * 0.25
    return round(max(0.0, min(100.0, score)), 2)


def _risk_penalty(risk: str, *, low: float, medium: float, high: float) -> float:
    if risk == "high":
        return high
    if risk == "medium":
        return medium
    return low


def _differentiation_score(
    *,
    template_sequence: list[str],
    layout_families: list[str],
    visual_objects: list[str],
    memory_anchors: list[str],
    ending_variants: list[str],
    dominant_template_count: int,
    caption_mode_repetition_risk: str,
    repeated_opening_risk: str,
    repeated_ending_risk: str,
    caption_conflict_count: int,
    top_heavy_ids: list[str],
    long_headline_ids: list[str],
    dense_readability_ids: list[str],
    repetition_info: dict[str, Any],
) -> float:
    unique_templates = len(set(template_sequence)) or 1
    unique_layout_families = len({item for item in layout_families if item}) or 1
    unique_visual_objects = len({item for item in visual_objects if item}) or 1
    unique_memory_anchors = len({item for item in memory_anchors if item}) or 1
    unique_ending_variants = len({item for item in ending_variants if item}) or 1
    score = 100.0
    score -= max(0, dominant_template_count - 2) * 8.0
    score -= max(0, len(template_sequence) - unique_templates) * 3.0
    score -= _risk_penalty(caption_mode_repetition_risk, low=0.0, medium=6.0, high=12.0)
    score -= _risk_penalty(repeated_opening_risk, low=0.0, medium=6.0, high=10.0)
    score -= _risk_penalty(repeated_ending_risk, low=0.0, medium=6.0, high=10.0)
    score -= caption_conflict_count * 3.5
    score -= len(top_heavy_ids) * 2.5
    score -= len(long_headline_ids) * 1.5
    score -= len(dense_readability_ids) * 2.0
    score -= repetition_info.get("repeated_template_runs", 0) * 2.5
    score -= repetition_info.get("repeated_role_runs", 0) * 1.5
    score += min(24.0, unique_layout_families * 4.0)
    score += min(18.0, unique_visual_objects * 2.5)
    score += min(10.0, unique_memory_anchors * 0.8)
    score += min(8.0, unique_ending_variants * 2.0)
    return round(max(0.0, min(100.0, score)), 2)


def _layout_readability_score(
    readability_risks: list[float],
    subtitle_similarities: list[float],
    dense_readability_ids: list[str],
    caption_conflict_ids: list[str],
) -> float:
    if readability_risks:
        average_readability = mean(readability_risks)
    else:
        average_readability = 0.12
    if subtitle_similarities:
        average_overlap = mean(subtitle_similarities)
    else:
        average_overlap = 0.0
    score = 100.0
    score -= average_readability * 60.0
    score -= average_overlap * 25.0
    score -= len(dense_readability_ids) * 2.5
    score -= len(caption_conflict_ids) * 2.0
    return round(max(0.0, min(100.0, score)), 2)


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


def _is_fragment_headline(text: str) -> bool:
    normalized = re.sub(r"\s+", "", str(text or "")).strip()
    if not normalized:
        return True
    if normalized in {"10", "我把", "以前的流程是", "以前", "之前", "然后", "再", "先"}:
        return True
    if normalized.isdigit() or len(normalized) <= 2:
        return True
    if normalized.startswith(("我把", "以前的流程是", "以前", "之前", "然后", "再")):
        return True
    return False


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
