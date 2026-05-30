"""Caption beat generator — V3."""
from pathlib import Path
from typing import Any


def generate_caption_beats(
    project_dir: Path,
    narration_plan: dict[str, Any],
    audio_timeline: dict[str, Any],
    motion_storyboard: dict[str, Any],
) -> dict[str, Any]:
    """Generate caption_beats.json from narration plan and audio timeline."""
    scenes = motion_storyboard.get("scenes", [])
    sentence_timings = audio_timeline.get("sentence_timings", [])

    beats = []
    for scene in scenes:
        sid = scene.get("scene_id", "S01")
        scene_start = float(scene.get("start", 0))
        scene_duration = float(scene.get("duration", 0))
        narration = scene.get("narration", "").strip()

        if not narration:
            # Use sentence timings to find matching narration
            scene_end = scene_start + scene_duration
            for st in sentence_timings:
                t_start = float(st.get("start", 0))
                t_end = float(st.get("end", 0))
                if t_start < scene_end and t_end > scene_start:
                    if not narration:
                        narration = st.get("text", "")

        if not narration:
            continue

        # Split into 2 caption beats per scene
        text_parts = _split_text(narration, 2)
        beat_count = len(text_parts)
        beat_duration = scene_duration / beat_count if beat_count > 0 else scene_duration

        for i, text in enumerate(text_parts):
            caption_id = f"{sid}_C{i+1:02d}"
            beat_start = scene_start + (i * beat_duration)
            beat_duration_actual = beat_duration
            if i == beat_count - 1:
                beat_duration_actual = (scene_start + scene_duration) - beat_start

            beats.append({
                "scene_id": sid,
                "caption_id": caption_id,
                "start": round(beat_start, 2),
                "duration": round(beat_duration_actual, 2),
                "text": text,
                "source_sentence": text,
                "visible": True,
            })

    result = {"caption_beats": beats, "caption_count": len(beats)}
    # Write to project_dir
    (project_dir / "caption_beats.json").write_text(
        __import__("json").dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def _split_text(text: str, min_parts: int = 2) -> list[str]:
    """Split text into caption-ready parts."""
    import re
    chinese_chars = len(re.findall(r"[一-鿿]", text))
    # Target ~20 chars per beat
    target_per_beat = max(15, chinese_chars // min_parts)

    parts = []
    sentences = re.split(r"[，,。；;]", text)
    current = ""
    current_chars = 0

    for sent in sentences:
        sent_chars = len(re.findall(r"[一-鿿]", sent))
        if current_chars + sent_chars > target_per_beat and current:
            parts.append(current.strip())
            current = sent
            current_chars = sent_chars
        else:
            current += " " + sent if current else sent
            current_chars += sent_chars

    if current.strip():
        parts.append(current.strip())

    # Ensure minimum parts
    while len(parts) < min_parts:
        parts.append(parts[-1] if parts else text[:20])

    return parts[:min_parts]