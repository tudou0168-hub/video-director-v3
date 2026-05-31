"""Pipeline runner for video-director-v3."""
import argparse
import asyncio
import json
import shutil
import traceback
from datetime import datetime
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
from video_director_v3.pipeline.stages import OutputMode


def main() -> int:
    parser = argparse.ArgumentParser(description="Video Director V3")
    parser.add_argument("--script", type=str, help="Input script path")
    parser.add_argument("--platform", type=str, default="douyin")
    parser.add_argument("--target-duration", type=int, default=40)
    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--output-mode", type=str, choices=["hyperframes_preview", "render_mp4"], required=True)
    parser.add_argument("--tts-mode", type=str, default="edge_tts")
    parser.add_argument("--tts-fallback", type=str, default="system_say")
    parser.add_argument("--design-variance", type=int, default=DEFAULT_DESIGN_VARIANCE)
    parser.add_argument("--motion-intensity", type=int, default=DEFAULT_MOTION_INTENSITY)
    parser.add_argument("--visual-density", type=int, default=DEFAULT_VISUAL_DENSITY)
    parser.add_argument("--no-allow-mock-audio", action="store_true")
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--render-smoke-seconds", type=float, default=None)
    parser.add_argument("--fps", type=int, default=25)
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--keep-frames", action="store_true", help="Keep frames/ directory after render (default: False)")

    args = parser.parse_args()

    # Validate render_mp4 requires --approved
    if args.output_mode == "render_mp4" and not args.approved:
        print("ERROR: render_mp4 requires --approved flag")
        print("Please run hyperframes_preview first, then add --approved")
        return 1

    # Ensure output directories exist
    ensure_dirs(args.project_id, test_mode=args.test_mode)
    project_dir = get_project_dir(args.project_id, test_mode=args.test_mode)

    if args.output_mode == "hyperframes_preview":
        return run_preview(args, project_dir)
    elif args.output_mode == "render_mp4":
        return run_render(args, project_dir)
    return 0


