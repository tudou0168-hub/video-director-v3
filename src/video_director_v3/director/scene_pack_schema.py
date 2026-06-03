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
    return errors
