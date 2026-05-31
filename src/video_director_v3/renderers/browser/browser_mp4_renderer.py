#!/usr/bin/env python3
"""Browser-based MP4 renderer — captures frames and encodes video with FFmpeg."""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any


# ─── FFmpeg helpers ────────────────────────────────────────────────────────────


def ffprobe_duration(path: Path) -> float | None:
    completed = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True,
    )
    if completed.returncode != 0:
        return None
    try:
        return round(float(completed.stdout.strip()), 2)
    except ValueError:
        return None


def ffprobe_has_stream(path: Path, stream_type: str) -> bool:
    """Check if output has video (v) or audio (a) stream."""
    cmd = ["ffprobe", "-v", "error", "-select_streams", stream_type,
           "-show_entries", "stream=codec_type", "-of", "json", str(path)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return False
        data = json.loads(result.stdout)
        return len(data.get("streams", [])) > 0
    except Exception:
        return False


def run_ffmpeg(cmd: list[str], timeout: int = 300) -> tuple[bool, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        ok = result.returncode == 0
        msg = result.stderr if not ok else "ok"
        return ok, msg[-500:] if msg else "ok"
    except subprocess.TimeoutExpired:
        return False, "ffmpeg timed out"
    except Exception as e:
        return False, str(e)


# ─── Frame capture ─────────────────────────────────────────────────────────────


async def _capture_frame(
    page,
    ts: float,
    frame_index: int,
    output_dir: Path,
    clean_mode: bool = False,
) -> dict[str, Any]:
    frame_name = f"frame_{frame_index:06d}.png"
    output_path = output_dir / frame_name

    await page.evaluate(f"""
        () => {{
            const tl = window.__timelines["combined"];
            if (tl) {{ tl.seek({ts}); tl.pause(); }}
        }}
    """)
    await page.wait_for_timeout(300)
    await page.screenshot(path=str(output_path), full_page=False)

    exists = output_path.exists()
    size = output_path.stat().st_size if exists else 0

    return {
        "frame_index": frame_index,
        "timestamp": ts,
        "frame_name": frame_name,
        "path": str(output_path),
        "exists": exists,
        "size": size,
    }


async def _capture_frame_sequence(
    html_path: str,
    output_dir: Path,
    fps: int = 25,
    duration: float = 40.0,
    clean_mode: bool = False,
) -> dict[str, Any]:
    """Capture frame sequence from HTML using Playwright."""
    frame_duration = 1.0 / fps
    total_frames = int(duration * fps)
    timestamps = [round(i * frame_duration, 4) for i in range(total_frames)]

    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    frames = []

    async with asyncio.timeout(600):
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1080, "height": 1920})

            html_file = Path(html_path)
            await page.goto(
                f"file://{html_file.absolute()}",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            await page.wait_for_timeout(5000)

            # Inject clean mode CSS to hide debug controls
            if clean_mode:
                await page.evaluate("""
                    () => {
                        const style = document.createElement('style');
                        style.textContent = `
                            #combined-progress, #combined-hud, #combined-time, #combined-controls, .scene-label {
                                display: none !important;
                            }
                            #combined-captions {
                                left: 72px !important;
                                right: 72px !important;
                                transform: none !important;
                            }
                            .caption-beat {
                                left: 0 !important;
                                right: 0 !important;
                                width: auto !important;
                            }
                        `;
                        document.head.appendChild(style);
                    }
                """)

            timeline_ok = await page.evaluate("""
                () => !!(window.__timelines && window.__timelines["combined"])
            """)
            if not timeline_ok:
                await browser.close()
                return {
                    "status": "FAIL",
                    "error": "window.__timelines['combined'] not found",
                    "frames": [],
                    "frames_expected": total_frames,
                    "frames_generated": 0,
                    "frames_dir": str(frames_dir),
                }

            for i, ts in enumerate(timestamps):
                frame_result = await _capture_frame(page, ts, i + 1, frames_dir)
                frames.append(frame_result)
                if i % 25 == 0:
                    await page.wait_for_timeout(0)  # yield to event loop

            await browser.close()

    ok_frames = [f for f in frames if f["exists"] and f["size"] > 1000]
    return {
        "status": "PASS" if len(ok_frames) >= total_frames * 0.95 else "FAIL",
        "frames": frames,
        "frames_expected": total_frames,
        "frames_generated": len(ok_frames),
        "frames_dir": str(frames_dir),
    }


# ─── Video encoding ─────────────────────────────────────────────────────────────


def encode_silent_video(
    frames_dir: Path,
    output_path: Path,
    fps: int = 25,
    width: int = 1080,
    height: int = 1920,
) -> tuple[bool, str]:
    """Use FFmpeg to encode frame sequence into MP4."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%06d.png"),
        "-vf", f"scale=1080:1920",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-an",
        str(output_path),
    ]
    return run_ffmpeg(cmd, timeout=300)


def mux_audio(
    silent_video: Path,
    audio_path: Path,
    output_path: Path,
) -> tuple[bool, str]:
    """Use FFmpeg to mux audio with silent video."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(silent_video),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path),
    ]
    return run_ffmpeg(cmd, timeout=120)


