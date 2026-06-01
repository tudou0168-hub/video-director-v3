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
    for timing in sentence_timings:
        sentence_start = float(timing.get("start", 0))
        sentence_end = float(timing.get("end", sentence_start))
        sentence_duration = max(sentence_end - sentence_start, 0)
        narration = timing.get("text", "").strip()
        if not narration or sentence_duration <= 0:
            continue
        scene = next(
            (item for item in scenes if float(item.get("start", 0)) <= sentence_start < float(item.get("start", 0)) + float(item.get("duration", 0))),
            scenes[-1] if scenes else {},
        )
        sid = scene.get("scene_id", "S01")
        text_parts = _split_text(narration, 2 if len(narration) > 26 else 1)
        beat_count = len(text_parts)
        beat_duration = sentence_duration / beat_count if beat_count > 0 else sentence_duration

        for i, text in enumerate(text_parts):
            caption_id = f"{timing.get('sentence_id', sid)}_C{i+1:02d}"
            beat_start = sentence_start + (i * beat_duration)
            beat_duration_actual = beat_duration
            if i == beat_count - 1:
                beat_duration_actual = sentence_end - beat_start

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
    target_per_beat = max(12, chinese_chars // max(min_parts, 1))

    parts = []
    chunks = [chunk.strip() for chunk in re.split(r"[，,。；;：:、]", text) if chunk.strip()]
    current = ""
    current_chars = 0

    for chunk in chunks:
        chunk_chars = len(re.findall(r"[一-鿿]", chunk))
        if current_chars + chunk_chars > target_per_beat and current:
            parts.append(current.strip())
            current = chunk
            current_chars = chunk_chars
        else:
            current += " " + chunk if current else chunk
            current_chars += chunk_chars

    if current.strip():
        parts.append(current.strip())

    if not parts:
        return [text.strip()]

    if len(parts) == 1 and min_parts > 1 and chinese_chars >= 18:
        midpoint = max(1, len(text) // 2)
        split_at = max(text.rfind("，", 0, midpoint), text.rfind("：", 0, midpoint), text.rfind(" ", 0, midpoint))
        if split_at <= 0:
            split_at = midpoint
        left = text[:split_at].strip(" ，：")
        right = text[split_at:].strip(" ，：")
        if left and right and left != right:
            return [left, right]

    return [part for part in parts[:max(min_parts, len(parts))] if part]
