"""Semantic transition planner — dynamic scene-to-scene transitions."""
from __future__ import annotations

from typing import Any


ROLE_PAIR_TRANSITIONS: dict[tuple[str, str], tuple[str, str, str]] = {
    ("hook", "pain"): ("hook_to_problem", "scan_reveal", "从 Hook 到问题揭示"),
    ("pain", "method"): ("problem_to_method", "cards_to_flow", "从问题到解决方案"),
    ("method", "method"): ("method_expand", "line_draw_bridge", "方法递进"),
    ("method", "evidence"): ("method_to_evidence", "flow_to_table", "从方法到证据"),
    ("evidence", "proof"): ("evidence_to_proof", "metric_to_compare", "从证据到结果"),
    ("proof", "cta"): ("proof_to_cta", "final_hold_fade", "从结果到行动号召"),
}

ROLE_DEFAULTS: dict[str, tuple[str, str, str]] = {
    "hook": ("hook_shift", "scan_reveal", "Hook 切换"),
    "pain": ("pain_shift", "glow_crossfade", "痛点切换"),
    "method": ("method_shift", "cards_to_flow", "方法切换"),
    "evidence": ("evidence_shift", "flow_to_table", "证据切换"),
    "proof": ("proof_shift", "metric_to_compare", "结果切换"),
    "cta": ("cta_shift", "final_hold_fade", "CTA 切换"),
}


def all_transitions() -> list[tuple[str, str, str]]:
    return list(ROLE_PAIR_TRANSITIONS.values())


def _pick_transition(from_role: str, to_role: str) -> tuple[str, str, str]:
    return (
        ROLE_PAIR_TRANSITIONS.get((from_role, to_role))
        or ROLE_DEFAULTS.get(to_role)
        or ("scene_bridge", "soft_wipe", "自然过渡")
    )


def build_semantic_transitions(storyboard_scenes: list[dict[str, Any]], target_duration: float) -> dict[str, Any]:
    """Build semantic_transitions.json from adjacent storyboard scenes."""
    scenes = storyboard_scenes
    transitions_list = []

    for idx, (from_scene, to_scene) in enumerate(zip(scenes, scenes[1:]), start=1):
        from_role = from_scene.get("role", "explain")
        to_role = to_scene.get("role", "explain")
        transition_type, visual_action, semantic_label = _pick_transition(from_role, to_role)
        duration = 0.32 if from_role == "hook" else 0.4
        from_end = float(from_scene.get("end", float(from_scene.get("start", 0)) + float(from_scene.get("duration", 0))))
        start_time = max(float(from_scene.get("start", 0)), from_end - duration)

        transitions_list.append({
            "transition_id": f"T{idx:02d}",
            "from_scene": from_scene.get("scene_id", ""),
            "to_scene": to_scene.get("scene_id", ""),
            "type": transition_type,
            "start": round(start_time, 2),
            "duration": duration,
            "visual_action": visual_action,
            "semantic_label": semantic_label,
            "binding_status": "bound",
            "gsap_code": "",
        })

    return {
        "transitions": transitions_list,
        "transition_count": len(transitions_list),
        "bound_transition_count": len(transitions_list),
        "status": "PASS",
    }
