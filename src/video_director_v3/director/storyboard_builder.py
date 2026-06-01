"""Storyboard builder — V3 dynamic mode (P3.2.2).

Builds motion storyboard by clustering sentence-level audio timings into
scenes whose count, duration and visual template are content-driven, not
hard-coded to 6/7/8.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from video_director_v3.templates.scene_protocol import pick_template_for_role, register_seed_templates


MAX_BODY_SCENE_SECONDS = 7.5
MIN_SCENE_SECONDS = 1.5


def _format_scene_id(index: int) -> str:
    return f"S{index + 1:02d}"


def _cluster_sentences(
    sentences: list[dict[str, Any]],
    timings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Cluster sentences into scenes by adjacent role and duration budget.

    Rules:
      - First sentence is always its own scene (Hook).
      - Last sentence is always its own scene (CTA).
      - Middle sentences cluster consecutive same-role into one scene.
      - If a cluster would exceed MAX_BODY_SCENE_SECONDS, split by sentence.
      - If a single sentence exceeds MAX_BODY_SCENE_SECONDS, keep as one scene.
    """
    if not sentences:
        return []

    timing_by_sid = {t.get("sentence_id", ""): t for t in timings}
    scenes: list[dict[str, Any]] = []
    cluster_indices: list[int] = []
    cursor_start = 0.0
    current_role: str | None = None

    def _flush(cluster: list[int], end_time: float) -> None:
        if not cluster:
            return
        start_time = float(timings[cluster[0]].get("start", 0))
        last_idx = cluster[-1]
        end_time = float(timings[last_idx].get("end", end_time))
        duration = round(max(end_time - start_time, MIN_SCENE_SECONDS), 3)
        role = sentences[last_idx].get("role", "explain")
        narration = " ".join(
            sentences[i].get("text", "").strip()
            for i in cluster
            if sentences[i].get("text")
        )
        sentence_ids = [sentences[i].get("sentence_id", "") for i in cluster]
        scenes.append({
            "scene_id": _format_scene_id(len(scenes)),
            "role": role,
            "start": round(start_time, 3),
            "duration": duration,
            "end": round(end_time, 3),
            "narration": narration.strip(),
            "sentence_ids": sentence_ids,
        })

    first_idx = 0
    first_role = sentences[first_idx].get("role", "hook")
    scenes.append({
        "scene_id": _format_scene_id(0),
        "role": first_role,
        "start": 0.0,
        "duration": round(float(timings[first_idx].get("duration", 0)), 3),
        "end": round(float(timings[first_idx].get("end", 0)), 3),
        "narration": sentences[first_idx].get("text", ""),
        "sentence_ids": [sentences[first_idx].get("sentence_id", "")],
    })

    middle_indices = list(range(1, len(sentences) - 1))
    cluster: list[int] = []
    cluster_start_time = 0.0

    for idx in middle_indices:
        sentence = sentences[idx]
        timing = timings[idx]
        role = sentence.get("role", "explain")
        start_t = float(timing.get("start", 0))
        end_t = float(timing.get("end", start_t))
        if not cluster:
            cluster = [idx]
            cluster_start_time = start_t
            current_role = role
            continue
        same_role = role == current_role
        proposed_end = end_t
        would_exceed = (proposed_end - cluster_start_time) > MAX_BODY_SCENE_SECONDS
        if same_role and not would_exceed:
            cluster.append(idx)
        else:
            _flush(cluster, float(timings[cluster[-1]].get("end", cluster_start_time)))
            cluster = [idx]
            cluster_start_time = start_t
            current_role = role
    if cluster:
        _flush(cluster, float(timings[cluster[-1]].get("end", cluster_start_time)))

    if len(sentences) > 1:
        last_idx = len(sentences) - 1
        last_sentence = sentences[last_idx]
        last_timing = timings[last_idx]
        scenes.append({
            "scene_id": _format_scene_id(len(scenes)),
            "role": last_sentence.get("role", "cta"),
            "start": round(float(last_timing.get("start", 0)), 3),
            "duration": round(float(last_timing.get("duration", 0)), 3),
            "end": round(float(last_timing.get("end", 0)), 3),
            "narration": last_sentence.get("text", ""),
            "sentence_ids": [last_sentence.get("sentence_id", "")],
        })

    last_scene = scenes[-1]
    last_scene["end"] = last_scene["start"] + last_scene["duration"]
    return scenes


def _assign_visual_templates(scenes: list[dict[str, Any]]) -> None:
    """Mutate scenes in-place: attach visual_template and accent by role."""
    register_seed_templates()
    for scene in scenes:
        role = scene.get("role", "explain")
        tpl = pick_template_for_role(role)
        scene["scene_framework"] = tpl.get("id", "")
        scene["visual_template"] = tpl.get("render_template", "hook_big_claim")
        fixture = tpl.get("preview_fixture", {}) or {}
        scene["accent"] = fixture.get("accent", "#25D8FF")
        scene["density"] = tpl.get("density", "medium")


def build_motion_storyboard(
    director_output: dict[str, Any] | None = None,
    aspect_ratio: str = "9:16",
    platform_profile: str = "douyin",
    target_duration: float = 40.0,
    *,
    narration_plan: dict[str, Any] | None = None,
    audio_timeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build motion storyboard. Dynamic when narration_plan + audio_timeline given."""
    project_id = "unknown"
    if narration_plan:
        project_id = narration_plan.get("project_id", project_id)
    elif director_output:
        project_id = director_output.get("project_id", project_id)

    scenes: list[dict[str, Any]] = []
    if narration_plan and audio_timeline:
        sentences = narration_plan.get("sentence_list", [])
        timings = audio_timeline.get("sentence_timings", [])
        if sentences and timings and len(sentences) == len(timings):
            scenes = _cluster_sentences(sentences, timings)
            _assign_visual_templates(scenes)

    if not scenes:
        legacy = (director_output or {}).get("scenes", []) or []
        if legacy:
            scenes = legacy
            _assign_visual_templates(scenes)
        else:
            scene_roles = ["hook", "pain", "method", "method", "evidence", "proof", "cta"]
            scene_dur = target_duration / len(scene_roles)
            cursor = 0.0
            for i, role in enumerate(scene_roles):
                scenes.append({
                    "scene_id": _format_scene_id(i),
                    "role": role,
                    "start": round(cursor, 2),
                    "duration": round(scene_dur, 2),
                    "layout_type": f"{role}_centered",
                    "components": [],
                    "visual_beats": [],
                    "motion_events": [],
                })
                cursor += scene_dur

    return {
        "project": {
            "project_id": project_id,
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
