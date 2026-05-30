"""Visual beat planner — V3 simplified."""
import json
from pathlib import Path
from typing import Any


def plan_visual_beats(
    storyboard: dict[str, Any],
    design_profile: dict[str, Any],
) -> dict[str, Any]:
    """Plan visual beats from storyboard."""
    scenes = storyboard.get("scenes", [])
    visual_beats = []

    for scene in scenes:
        sid = scene.get("scene_id", "S01")
        role = scene.get("role", "explain")
        duration = float(scene.get("duration", 5.0))

        # Generate 2 visual beats per scene
        beats = []
        if role == "hook":
            beats = [
                {"beat_id": f"{sid}_VB01", "type": "headline_enter", "start": 0.0, "duration": 1.2},
                {"beat_id": f"{sid}_VB02", "type": "sub_element_fade", "start": 1.2, "duration": 0.8},
            ]
        elif role == "method":
            beats = [
                {"beat_id": f"{sid}_VB01", "type": "component_enter", "start": 0.3, "duration": 1.0},
                {"beat_id": f"{sid}_VB02", "type": "component_stagger", "start": 1.3, "duration": 1.0},
            ]
        else:
            beats = [
                {"beat_id": f"{sid}_VB01", "type": "fade_in", "start": 0.0, "duration": 0.8},
                {"beat_id": f"{sid}_VB02", "type": "hold", "start": 0.8, "duration": duration - 0.8},
            ]

        visual_beats.append({
            "scene_id": sid,
            "role": role,
            "visual_beats": beats,
        })

    return {"scenes": visual_beats}


def write_outputs(visual_beats: dict[str, Any], project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "visual_beats.json").write_text(
        json.dumps(visual_beats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )