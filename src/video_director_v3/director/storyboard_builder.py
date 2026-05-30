"""Storyboard builder — V3 simplified."""
import json
from pathlib import Path
from typing import Any


def build_motion_storyboard(
    director_output: dict[str, Any],
    aspect_ratio: str = "9:16",
    platform_profile: str = "douyin",
    target_duration: float = 40.0,
) -> dict[str, Any]:
    """Build motion storyboard from director output."""
    scenes = director_output.get("scenes", [])
    if not scenes:
        # Generate default scenes
        scene_roles = ["hook", "pain", "method", "method", "evidence", "proof", "cta"]
        total_scenes = len(scene_roles)
        scene_dur = target_duration / total_scenes
        cursor = 0.0
        scenes = []
        for i, role in enumerate(scene_roles):
            start = cursor
            scenes.append({
                "scene_id": f"S{i+1:02d}",
                "role": role,
                "start": round(start, 2),
                "duration": round(scene_dur, 2),
                "layout_type": f"{role}_centered",
                "components": [],
                "visual_beats": [],
                "motion_events": [],
            })
            cursor += scene_dur

    return {
        "project": {
            "project_id": director_output.get("project_id", "unknown"),
            "aspect_ratio": aspect_ratio,
            "platform": platform_profile,
            "duration": target_duration,
            "target_duration": target_duration,
        },
        "scenes": scenes,
    }


def write_outputs(storyboard: dict[str, Any], project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "motion_storyboard.json").write_text(
        json.dumps(storyboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )