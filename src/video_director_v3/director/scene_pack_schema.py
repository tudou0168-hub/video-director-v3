"""Dry-run scene_pack schema for the semantic director boundary.

The scene_pack is the contract between V3 semantic planning and HyperFrames
native preview/render. It is intentionally data-only in this phase: existing
render templates still consume the current director_timeline shape until the
next migration step.
"""
from __future__ import annotations

from typing import Any


SCENE_PACK_VERSION = "v0.1-dry-run"

SUPPORTED_ROLES = {
    "hook",
    "problem",
    "conflict",
    "method",
    "proof",
    "offer",
    "cta",
    "verdict",
}

REQUIRED_SCENE_FIELDS = {
    "id",
    "role",
    "intent",
    "duration",
    "voiceover",
    "display_headline",
    "display_subtitle",
    "template_type",
    "slots",
    "qa_rules",
}

OPTIONAL_SCENE_EXTENSIONS = {
    "offer_profile_ref",
    "proof_asset_ref",
    "cta_policy_ref",
    "cta_stage",
    "cta_strength",
    "chapter_goal",
    "caption_mode",
    "layout_family",
    "layout_variant",
    "visual_object",
    "visual_headline",
    "memory_anchor",
    "save_reason",
    "primary_message",
    "visual_hook",
    "primary_elements",
    "support_elements",
    "forbidden_duplicates",
    "visual_role",
    "sequence_slot",
    "visual_strategy_reason",
    "layout_band",
    "headline_compact",
    "title_caption_similarity",
    "readability_risk",
    "layout_box",
}

TOP_LEVEL_OPTIONAL_EXTENSIONS = {
    "video_type",
    "visual_strategy_id",
    "opening_variant",
    "ending_variant",
    "template_sequence_signature",
    "visual_strategy",
}

CTA_STAGES = {"opening", "mid", "late", "final"}
CTA_STRENGTHS = {"soft", "normal", "strong"}

ROLE_ALIASES = {
    "pain": "problem",
    "explain": "method",
    "evidence": "proof",
    "summary": "verdict",
    "ready": "offer",
}


def normalize_scene_role(role: str) -> str:
    """Map legacy storyboard roles into the scene_pack role vocabulary."""
    normalized = (role or "method").strip().lower()
    return ROLE_ALIASES.get(normalized, normalized if normalized in SUPPORTED_ROLES else "method")


def validate_scene_pack(scene_pack: dict[str, Any]) -> list[str]:
    """Return validation errors for a scene_pack document."""
    errors: list[str] = []
    if scene_pack.get("version") != SCENE_PACK_VERSION:
        errors.append(f"version must be {SCENE_PACK_VERSION!r}")
    errors.extend(validate_scene_pack_extensions(scene_pack))
    if not isinstance(scene_pack.get("scenes"), list) or not scene_pack.get("scenes"):
        errors.append("scenes must be a non-empty list")
        return errors

    for index, scene in enumerate(scene_pack["scenes"]):
        errors.extend(validate_scene(scene, index))
    return errors


