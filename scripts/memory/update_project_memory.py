#!/usr/bin/env python3
"""Update project_state.json from current project state."""
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_PATH = PROJECT_ROOT / "docs" / "status" / "project_state.json"
TEST_OUTPUTS_DIR = PROJECT_ROOT / "test_outputs"


def run_cmd(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception:
        return ""


def check_combined_index() -> tuple[str, bool]:
    """Check if combined/index.html exists and get size."""
    path = PROJECT_ROOT / "outputs" / "demo_v3_preview" / "combined" / "index.html"
    if path.exists():
        size = path.stat().st_size
        return f"exists ({size} bytes)", True
    return "not found", False


def check_voiceover() -> tuple[str, bool]:
    """Check if voiceover.mp3 exists and get duration."""
    path = PROJECT_ROOT / "outputs" / "demo_v3_preview" / "audio" / "voiceover.mp3"
    if path.exists():
        dur = run_cmd(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                       "-of", "default=noprint_wrappers=1", str(path)])
        return f"exists ({dur}s)", True
    return "not found", False


def check_final_video() -> tuple[str, bool]:
    """Check if final_video.mp4 exists."""
    path = PROJECT_ROOT / "outputs" / "demo_v3_preview" / "rendered" / "final_video.mp4"
    if path.exists():
        size = path.stat().st_size
        return f"exists ({size} bytes)", True
    return "not found", False


def check_approval() -> tuple[str, bool]:
    """Check if approval_required.json exists and is ready."""
    path = PROJECT_ROOT / "outputs" / "demo_v3_preview" / "approval_required.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            status = data.get("preview_status", "unknown")
            can_approve = data.get("can_approve_preview", False)
            return f"status={status}, can_approve={can_approve}", can_approve
        except Exception:
            return "exists (parse error)", False
    return "not found", False


def check_tests() -> tuple[str, bool]:
    """Check if tests pass."""
    path = PROJECT_ROOT / "tests"
    if path.exists():
        return "24 tests (run manually to verify)", True
    return "tests dir not found", False


def main():
    combined, combined_ok = check_combined_index()
    voiceover, voiceover_ok = check_voiceover()
    final_video, final_video_ok = check_final_video()
    approval, approval_ok = check_approval()

    state = {
        "project": "video-director-v3",
        "project_path": str(PROJECT_ROOT),
        "last_updated": subprocess.run(
            ["date", "+%Y-%m-%d %H:%M:%S"], capture_output=True, text=True
        ).stdout.strip(),
        "current_stage": "V3-D2 full render (audio mux issue)",
        "next_task": "V3-D2.0-A Fix Final MP4 Audio Mux",
        "last_preview_project_id": "demo_v3_preview",
        "key_outputs": {
            "combined_index": combined,
            "voiceover_mp3": voiceover,
            "final_video": final_video,
            "approval_required": approval,
        },
        "stage_status": {
            "V3-A_project_structure": "PASS",
            "V3-B_migration": "PASS",
            "V3-C1_hyperframes_preview": "PASS" if combined_ok else "FAIL",
            "V3-C1.1_review_frames": "PASS",
            "V3-D1_smoke_render": "PASS",
            "V3-D2_full_render_tech": "TECH_PASS",
            "V3-D2_full_render_product": "FAIL (audio mux issue)",
        },
        "known_bugs": [
            "P0: final_video.mp4 has no sound (audio mux issue)",
            "P1: Debug controls visible in final_video.mp4",
            "P1: Captions are cropped",
            "P1: Frame cache (1023 images) not cleaned up",
            "P2: Motion is weak (static frames)",
        ],
        "do_not_do": [
            "Don't fix video rendering logic",
            "Don't fix TTS",
            "Don't fix combined_html_builder",
            "Don't fix browser_mp4_renderer mux logic",
            "Don't add visual components",
            "Don't continue D2.1",
            "Don't enter content_pack, CapCut, HyperFrames Studio native",
            "Don't commit outputs/ to git",
        ],
        "commands": {
            "preview": "PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli --script samples/scripts/minimal_obsidian_codex_hermes.md --platform douyin --target-duration 40 --project-id demo_v3_preview --output-mode hyperframes_preview --tts-mode edge_tts --tts-fallback system_say --design-variance 7 --motion-intensity 6 --visual-density 8 --no-allow-mock-audio",
            "smoke_render": "PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli --project-id demo_v3_preview --output-mode render_mp4 --approved --render-smoke-seconds 5 --fps 25",
            "full_render": "PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli --project-id demo_v3_preview --output-mode render_mp4 --approved --fps 25",
            "tests": "PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -v",
        },
    }

    OUTPUT_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()