# ─── Main renderer ─────────────────────────────────────────────────────────────


async def render_browser_mp4(
    project_dir: Path,
    fps: int = 25,
    smoke_seconds: float | None = None,
    progress_callback=None,
    clean_mode: bool = True,
    keep_frames: bool = False,
) -> dict[str, Any]:
    """Render MP4 from combined/index.html using Playwright + FFmpeg.

    Args:
        project_dir: Path to project directory
        fps: frames per second for output video
        smoke_seconds: if set, only render this many seconds (smoke test)
        progress_callback: optional callable(frame_count, total) for progress
        clean_mode: if True, inject CSS to hide debug controls (default: True)
        keep_frames: if True, keep frames/ directory after render (default: False)

    Returns render report dict.
    """
    # Check prerequisites
    combined_html = project_dir / "combined" / "index.html"
    if not combined_html.exists():
        return {"status": "FAIL", "error": f"combined/index.html not found at {combined_html}"}

    # Resolve audio
    audio_candidates = [
        project_dir / "audio" / "voiceover.mp3",
        project_dir / "combined" / "assets" / "voiceover.mp3",
    ]
    audio_path = next((p for p in audio_candidates if p.exists()), None)
    if not audio_path:
        return {
            "status": "FAIL",
            "error": f"voiceover.mp3 not found in {[str(p) for p in audio_candidates]}",
        }

    # Determine duration from audio
    audio_duration = ffprobe_duration(audio_path)
    if audio_duration is None:
        return {"status": "FAIL", "error": "Cannot determine audio duration via ffprobe"}

    render_duration = smoke_seconds if smoke_seconds is not None else audio_duration

    # Verify audio duration contract for full render
    if smoke_seconds is None and not (38.0 <= audio_duration <= 43.0):
        return {
            "status": "FAIL",
            "error": f"Audio duration {audio_duration:.2f}s outside contract 38-43s",
        }

    # Output dirs
    is_smoke = smoke_seconds is not None
    rendered_dir = project_dir / ("rendered_smoke" if is_smoke else "rendered")
    rendered_dir.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Capture frames ─────────────────────────────────────────────
    capture_result = await _capture_frame_sequence(
        html_path=str(combined_html),
        output_dir=rendered_dir,
        fps=fps,
        duration=render_duration,
        clean_mode=clean_mode,
    )

    if capture_result["status"] == "FAIL":
        return {
            "status": "FAIL",
            "error": f"Frame capture failed: {capture_result.get('error')}",
            "capture_result": capture_result,
        }

    frames_generated = capture_result["frames_generated"]
    frames_expected = capture_result["frames_expected"]
    frames_dir = Path(capture_result["frames_dir"])

    if progress_callback:
        progress_callback(frames_generated, frames_expected)

    # ── Step 2: Encode silent video ───────────────────────────────────────
    silent_video = rendered_dir / "silent_video.mp4"
    ok, msg = encode_silent_video(
        frames_dir=frames_dir,
        output_path=silent_video,
        fps=fps,
    )
    if not ok:
        return {"status": "FAIL", "error": f"FFmpeg encode failed: {msg}"}

    # ── Step 3: Mux audio ──────────────────────────────────────────────────
    final_video = rendered_dir / ("final_video_smoke.mp4" if is_smoke else "final_video.mp4")
    ok, msg = mux_audio(silent_video, audio_path, final_video)
    if not ok:
        return {"status": "FAIL", "error": f"FFmpeg mux failed: {msg}"}

    # ── Step 4: Verify output ─────────────────────────────────────────────
    final_duration = ffprobe_duration(final_video)
    has_video = ffprobe_has_stream(final_video, "v")
    has_audio = ffprobe_has_stream(final_video, "a")

    # ── Step 5: Cleanup frames cache ─────────────────────────────────────
    frames_cache_cleaned = False
    frames_cache_exists_after = frames_dir.exists() and any(frames_dir.iterdir()) if frames_dir.exists() else False
    if not keep_frames and frames_dir.exists():
        import shutil
        shutil.rmtree(frames_dir)
        frames_cache_cleaned = True
        frames_cache_exists_after = False

    # Determine clean_render status
    clean_render_status = "PASS"
    clean_render_issues = []
    if not clean_mode:
        clean_render_issues.append("clean_mode was disabled")
    if frames_cache_exists_after:
        clean_render_status = "FAIL"
        clean_render_issues.append("frames/ directory still exists after render")
    if clean_mode and frames_dir.exists() and not any(frames_dir.iterdir()):
        # frames dir exists but is empty - OK
        pass

    render_status = "PASS"
    issues = []
    if not has_video:
        render_status = "FAIL"
        issues.append("No video stream in final output")
    if not has_audio:
        render_status = "FAIL"
        issues.append("No audio stream in final output")
    if final_duration and smoke_seconds is None:
        if not (38.0 <= final_duration <= 43.0):
            issues.append(f"Final duration {final_duration:.2f}s outside contract")
    if frames_generated < frames_expected * 0.95:
        issues.append(f"Only {frames_generated}/{frames_expected} frames captured")
    if clean_render_status == "FAIL":
        render_status = "FAIL"
        issues.extend(clean_render_issues)

    # Count final_review_frames
    final_review_frames_dir = project_dir / "final_review_frames"
    final_review_frames_count = 0
    if final_review_frames_dir.exists():
        final_review_frames_count = len(list(final_review_frames_dir.iterdir()))

    return {
        "status": render_status,
        "project_id": project_dir.name,
        "render_path": "browser_frame_sequence",
        "combined_index": str(combined_html),
        "audio_source": str(audio_path),
        "duration": final_duration or 0.0,
        "fps": fps,
        "viewport": {"width": 1080, "height": 1920},
        "frames_expected": frames_expected,
        "frames_generated": frames_generated,
        "frames_dir": str(frames_dir),
        "silent_video": str(silent_video),
        "final_video": str(final_video),
        "final_video_has_video_stream": has_video,
        "final_video_has_audio_stream": has_audio,
        "final_video_duration": final_duration or 0.0,
        "render_status": render_status,
        "issues": issues,
        # Clean render fields
        "clean_render_status": clean_render_status,
        "debug_controls_hidden": clean_mode,
        "captions_layout_fixed": clean_mode,
        "frames_cache_cleaned": frames_cache_cleaned,
        "frames_cache_path": str(frames_dir),
        "frames_cache_exists_after_render": frames_cache_exists_after,
        "final_review_frames_count": final_review_frames_count,
        "clean_render_issues": clean_render_issues,
    }


def write_render_report(report: dict[str, Any], project_dir: Path, is_smoke: bool = False) -> None:
    rendered_dir = project_dir / ("rendered_smoke" if is_smoke else "rendered")
    report_path = rendered_dir / "render_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")