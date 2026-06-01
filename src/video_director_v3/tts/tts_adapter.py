#!/usr/bin/env python3
"""V1.10 TTS adapter — migrated to V3."""
from __future__ import annotations

import json
import os
import subprocess
import uuid
from pathlib import Path
from typing import Any

from video_director_v3.config import MAX_NARRATION_SECONDS

def _this_run_id() -> str:
    return os.environ.get("VD_RUN_ID") or str(uuid.uuid4())[:8]


def clean_audio_outputs_for_run(audio_dir: Path) -> None:
    audio_dir.mkdir(parents=True, exist_ok=True)
    for fname in ["voiceover.mp3", "voiceover.wav", "voiceover.m4a",
                  "tts_result.json", "mock_voiceover.json", "audio_timeline.json"]:
        f = audio_dir / fname
        if f.exists():
            f.unlink()


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def render_edge_tts(text: str, output_path: Path, voice: str,
                    rate: str, pitch: str) -> tuple[bool, str, str]:
    command = ["edge-tts", "--voice", voice, "--rate", rate, "--pitch", pitch,
               "--text", text, "--write-media", str(output_path)]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired as e:
        return False, "edge-tts timed out after 120s", f"TimeoutExpired: {e}"
    except FileNotFoundError as e:
        return False, f"edge-tts not found: {e}", f"FileNotFoundError: {e}"
    except Exception as e:
        return False, f"edge-tts error: {e}", f"{type(e).__name__}: {e}"
    if completed.returncode == 0 and output_path.exists():
        return True, (completed.stderr or completed.stdout or "ok")[-500:], ""
    return False, (completed.stderr or completed.stdout or "")[-500:], f"returncode={completed.returncode}"


def render_system_say(text: str, output_path: Path, rate_arg: str = "") -> tuple[bool, str, str]:
    cmd = ["say"]
    if rate_arg:
        for tok in rate_arg.split():
            cmd.append(tok)
    cmd.extend(["-o", str(output_path), "--"])
    try:
        completed = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True, timeout=120)
    except FileNotFoundError:
        return False, "say not available", "FileNotFoundError"
    except subprocess.TimeoutExpired:
        return False, "say timed out", "TimeoutExpired"
    except Exception as e:
        return False, f"say error: {e}", f"{type(e).__name__}: {e}"
    if completed.returncode == 0 and output_path.exists():
        return True, "ok", ""
    return False, (completed.stderr.decode("utf-8", errors="replace") if completed.stderr else ""), f"returncode={completed.returncode}"


def build_audio_timeline(narration_plan: dict[str, Any]) -> dict[str, Any]:
    current = 0.0
    timings = []
    for sentence in narration_plan.get("sentence_list", []):
        duration = float(sentence.get("estimated_duration", 3.0))
        start = round(current, 2)
        end = round(start + duration, 2)
        timings.append({
            "sentence_id": sentence.get("sentence_id", ""),
            "text": sentence.get("text", ""),
            "start": start,
            "end": end,
            "duration": duration,
            "pause_after": sentence.get("pause_after", 0.0),
            "emphasis_words": sentence.get("emphasis_words", []),
        })
        current = end + float(sentence.get("pause_after", 0.0))
    return {"total_duration": round(current, 2), "sentence_timings": timings}


def scale_timeline_to_real(timeline: dict[str, Any], real_duration: float) -> dict[str, Any]:
    current_total = max(float(timeline.get("total_duration", 0.0)), 0.1)
    factor = real_duration / current_total
    timings = []
    cursor = 0.0
    for item in timeline.get("sentence_timings", []):
        duration = round(float(item["duration"]) * factor, 2)
        pause_after = round(float(item.get("pause_after", 0.0)) * factor, 2)
        start = round(cursor, 2)
        end = round(start + duration, 2)
        timings.append({**item, "start": start, "end": end, "duration": duration, "pause_after": pause_after})
        cursor = end + pause_after
    if timings:
        delta = round(real_duration - cursor, 2)
        timings[-1]["duration"] = round(max(0.5, timings[-1]["duration"] + delta), 2)
        timings[-1]["end"] = round(timings[-1]["start"] + timings[-1]["duration"], 2)
        timings[-1]["pause_after"] = 0.0
    return {"total_duration": real_duration, "sentence_timings": timings}


def _check_duration_contract(audio_path: Path) -> tuple[bool, str, float | None]:
    real_dur = ffprobe_duration(audio_path)
    if real_dur is None:
        return False, "ffprobe could not read audio duration", None
    if real_dur <= 0:
        return False, f"invalid audio duration: {real_dur:.2f}s", real_dur
    if real_dur > MAX_NARRATION_SECONDS:
        return False, f"natural-rate narration exceeds {MAX_NARRATION_SECONDS:.0f}s: {real_dur:.2f}s", real_dur
    return True, "ok", real_dur