def run_preview(args: argparse.Namespace, project_dir: Path) -> int:
    """Run hyperframes_preview mode with real pipeline stages."""
    print(f"[V3] Starting hyperframes_preview for {args.project_id}")

    stages = []
    errors = []

    # ── 1. Read input script ─────────────────────────────────────────────────
    try:
        script_path = Path(args.script)
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        script_content = script_path.read_text(encoding="utf-8")
        (project_dir / "input_script.md").write_text(script_content, encoding="utf-8")
        _record_stage(stages, "read_input_script", "PASS", "input script loaded")
    except Exception as e:
        _record_error(errors, "read_input_script", e)
        _record_stage(stages, "read_input_script", "FAIL", str(e))

    # ── 2. Narration plan ───────────────────────────────────────────────────
    try:
        from video_director_v3.director.narration_planner import build_narration_plan, write_outputs
        title = next((l.lstrip("# ").strip() for l in script_content.splitlines() if l.strip()), args.project_id)
        narration_plan = build_narration_plan(
            script_content,
            project_id=args.project_id,
            title=title,
            platform=args.platform,
            target_duration=args.target_duration,
        )
        write_outputs(narration_plan, project_dir)
        _record_stage(stages, "narration_plan", "PASS", f"{len(narration_plan.get('sentence_list', []))} sentences")
    except Exception as e:
        _record_error(errors, "narration_plan", e)
        _record_stage(stages, "narration_plan", "FAIL", str(e))
        narration_plan = {"sentence_list": [], "target_duration": args.target_duration}

    # ── 3. TTS ──────────────────────────────────────────────────────────────
    tts_result = None
    try:
        from video_director_v3.tts.tts_adapter import run_tts
        allow_mock = not args.no_allow_mock_audio
        tts_result = run_tts(
            narration_plan,
            project_dir,
            mode=args.tts_mode,
            allow_mock_audio=allow_mock,
        )
        status = tts_result.get("status", "unknown")
        if status == "ok":
            _record_stage(stages, "tts", "PASS", f"TTS {args.tts_mode} ok, duration={tts_result.get('real_duration', 0):.2f}s")
        else:
            _record_stage(stages, "tts", "FAIL" if not allow_mock else "WARN", f"TTS status: {status}")
    except Exception as e:
        _record_error(errors, "tts", e)
        _record_stage(stages, "tts", "FAIL", str(e))

    # ── 4. Motion storyboard ─────────────────────────────────────────────────
    storyboard = None
    try:
        from video_director_v3.director.storyboard_builder import build_motion_storyboard, write_outputs
        storyboard = build_motion_storyboard(
            narration_plan.get("director_output", {}),
            aspect_ratio="9:16",
            platform_profile=args.platform,
            target_duration=args.target_duration,
        )
        write_outputs(storyboard, project_dir)
        _record_stage(stages, "motion_storyboard", "PASS", f"{len(storyboard.get('scenes', []))} scenes")
    except Exception as e:
        _record_error(errors, "motion_storyboard", e)
        _record_stage(stages, "motion_storyboard", "FAIL", str(e))
        storyboard = _fallback_storyboard(args.project_id, args.target_duration)
        (project_dir / "motion_storyboard.json").write_text(
            json.dumps(storyboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    # ── 5. Design dials & profile ───────────────────────────────────────────
    try:
        design_dials = {
            "design_variance": args.design_variance,
            "motion_intensity": args.motion_intensity,
            "visual_density": args.visual_density,
        }
        (project_dir / "design_dials.json").write_text(
            json.dumps(design_dials, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        visual_style_profile = {
            "aspect_ratio": "9:16",
            "design_variance": args.design_variance,
            "motion_intensity": args.motion_intensity,
            "visual_density": args.visual_density,
            "layout_strategy": "centered",
            "hook_strategy": "metrics_focus",
            "caption_style": {},
            "color_tokens": {},
            "component_preferences": [],
            "transition_style": "fade",
            "density_rules": {},
        }
        (project_dir / "visual_style_profile.json").write_text(
            json.dumps(visual_style_profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _record_stage(stages, "design_profile", "PASS", "design dials and profile generated")
    except Exception as e:
        _record_error(errors, "design_profile", e)
        _record_stage(stages, "design_profile", "FAIL", str(e))

    # ── 6. Semantic transitions ───────────────────────────────────────────
    try:
        from video_director_v3.motion.semantic_transition_planner import build_semantic_transitions
        st_data = build_semantic_transitions(
            storyboard.get("scenes", []) if storyboard else [],
            args.target_duration,
        )
        (project_dir / "semantic_transitions.json").write_text(
            json.dumps(st_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _record_stage(stages, "semantic_transitions", "PASS", f"{st_data.get('transition_count', 0)} transitions")
    except Exception as e:
        _record_error(errors, "semantic_transitions", e)
        _record_stage(stages, "semantic_transitions", "FAIL", str(e))

    # ── 7. Visual beats ─────────────────────────────────────────────────────
    try:
        from video_director_v3.motion.visual_beat_planner import plan_visual_beats, write_outputs
        visual_beats = plan_visual_beats(storyboard or {}, {})
        write_outputs(visual_beats, project_dir)
        _record_stage(stages, "visual_beats", "PASS", "visual beats generated")
    except Exception as e:
        _record_error(errors, "visual_beats", e)
        _record_stage(stages, "visual_beats", "FAIL", str(e))

    # ── 8. Caption beats ───────────────────────────────────────────────────
    caption_beats_data = None
    try:
        from video_director_v3.motion.caption_beat_generator import generate_caption_beats
        audio_timeline = {"sentence_timings": []}
        audio_tl_path = project_dir / "audio_timeline.json"
        if audio_tl_path.exists():
            audio_timeline = json.loads(audio_tl_path.read_text(encoding="utf-8"))
        caption_beats_data = generate_caption_beats(
            project_dir=project_dir,
            narration_plan=narration_plan,
            audio_timeline=audio_timeline,
            motion_storyboard=storyboard or {},
        )
        _record_stage(stages, "caption_beats", "PASS", f"{caption_beats_data.get('caption_count', 0)} caption beats")
    except Exception as e:
        _record_error(errors, "caption_beats", e)
        _record_stage(stages, "caption_beats", "FAIL", str(e))

    # ── 9. Combined HTML ───────────────────────────────────────────────────
    try:
        from video_director_v3.renderers.hyperframes.combined_html_builder import build_combined_html

        manifest = build_combined_html(
            project_dir=project_dir,
            storyboard=storyboard or {},
            tts_result=tts_result,
            caption_beats=caption_beats_data,
            semantic_transitions=None,
        )
        combined_html_path = project_dir / "combined" / "index.html"
        _record_stage(stages, "combined_html", "PASS", "combined/index.html generated", combined_html_path)
    except Exception as e:
        _record_error(errors, "combined_html", e)
        _record_stage(stages, "combined_html", "FAIL", str(e))

    # ── 10. Review frames capture ─────────────────────────────────────────
    review_frames_data = None
    try:
        from video_director_v3.renderers.browser.review_frame_capturer import (
            capture_review_frames,
            write_capture_results,
            TIMESTAMPS,
        )
        combined_html_path = project_dir / "combined" / "index.html"
        if combined_html_path.exists():
            review_frames_dir = project_dir / "review_frames"
            capture_result = asyncio.run(
                capture_review_frames(
                    html_path=str(combined_html_path),
                    output_dir=str(review_frames_dir),
                    timestamps=TIMESTAMPS,
                )
            )
            write_capture_results(capture_result, review_frames_dir)
            review_frames_data = capture_result

            ok_count = capture_result.get("ok_count", 0)
            status = "PASS" if ok_count >= 7 else "FAIL"
            _record_stage(
                stages, "review_frames", status,
                f"{ok_count}/7 frames captured",
                review_frames_dir,
            )
        else:
            _record_stage(stages, "review_frames", "FAIL", "combined/index.html not found")
            review_frames_data = {"status": "FAIL", "error": "no HTML"}
    except Exception as e:
        _record_error(errors, "review_frames", e)
        _record_stage(stages, "review_frames", "FAIL", str(e))
        review_frames_data = {"status": "FAIL", "error": str(e)}

    # ── 11. Input relevance ───────────────────────────────────────────────
    try:
        from video_director_v3.director.input_relevance_evaluator import build_input_relevance_report
        input_rel = build_input_relevance_report(project_dir)
        (project_dir / "input_relevance_report.json").write_text(
            json.dumps(input_rel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        score = input_rel.get("input_relevance_score", 0)
        status = "PASS" if score >= INPUT_RELEVANCE_THRESHOLD else "FAIL"
        _record_stage(stages, "input_relevance", status, f"score={score:.3f}")
    except Exception as e:
        _record_error(errors, "input_relevance", e)
        _record_stage(stages, "input_relevance", "FAIL", str(e))

    # ── 11. Quality report ────────────────────────────────────────────────
    try:
        quality = _build_quality_report(project_dir, stages, args.platform, tts_result, review_frames_data)
        (project_dir / "quality_report.json").write_text(
            json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (project_dir / "quality_report.md").write_text(_markdown_quality(quality), encoding="utf-8")
        _record_stage(stages, "quality_report", "PASS", "quality report generated")
    except Exception as e:
        _record_error(errors, "quality_report", e)
        _record_stage(stages, "quality_report", "FAIL", str(e))

    # ── 12. Approval required ─────────────────────────────────────────────
    try:
        combined_html_path = project_dir / "combined" / "index.html"
        html_exists = combined_html_path.exists()
        html_size = combined_html_path.stat().st_size if html_exists else 0

        review_frames_ok = (
            review_frames_data is not None
            and review_frames_data.get("status") == "PASS"
            and review_frames_data.get("ok_count", 0) >= 7
        )
        can_approve = html_exists and (tts_result.get("status") == "ok" if tts_result else False) and review_frames_ok

        approval = {
            "status": "pending",
            "preview_status": "READY" if can_approve else "FAILED",
            "review_frames_count": review_frames_data.get("ok_count", 0) if review_frames_data else 0,
            "review_frames_status": review_frames_data.get("status", "unknown") if review_frames_data else "unknown",
            "can_approve_preview": can_approve,
            "next_command": f"python3 -m video_director_v3.cli --project-id {args.project_id} --output-mode render_mp4 --approved" if can_approve else "N/A — fix review_frames first",
            "checks": {
                "combined_html_exists": html_exists,
                "combined_html_size": html_size,
                "tts_status": tts_result.get("status") if tts_result else "none",
                "caption_beats_count": caption_beats_data.get("caption_count", 0) if caption_beats_data else 0,
                "review_frames_ok": review_frames_ok,
                "review_frames_count": review_frames_data.get("ok_count", 0) if review_frames_data else 0,
            },
        }
        (project_dir / "approval_required.json").write_text(
            json.dumps(approval, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _record_stage(stages, "approval_required", "PASS" if can_approve else "FAIL", "approval_required.json generated")
    except Exception as e:
        _record_error(errors, "approval_required", e)
        _record_stage(stages, "approval_required", "FAIL", str(e))

    # ── 13. Error report ──────────────────────────────────────────────────
    _write_error_report(project_dir, stages, errors)

    # ── 14. Preview report ────────────────────────────────────────────────
    try:
        preview_md = _build_preview_report(project_dir, stages, args)
        (project_dir / "preview_report.md").write_text(preview_md, encoding="utf-8")
        _record_stage(stages, "preview_report", "PASS", "preview_report.md generated")
    except Exception as e:
        _record_error(errors, "preview_report", e)

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n[V3] Preview complete for {args.project_id}")
    print(f"  project_dir: {project_dir}")
    print(f"  combined_html: {project_dir / 'combined' / 'index.html'}")
    print(f"  approval_required: {project_dir / 'approval_required.json'}")
    print(f"  next_step: Add --approved to render MP4 after review")

    failed = [s for s in stages if s["status"] == "FAIL"]
    if failed:
        print(f"\n  WARNING: {len(failed)} stage(s) failed:")
        for s in failed:
            print(f"    - {s['name']}: {s['detail']}")

    return 0


def run_render(args: argparse.Namespace, project_dir: Path) -> int:
    """Run render_mp4 mode with approval gate and smoke render support."""
    print(f"[V3] Starting render_mp4 for {args.project_id}")

    # ── Approval Gate ───────────────────────────────────────────────────────
    approval_path = project_dir / "approval_required.json"
    if not args.approved:
        print("ERROR: render_mp4 requires --approved flag")
        print("Please run hyperframes_preview first, review the frames, then add --approved")
        return 1

    if not approval_path.exists():
        print(f"ERROR: {approval_path} not found")
        print("Please run hyperframes_preview first")
        return 1

    approval_data = {}
    try:
        approval_data = json.loads(approval_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to read approval_required.json: {e}")
        return 1

    can_approve = approval_data.get("can_approve_preview", False)
    if not can_approve:
        print("ERROR: Preview has not passed approval checks.")
        print(f"  preview_status: {approval_data.get('preview_status', 'unknown')}")
        print(f"  review_frames_count: {approval_data.get('review_frames_count', 0)}")
        print(f"  review_frames_status: {approval_data.get('review_frames_status', 'unknown')}")
        print("Please review the preview and ensure all checks pass before rendering.")
        return 1

    # ── Check combined/index.html ────────────────────────────────────────────
    combined_index = project_dir / "combined" / "index.html"
    if not combined_index.exists():
        print(f"ERROR: combined/index.html not found: {combined_index}")
        print("Please run hyperframes_preview first")
        return 1

    # ── Check audio exists ───────────────────────────────────────────────────
    audio_candidates = [
        project_dir / "audio" / "voiceover.mp3",
        project_dir / "combined" / "assets" / "voiceover.mp3",
    ]
    audio_path = next((p for p in audio_candidates if p.exists()), None)
    if not audio_path:
        print(f"ERROR: voiceover.mp3 not found in {[str(p) for p in audio_candidates]}")
        return 1

    # ── Render ───────────────────────────────────────────────────────────────
    smoke_seconds = args.render_smoke_seconds
    is_smoke = smoke_seconds is not None

    print(f"[V3] Rendering {'smoke' if is_smoke else 'full'} video")
    print(f"  fps: {args.fps}")
    print(f"  combined/index.html: {combined_index}")
    print(f"  audio: {audio_path}")

    if is_smoke:
        print(f"  smoke_seconds: {smoke_seconds}")

    try:
        from video_director_v3.renderers.browser.browser_mp4_renderer import (
            render_browser_mp4,
            write_render_report,
        )

        smoke_dur = smoke_seconds

        report = asyncio.run(
            render_browser_mp4(
                project_dir=project_dir,
                fps=args.fps,
                smoke_seconds=smoke_dur,
                clean_mode=True,
                keep_frames=args.keep_frames,
            )
        )

        write_render_report(report, project_dir, is_smoke=is_smoke)

        print(f"\n[V3] Render {'smoke' if is_smoke else 'full'} complete")
        print(f"  render_status: {report.get('render_status')}")
        print(f"  frames_generated: {report.get('frames_generated', 0)}/{report.get('frames_expected', 0)}")
        print(f"  final_video: {report.get('final_video')}")
        print(f"  duration: {report.get('final_video_duration', 0):.2f}s")
        print(f"  video_stream: {report.get('final_video_has_video_stream')}")
        print(f"  audio_stream: {report.get('final_video_has_audio_stream')}")
        print(f"  clean_render_status: {report.get('clean_render_status')}")
        print(f"  frames_cache_cleaned: {report.get('frames_cache_cleaned')}")
        print(f"  final_review_frames_count: {report.get('final_review_frames_count', 0)}")

        if report.get("issues"):
            print(f"  issues: {report['issues']}")

        if report.get("status") == "FAIL":
            print(f"\nERROR: Render failed: {report.get('error', 'unknown')}")
            return 1

        return 0

    except Exception as e:
        import traceback
        print(f"ERROR: Render failed: {e}")
        print(traceback.format_exc())
        return 1


def _fallback_storyboard(project_id: str, target_duration: float) -> dict:
    """Create a minimal storyboard when real one fails."""
    scene_roles = ["hook", "pain", "method", "method", "evidence", "proof", "cta"]
    scene_dur = target_duration / len(scene_roles)
    cursor = 0.0
    scenes = []
    for i, role in enumerate(scene_roles):
        scenes.append({
            "scene_id": f"S{i+1:02d}",
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
            "aspect_ratio": "9:16",
            "duration": target_duration,
        },
        "scenes": scenes,
    }


def _record_stage(stages: list, name: str, status: str, detail: str, artifact: Path | None = None) -> None:
    stages.append({"name": name, "status": status, "detail": detail, "artifact": str(artifact) if artifact else None})


def _record_error(errors: list, stage: str, error: Exception) -> None:
    errors.append({"stage": stage, "type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})


def _write_error_report(project_dir: Path, stages: list, errors: list) -> None:
    (project_dir / "error_report.json").write_text(
        json.dumps({"status": "failed" if errors else "ok", "stages": stages, "errors": errors}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [f"# Error Report: {project_dir.name}", "", f"- Status: `{'failed' if errors else 'ok'}`", ""]
    for s in stages:
        lines.append(f"- {s['status']}: {s['name']} - {s['detail']}")
    if errors:
        lines.extend(["", "## Errors", ""])
        for e in errors:
            lines.append(f"- `{e['stage']}` {e['type']}: {e['message']}")
    else:
        lines.append("- No errors")
    (project_dir / "error_report.md").write_text("\n".join(lines), encoding="utf-8")


def _build_quality_report(project_dir: Path, stages: list, platform: str, tts_result: dict | None, review_frames_data: dict | None = None) -> dict:
    combined_html = project_dir / "combined" / "index.html"
    html_exists = combined_html.exists()
    html_size = combined_html.stat().st_size if html_exists else 0

    audio_ok = False
    audio_duration = 0.0
    if tts_result and tts_result.get("audio_path"):
        audio_path = Path(tts_result["audio_path"])
        if audio_path.exists():
            audio_ok = True
            audio_duration = tts_result.get("real_duration", 0.0)

    score = 60
    if html_exists and html_size > 20000:
        score += 20
    if audio_ok and AUDIO_DURATION_MIN <= audio_duration <= AUDIO_DURATION_MAX:
        score += 20

    # Review frames penalty
    review_frames_ok = False
    if review_frames_data and review_frames_data.get("status") == "PASS":
        score += 20
        review_frames_ok = True
    elif review_frames_data and review_frames_data.get("ok_count", 0) < 7:
        score -= 10
        review_frames_ok = False

    return {
        "project": {"project_id": project_dir.name, "platform": platform},
        "overall": {"overall_score": min(100, score)},
        "sections": {
            "combined_html": {"score": 40 if (html_exists and html_size > 20000) else 0, "details": f"size={html_size}"},
            "audio": {"score": 20 if audio_ok else 0, "details": f"duration={audio_duration:.2f}s"},
            "review_frames": {
                "score": 20 if review_frames_ok else 0,
                "details": f"ok={review_frames_data.get('ok_count', 0) if review_frames_data else 0}/7",
            },
            "preview": {"score": 40 if html_exists else 0},
        },
        "main_issues": [],
        "stages": stages,
    }


def _markdown_quality(quality: dict) -> str:
    score = quality.get("overall", {}).get("overall_score", 0)
    lines = [f"# Quality Report: {quality['project']['project_id']}", "", f"- 总分：`{score}`", f"- 平台：`{quality['project']['platform']}`", ""]
    lines.append("## 主要问题")
    issues = quality.get("main_issues", [])
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- 无")
    return "\n".join(lines)


def _build_preview_report(project_dir: Path, stages: list, args: argparse.Namespace) -> str:
    lines = [f"# Preview Report: {args.project_id}", "", f"- Platform: `{args.platform}`", f"- Target duration: `{args.target_duration}s`", ""]
    lines.append("## Stages")
    for s in stages:
        lines.append(f"- {s['status']}: {s['name']} — {s['detail']}")
    return "\n".join(lines)