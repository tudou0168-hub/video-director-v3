"""Render a Studio-native HyperFrames project and publish a verified MP4."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from video_director_v3.config import MAX_SYNC_DRIFT_SECONDS


def _run(command: list[str], timeout: int = 900) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def ffprobe_duration(path: Path) -> float | None:
    result = _run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path),
    ], timeout=30)
    if result.returncode != 0:
        return None
    try:
        return round(float(result.stdout.strip()), 3)
    except ValueError:
        return None


def ffprobe_has_stream(path: Path, stream_type: str) -> bool:
    result = _run([
        "ffprobe", "-v", "error", "-select_streams", stream_type,
        "-show_entries", "stream=codec_type", "-of", "json", str(path),
    ], timeout=30)
    if result.returncode != 0:
        return False
    return bool(json.loads(result.stdout).get("streams", []))


def measure_volume(path: Path) -> dict[str, Any]:
    result = _run([
        "ffmpeg", "-i", str(path), "-af", "volumedetect", "-f", "null", "/dev/null",
    ], timeout=120)
    output = result.stderr
    values: dict[str, Any] = {"checked": result.returncode == 0}
    for key in ("mean_volume", "max_volume"):
        marker = f"{key}: "
        line = next((line for line in output.splitlines() if marker in line), "")
        values[key] = line.split(marker, 1)[1].strip() if marker in line else None
    return values


def _last_end(items: list[dict[str, Any]], start_key: str, end_key: str, duration_key: str | None = None) -> float:
    ends = []
    for item in items:
        if end_key in item:
            ends.append(float(item[end_key]))
        elif duration_key and start_key in item and duration_key in item:
            ends.append(float(item[start_key]) + float(item[duration_key]))
    return round(max(ends, default=0.0), 3)


def read_timeline_ends(timeline_dir: Path) -> tuple[float, float]:
    data_dir = timeline_dir / "data"
    captions = json.loads((data_dir / "caption_beats.json").read_text(encoding="utf-8"))
    director = json.loads((data_dir / "director_timeline.json").read_text(encoding="utf-8"))
    caption_items = captions.get("beats", captions.get("caption_beats", []))
    scene_items = director.get("scenes", [])
    caption_end = _last_end(caption_items, "start_time", "end_time", "duration")
    if not caption_end:
        caption_end = _last_end(caption_items, "start", "end", "duration")
    scene_end = _last_end(scene_items, "start_time", "end_time", "duration")
    if not scene_end:
        scene_end = _last_end(scene_items, "start", "end", "duration")
    return caption_end, scene_end


def build_sync_report(
    *,
    audio_duration: float,
    video_duration: float,
    caption_end: float,
    scene_end: float,
    has_video: bool,
    has_audio: bool,
    volume: dict[str, Any] | None = None,
) -> dict[str, Any]:
    checks = {
        "audio_duration_seconds": round(audio_duration, 3),
        "video_duration_seconds": round(video_duration, 3),
        "caption_end_seconds": round(caption_end, 3),
        "scene_end_seconds": round(scene_end, 3),
        "video_audio_drift_seconds": round(abs(video_duration - audio_duration), 3),
        "caption_audio_drift_seconds": round(abs(caption_end - audio_duration), 3),
        "scene_audio_drift_seconds": round(abs(scene_end - audio_duration), 3),
        "has_video_stream": has_video,
        "has_audio_stream": has_audio,
        "volume": volume or {},
    }
    checks["max_drift_seconds"] = max(
        checks["video_audio_drift_seconds"],
        checks["caption_audio_drift_seconds"],
        checks["scene_audio_drift_seconds"],
    )
    issues = []
    if not has_video:
        issues.append("final video stream missing")
    if not has_audio:
        issues.append("final video audio stream missing")
    if checks["max_drift_seconds"] > MAX_SYNC_DRIFT_SECONDS:
        issues.append(f"sync drift exceeds {MAX_SYNC_DRIFT_SECONDS:.1f}s")
    return {"status": "FAIL" if issues else "PASS", "checks": checks, "issues": issues}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _build_smoke_timeline(timeline_dir: Path, rendered_dir: Path, duration: float) -> Path:
    smoke_dir = rendered_dir / "_smoke_timeline"
    if smoke_dir.exists():
        shutil.rmtree(smoke_dir)
    shutil.copytree(timeline_dir, smoke_dir, ignore=shutil.ignore_patterns("snapshots"))
    index_path = smoke_dir / "index.html"
    html = index_path.read_text(encoding="utf-8")

    def trim_block(match: re.Match[str]) -> str:
        block = match.group(0)
        start_match = re.search(r'data-start="([^"]+)"', block)
        duration_match = re.search(r'data-duration="([^"]+)"', block)
        if not start_match or not duration_match:
            return block
        start = float(start_match.group(1))
        clip_duration = float(duration_match.group(1))
        if start >= duration:
            return ""
        trimmed = min(clip_duration, max(duration - start - 0.001, 0))
        return block[:duration_match.start(1)] + str(round(trimmed, 3)) + block[duration_match.end(1):]

    html = re.sub(r'<section id="scene-[^"]+"[^>]*>.*?</section>', trim_block, html, flags=re.S)
    html = re.sub(r'<div id="caption-[^"]+"[^>]*>.*?</div>', trim_block, html, flags=re.S)
    html = re.sub(
        r'(<div id="root"[^>]*data-duration=")[^"]+',
        rf'\g<1>{duration}',
        html,
        count=1,
    )
    html = re.sub(
        r'(<audio id="voiceover-audio"[^>]*data-duration=")[^"]+',
        rf'\g<1>{duration}',
        html,
        count=1,
    )
    index_path.write_text(html, encoding="utf-8")
    return smoke_dir


def render_native_mp4(
    project_dir: Path,
    *,
    fps: int = 25,
    smoke_seconds: float | None = None,
    quality: str = "draft",
) -> dict[str, Any]:
    timeline_dir = project_dir / "hyperframes_timeline"
    audio_path = timeline_dir / "assets" / "voiceover.mp3"
    if not (timeline_dir / "index.html").exists():
        return {"status": "FAIL", "error": f"Native index missing: {timeline_dir / 'index.html'}"}
    if not audio_path.exists():
        return {"status": "FAIL", "error": f"Voiceover missing: {audio_path}"}

    audio_duration = ffprobe_duration(audio_path)
    if not audio_duration:
        return {"status": "FAIL", "error": f"Cannot probe voiceover: {audio_path}"}

    is_smoke = smoke_seconds is not None
    render_duration = min(float(smoke_seconds), audio_duration) if is_smoke else audio_duration
    rendered_dir = project_dir / ("rendered_smoke" if is_smoke else "rendered")
    rendered_dir.mkdir(parents=True, exist_ok=True)
    native_render = rendered_dir / "native_render.mp4"
    silent_video = rendered_dir / "silent_video.mp4"
    final_video = rendered_dir / ("final_video_smoke.mp4" if is_smoke else "final_video.mp4")
    render_timeline_dir = _build_smoke_timeline(timeline_dir, rendered_dir, render_duration) if is_smoke else timeline_dir

    render_result = _run([
        "npx", "hyperframes", "render", str(render_timeline_dir),
        "--output", str(native_render), "--fps", str(fps),
        "--quality", quality, "--workers", "1", "--strict",
    ])
    if render_result.returncode != 0:
        return {"status": "FAIL", "error": f"HyperFrames native render failed: {render_result.stderr[-1000:]}"}

    strip_result = _run([
        "ffmpeg", "-y", "-i", str(native_render), "-t", str(render_duration),
        "-c:v", "copy", "-an", str(silent_video),
    ], timeout=180)
    if strip_result.returncode != 0:
        return {"status": "FAIL", "error": f"Silent video extraction failed: {strip_result.stderr[-1000:]}"}

    mux_result = _run([
        "ffmpeg", "-y", "-i", str(silent_video), "-i", str(audio_path),
        "-t", str(render_duration), "-c:v", "copy", "-c:a", "aac",
        "-b:a", "192k", "-shortest", str(final_video),
    ], timeout=180)
    if mux_result.returncode != 0:
        return {"status": "FAIL", "error": f"Audio mux failed: {mux_result.stderr[-1000:]}"}

    video_duration = ffprobe_duration(final_video) or 0.0
    caption_end, scene_end = read_timeline_ends(timeline_dir)
    if is_smoke:
        caption_end = min(caption_end, render_duration)
        scene_end = min(scene_end, render_duration)
    sync_report = build_sync_report(
        audio_duration=render_duration,
        video_duration=video_duration,
        caption_end=caption_end,
        scene_end=scene_end,
        has_video=ffprobe_has_stream(final_video, "v"),
        has_audio=ffprobe_has_stream(final_video, "a"),
        volume=measure_volume(final_video),
    )
    _write_json(rendered_dir / "sync_report.json", sync_report)
    report = {
        "status": sync_report["status"],
        "render_status": sync_report["status"],
        "project_id": project_dir.name,
        "render_path": "hyperframes_studio_native",
        "timeline_dir": str(timeline_dir),
        "audio_source": str(audio_path),
        "native_render": str(native_render),
        "silent_video": str(silent_video),
        "final_video": str(final_video),
        "final_video_duration": video_duration,
        "final_video_has_video_stream": sync_report["checks"]["has_video_stream"],
        "final_video_has_audio_stream": sync_report["checks"]["has_audio_stream"],
        "sync_status": sync_report["status"],
        "sync_report": str(rendered_dir / "sync_report.json"),
        "issues": sync_report["issues"],
    }
    _write_json(rendered_dir / "render_report.json", report)
    if native_render.exists():
        native_render.unlink()
    if silent_video.exists():
        silent_video.unlink()
    if is_smoke and render_timeline_dir.exists():
        shutil.rmtree(render_timeline_dir)
    return report
