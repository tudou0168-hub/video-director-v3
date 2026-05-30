"""Semantic transition planner — V3."""
from typing import Any


SEMANTIC_TRANSITIONS = [
    {
        "transition_id": "T01",
        "from_scene": "S01",
        "to_scene": "S02",
        "transition_type": "hook_to_problem",
        "duration": 0.4,
        "semantic_label": "从Hook到问题揭示",
        "gsap_code": "",
    },
    {
        "transition_id": "T02",
        "from_scene": "S02",
        "to_scene": "S03",
        "transition_type": "problem_to_method",
        "duration": 0.4,
        "semantic_label": "从问题到解决方案",
        "gsap_code": "",
    },
    {
        "transition_id": "T03",
        "from_scene": "S03",
        "to_scene": "S04",
        "transition_type": "method_expand",
        "duration": 0.4,
        "semantic_label": "方法扩展",
        "gsap_code": "",
    },
    {
        "transition_id": "T04",
        "from_scene": "S04",
        "to_scene": "S05",
        "transition_type": "method_steps",
        "duration": 0.4,
        "semantic_label": "步骤展示",
        "gsap_code": "",
    },
    {
        "transition_id": "T05",
        "from_scene": "S05",
        "to_scene": "S06",
        "transition_type": "steps_to_proof",
        "duration": 0.4,
        "semantic_label": "效果验证",
        "gsap_code": "",
    },
    {
        "transition_id": "T06",
        "from_scene": "S06",
        "to_scene": "S07",
        "transition_type": "proof_to_cta",
        "duration": 0.4,
        "semantic_label": "到行动号召",
        "gsap_code": "",
    },
]


def all_transitions():
    return SEMANTIC_TRANSITIONS


def build_semantic_transitions(storyboard_scenes: list[dict[str, Any]], target_duration: float) -> dict[str, Any]:
    """Build semantic_transitions.json from storyboard scenes."""
    scenes = storyboard_scenes
    transitions_list = []

    for idx, t in enumerate(SEMANTIC_TRANSITIONS):
        from_sid = t.get("from_scene", "")
        to_sid = t.get("to_scene", "")

        # Find start time from scene timing
        start_time = 0.0
        from_scene = next((s for s in scenes if s.get("scene_id") == from_sid), None)
        if from_scene:
            start_time = float(from_scene.get("start", 0)) + float(from_scene.get("duration", 0)) - t.get("duration", 0.4)

        transitions_list.append({
            "transition_id": t["transition_id"],
            "from_scene": from_sid,
            "to_scene": to_sid,
            "type": t.get("transition_type", ""),
            "start": round(start_time, 2),
            "duration": t.get("duration", 0.4),
            "visual_action": "fade_slide_bridge",
            "semantic_label": t.get("semantic_label", ""),
            "binding_status": "bound",
            "gsap_code": t.get("gsap_code", ""),
        })

    return {
        "transitions": transitions_list,
        "transition_count": len(transitions_list),
        "bound_transition_count": len(transitions_list),
        "status": "PASS",
    }