def validate_scene(scene: dict[str, Any], index: int = 0) -> list[str]:
    """Return validation errors for one scene_pack scene."""
    prefix = f"scenes[{index}]"
    errors: list[str] = []
    missing = REQUIRED_SCENE_FIELDS - set(scene)
    for field in sorted(missing):
        errors.append(f"{prefix}.{field} is required")

    role = scene.get("role")
    if role not in SUPPORTED_ROLES:
        errors.append(f"{prefix}.role {role!r} is not supported")
    if not isinstance(scene.get("duration"), (int, float)) or float(scene.get("duration", 0)) <= 0:
        errors.append(f"{prefix}.duration must be > 0")
    for field in ("id", "intent", "voiceover", "display_headline", "template_type"):
        value = scene.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.{field} must be a non-empty string")
    if not isinstance(scene.get("slots"), dict):
        errors.append(f"{prefix}.slots must be an object")
    if not isinstance(scene.get("qa_rules"), dict):
        errors.append(f"{prefix}.qa_rules must be an object")

    for field in ("offer_profile_ref", "proof_asset_ref", "cta_policy_ref"):
        if field in scene:
            value = scene.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{field} must be a non-empty string when present")

    if "cta_stage" in scene:
        value = scene.get("cta_stage")
        if value not in CTA_STAGES:
            errors.append(f"{prefix}.cta_stage {value!r} is not supported")
    if "cta_strength" in scene:
        value = scene.get("cta_strength")
        if value not in CTA_STRENGTHS:
            errors.append(f"{prefix}.cta_strength {value!r} is not supported")
    if "caption_mode" in scene:
        value = scene.get("caption_mode")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.caption_mode must be a non-empty string when present")
        elif value not in {"standard_caption", "emphasis_caption", "minimal_caption", "quote_caption", "action_caption"}:
            errors.append(f"{prefix}.caption_mode {value!r} is not supported")
    if "layout_family" in scene:
        value = scene.get("layout_family")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.layout_family must be a non-empty string when present")
        elif value not in {
            "hero_statement",
            "hero_metric",
            "process_ladder",
            "tool_pipeline",
            "config_panel",
            "file_tree",
            "comparison_board",
            "proof_matrix",
            "framework_map",
            "decision_fork",
            "opportunity_map",
            "action_close",
            "insight_close",
            "checklist_close",
            "offer_close",
        }:
            errors.append(f"{prefix}.layout_family {value!r} is not supported")
    if "ending_variant" in scene:
        value = scene.get("ending_variant")
        if not isinstance(value, str):
            errors.append(f"{prefix}.ending_variant must be a string when present")
        elif value not in {"insight_close", "homework_close", "action_close", "checklist_close", "offer_close", ""}:
            errors.append(f"{prefix}.ending_variant {value!r} is not supported")
    if "visual_object" in scene:
        value = scene.get("visual_object")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.visual_object must be a non-empty string when present")
    if "visual_headline" in scene:
        value = scene.get("visual_headline")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.visual_headline must be a non-empty string when present")
    if "memory_anchor" in scene:
        value = scene.get("memory_anchor")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.memory_anchor must be a non-empty string when present")
    if "save_reason" in scene:
        value = scene.get("save_reason")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.save_reason must be a non-empty string when present")
    if "visual_role" in scene:
        value = scene.get("visual_role")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.visual_role must be a non-empty string when present")
    if "sequence_slot" in scene:
        value = scene.get("sequence_slot")
        if value not in {"opening", "middle", "ending"}:
            errors.append(f"{prefix}.sequence_slot {value!r} is not supported")
    if "visual_strategy_reason" in scene:
        value = scene.get("visual_strategy_reason")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.visual_strategy_reason must be a non-empty string when present")
    if "layout_band" in scene:
        value = scene.get("layout_band")
        if value not in {"upper", "middle", "lower"}:
            errors.append(f"{prefix}.layout_band {value!r} is not supported")
    if "headline_compact" in scene:
        value = scene.get("headline_compact")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.headline_compact must be a non-empty string when present")
    if "title_caption_similarity" in scene:
        value = scene.get("title_caption_similarity")
        if not isinstance(value, (int, float)) or float(value) < 0 or float(value) > 1:
            errors.append(f"{prefix}.title_caption_similarity must be between 0 and 1")
    if "readability_risk" in scene:
        value = scene.get("readability_risk")
        if not isinstance(value, (int, float)) or float(value) < 0 or float(value) > 1:
            errors.append(f"{prefix}.readability_risk must be between 0 and 1")
    if "layout_box" in scene:
        value = scene.get("layout_box")
        if not isinstance(value, dict):
            errors.append(f"{prefix}.layout_box must be an object when present")
    return errors


def validate_scene_pack_extensions(scene_pack: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("video_type", "visual_strategy_id", "opening_variant", "ending_variant", "template_sequence_signature"):
        if field in scene_pack:
            value = scene_pack.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field} must be a non-empty string when present")
    if "video_type" in scene_pack and scene_pack.get("video_type") not in {"knowledge_method", "ai_toolflow", "sales_offer"}:
        errors.append(f"video_type {scene_pack.get('video_type')!r} is not supported")
    if "opening_variant" in scene_pack and scene_pack.get("opening_variant") not in {"pain_hook", "result_hook", "mistake_hook", "contrast_hook", "process_hook"}:
        errors.append(f"opening_variant {scene_pack.get('opening_variant')!r} is not supported")
    if "ending_variant" in scene_pack and scene_pack.get("ending_variant") not in {"insight_close", "homework_close", "action_close", "checklist_close", "offer_close"}:
        errors.append(f"ending_variant {scene_pack.get('ending_variant')!r} is not supported")
    if "visual_strategy" in scene_pack and not isinstance(scene_pack.get("visual_strategy"), dict):
        errors.append("visual_strategy must be an object when present")
    return errors