def run_tts(
    narration_plan: dict[str, Any],
    project_dir: Path,
    mode: str = "edge_tts",
    edge_voice: str = "zh-CN-YunxiNeural",
    edge_rate: str = "+0%",
    edge_pitch: str = "-2Hz",
    allow_mock_audio: bool = False,
    run_id: str | None = None,
) -> dict[str, Any]:
    audio_dir = project_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    run_id = run_id or _this_run_id()
    os.environ["VD_RUN_ID"] = run_id
    clean_audio_outputs_for_run(audio_dir)

    original_timeline = build_audio_timeline(narration_plan)
    write_json(audio_dir / "audio_timeline.json", original_timeline)
    write_json(project_dir / "audio_timeline.json", original_timeline)

    if mode == "mock":
        result = {"mode": "mock", "status": "ok", "audio_path": None, "timeline": original_timeline,
                  "generated_this_run": True, "run_id": run_id, "message": "mock mode"}
        write_json(audio_dir / "tts_result.json", result)
        return result

    # Build text from sentences
    text_primary = "\n".join(s.get("text", "") for s in narration_plan.get("sentence_list", []))
    if mode == "edge_tts":
        target_1 = audio_dir / "voiceover.mp3"
        ok_1, msg_1, _ = render_edge_tts(text_primary, target_1, edge_voice, edge_rate, edge_pitch)
        if ok_1 and target_1.exists():
            ok_contract, reason_1, real_dur_1 = _check_duration_contract(target_1)
            if ok_contract:
                mark_audio_as_generated(target_1, run_id)
                timeline = scale_timeline_to_real(original_timeline, real_dur_1) if real_dur_1 else original_timeline
                write_json(audio_dir / "audio_timeline.json", timeline)
                write_json(project_dir / "audio_timeline.json", timeline)
                result = {"mode": "edge_tts", "status": "ok", "audio_path": str(target_1),
                          "timeline": timeline, "real_duration": real_dur_1,
                          "speaking_rate": edge_rate, "generated_this_run": True, "run_id": run_id,
                          "message": "edge_tts natural-rate ok"}
                write_json(audio_dir / "tts_result.json", result)
                return result

        # Fallback stays at the platform default speaking rate.
        for rate_arg in [""]:
                suffix = "_r200" if rate_arg else ""
                target_fb = audio_dir / f"voiceover{suffix}.aiff"
                ok_fb, msg_fb, _ = render_system_say(text_primary, target_fb, rate_arg)
                if ok_fb and target_fb.exists():
                    real_dur_fb = ffprobe_duration(target_fb)
                    ok_contract, reason_fb, _ = _check_duration_contract(target_fb)
                    if ok_contract:
                        mp3_path = audio_dir / "voiceover.mp3"
                        try:
                            subprocess.run(["ffmpeg", "-y", "-i", str(target_fb), "-codec:a", "libmp3lame", "-b:a", "192k", str(mp3_path)],
                                          capture_output=True, timeout=60)
                        except Exception:
                            pass
                        final_path = mp3_path if mp3_path.exists() else target_fb
                        final_dur = ffprobe_duration(final_path) if final_path.exists() else real_dur_fb
                        mark_audio_as_generated(final_path, run_id)
                        timeline = scale_timeline_to_real(original_timeline, final_dur)
                        write_json(audio_dir / "audio_timeline.json", timeline)
                        write_json(project_dir / "audio_timeline.json", timeline)
                        result = {"mode": f"system_say{rate_arg}", "status": "ok", "audio_path": str(final_path),
                                  "timeline": timeline, "real_duration": final_dur,
                                  "fallback_used": "system_say",
                                  "generated_this_run": True, "run_id": run_id, "message": "system_say fallback ok"}
                        write_json(audio_dir / "tts_result.json", result)
                        return result

        # All failed
        if allow_mock_audio:
            result = {"mode": mode, "status": "mock", "audio_path": None, "timeline": original_timeline,
                      "generated_this_run": True, "run_id": run_id, "message": "mock fallback"}
            write_json(audio_dir / "tts_result.json", result)
            return result
        result = {"mode": mode, "status": "failed", "audio_path": None, "timeline": original_timeline,
                  "generated_this_run": True, "run_id": run_id, "message": f"all TTS failed: {msg_1}"}
        write_json(audio_dir / "tts_result.json", result)
        return result

    if mode == "system_say":
        for rate_arg in [""]:
            suffix = "_r200" if rate_arg else ""
            target = audio_dir / f"voiceover{suffix}.aiff"
            ok, msg, _ = render_system_say(text_primary, target, rate_arg)
            if ok and target.exists():
                real_dur = ffprobe_duration(target)
                ok_contract, _, real_dur = _check_duration_contract(target)
                if ok_contract:
                    mp3_path = audio_dir / "voiceover.mp3"
                    try:
                        subprocess.run(["ffmpeg", "-y", "-i", str(target), "-codec:a", "libmp3lame", "-b:a", "192k", str(mp3_path)],
                                      capture_output=True, timeout=60)
                    except Exception:
                        pass
                    final_path = mp3_path if mp3_path.exists() else target
                    final_dur = ffprobe_duration(final_path) or real_dur
                    mark_audio_as_generated(final_path, run_id)
                    timeline = scale_timeline_to_real(original_timeline, final_dur)
                    write_json(audio_dir / "audio_timeline.json", timeline)
                    write_json(project_dir / "audio_timeline.json", timeline)
                    result = {"mode": f"system_say{rate_arg}", "status": "ok", "audio_path": str(final_path),
                              "timeline": timeline, "real_duration": final_dur,
                              "generated_this_run": True, "run_id": run_id, "message": "ok"}
                    write_json(audio_dir / "tts_result.json", result)
                    return result
        result = {"mode": "system_say", "status": "failed", "audio_path": None, "timeline": original_timeline,
                  "generated_this_run": True, "run_id": run_id, "message": "system_say failed"}
        write_json(audio_dir / "tts_result.json", result)
        return result

    result = {"mode": mode, "status": "failed", "audio_path": None, "timeline": original_timeline,
              "generated_this_run": True, "run_id": run_id, "message": f"unknown mode: {mode}"}
    write_json(audio_dir / "tts_result.json", result)
    return result


def mark_audio_as_generated(audio_path: Path, run_id: str) -> None:
    if audio_path.exists():
        os.utime(audio_path, None)
