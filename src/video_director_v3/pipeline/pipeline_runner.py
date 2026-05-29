"""Pipeline runner for video-director-v3."""
import argparse
import sys
from pathlib import Path

from video_director_v3.config import (
    AUDIO_DURATION_MAX,
    AUDIO_DURATION_MIN,
    DEFAULT_DESIGN_VARIANCE,
    DEFAULT_MOTION_INTENSITY,
    DEFAULT_VISUAL_DENSITY,
    INPUT_RELEVANCE_THRESHOLD,
)
from video_director_v3.pipeline.project_paths import (
    ensure_dirs,
    get_combined_index,
    get_project_dir,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Video Director V3")
    parser.add_argument("--script", type=str, help="Input script path")
    parser.add_argument("--platform", type=str, default="douyin")
    parser.add_argument("--target-duration", type=int, default=40)
    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument(
        "--output-mode",
        type=str,
        choices=["hyperframes_preview", "render_mp4"],
        required=True,
    )
    parser.add_argument("--tts-mode", type=str, default="edge_tts")
    parser.add_argument("--tts-fallback", type=str, default="system_say")
    parser.add_argument("--design-variance", type=int, default=DEFAULT_DESIGN_VARIANCE)
    parser.add_argument("--motion-intensity", type=int, default=DEFAULT_MOTION_INTENSITY)
    parser.add_argument("--visual-density", type=int, default=DEFAULT_VISUAL_DENSITY)
    parser.add_argument("--no-allow-mock-audio", action="store_true")
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--test-mode", action="store_true")

    args = parser.parse_args()

    # Validate render_mp4 requires --approved
    if args.output_mode == "render_mp4" and not args.approved:
        print("ERROR: render_mp4 requires --approved flag")
        print("Please run hyperframes_preview first, then add --approved")
        return 1

    # Ensure output directories exist
    ensure_dirs(args.project_id, test_mode=args.test_mode)

    if args.output_mode == "hyperframes_preview":
        return run_preview(args)
    elif args.output_mode == "render_mp4":
        return run_render(args)
    return 0


def run_preview(args: argparse.Namespace) -> int:
    """Run hyperframes_preview mode."""
    print(f"[V3] Starting hyperframes_preview for {args.project_id}")

    # Load script
    script_path = Path(args.script)
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        return 1

    script_content = script_path.read_text(encoding="utf-8")

    # TODO: Implement full preview pipeline
    # For now, create a minimal stub that demonstrates the structure
    project_dir = get_project_dir(args.project_id, test_mode=args.test_mode)

    # Create input_script.md
    (project_dir / "input_script.md").write_text(script_content, encoding="utf-8")

    # Create stub files
    (project_dir / "DESIGN.md").write_text("# Design Doc\n", encoding="utf-8")
    (project_dir / "brandkit.json").write_text("{}", encoding="utf-8")
    (project_dir / "design_dials.json").write_text(
        '{"design_variance":' + str(args.design_variance) + "}", encoding="utf-8"
    )
    (project_dir / "visual_style_profile.json").write_text("{}", encoding="utf-8")
    (project_dir / "narration_plan.json").write_text("{}", encoding="utf-8")
    (project_dir / "voiceover_script.md").write_text(script_content, encoding="utf-8")
    (project_dir / "audio_timeline.json").write_text("[]", encoding="utf-8")
    (project_dir / "motion_storyboard.json").write_text("[]", encoding="utf-8")
    (project_dir / "visual_beats.json").write_text("[]", encoding="utf-8")
    (project_dir / "caption_beats.json").write_text("[]", encoding="utf-8")
    (project_dir / "motion_events.json").write_text("[]", encoding="utf-8")
    (project_dir / "semantic_transitions.json").write_text("[]", encoding="utf-8")
    (project_dir / "input_relevance_report.json").write_text(
        '{"score": 0.75}', encoding="utf-8"
    )

    # Create approval_required.json
    (project_dir / "approval_required.json").write_text(
        '{"status": "pending", "review_frames": []}', encoding="utf-8"
    )

    # Create combined/index.html stub
    combined_dir = project_dir / "combined"
    combined_dir.mkdir(parents=True, exist_ok=True)
    (combined_dir / "assets").mkdir(parents=True, exist_ok=True)

    print(f"[V3] Preview mode complete - files at {project_dir}")
    print(f"[V3] NOTE: Full pipeline not yet implemented - this is a stub")
    return 0


def run_render(args: argparse.Namespace) -> int:
    """Run render_mp4 mode."""
    print(f"[V3] Starting render_mp4 for {args.project_id}")

    combined_index = get_combined_index(args.project_id, test_mode=args.test_mode)
    if not combined_index.exists():
        print(f"ERROR: combined/index.html not found: {combined_index}")
        print("Please run hyperframes_preview first")
        return 1

    print(f"[V3] Render mode complete - NOTE: Full render not yet implemented")
    return 0


if __name__ == "__main__":
    sys.exit(main())