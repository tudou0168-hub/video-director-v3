"""Visual beat planner — cadence follows role and scene duration."""
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
        beats = _build_scene_beats(sid, role, duration)

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


def _build_scene_beats(scene_id: str, role: str, duration: float) -> list[dict[str, Any]]:
    interval = 2.0 if role == "hook" else 3.5 if role in {"method", "evidence", "proof"} else 4.0
    beat_type = {
        "hook": "headline_pulse",
        "pain": "card_focus",
        "method": "step_reveal",
        "evidence": "proof_focus",
        "proof": "compare_shift",
        "cta": "check_pop",
    }.get(role, "panel_shift")

    beats = [
        {"beat_id": f"{scene_id}_VB01", "type": "scene_enter", "start": 0.0, "duration": round(min(1.0, duration), 2)}
    ]
    cursor = min(1.0, duration)
    beat_index = 2

    while cursor < max(duration - 0.45, 0):
        beat_duration = min(1.0, max(duration - cursor, 0.45))
        beats.append({
            "beat_id": f"{scene_id}_VB{beat_index:02d}",
            "type": beat_type,
            "start": round(cursor, 2),
            "duration": round(beat_duration, 2),
        })
        beat_index += 1
        cursor += interval

    if beats[-1]["type"] != "scene_hold" and duration > beats[-1]["start"] + beats[-1]["duration"]:
        hold_start = round(beats[-1]["start"] + beats[-1]["duration"], 2)
        hold_duration = round(max(duration - hold_start, 0.0), 2)
        if hold_duration > 0:
            beats.append({
                "beat_id": f"{scene_id}_VB{beat_index:02d}",
                "type": "scene_hold",
                "start": hold_start,
                "duration": hold_duration,
            })

    return beats
