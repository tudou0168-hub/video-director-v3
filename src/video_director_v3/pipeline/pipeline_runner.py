"""Pipeline runner for video-director-v3."""
import argparse
import json
import traceback
from pathlib import Path

from video_director_v3.config import (
    DEFAULT_DESIGN_VARIANCE,
    DEFAULT_MOTION_INTENSITY,
    DEFAULT_VISUAL_DENSITY,
    INPUT_RELEVANCE_THRESHOLD,
)
from video_director_v3.pipeline.project_paths import (
    ensure_dirs,
    get_project_dir,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Video Director V3")
    parser.add_argument("--script", type=str, help="Input script path")
    parser.add_argument("--platform", type=str, default="douyin")
    parser.add_argument("--target-duration", type=int, default=40, help="Legacy storyboard hint; narration audio is authoritative")
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

    audio_duration = float(tts_result.get("real_duration", args.target_duration)) if tts_result else float(args.target_duration)

    audio_timeline = {"sentence_timings": []}
    audio_tl_path = project_dir / "audio_timeline.json"
    if audio_tl_path.exists():
        try:
            audio_timeline = json.loads(audio_tl_path.read_text(encoding="utf-8"))
        except Exception as e:
            _record_error(errors, "audio_timeline", e)

    # ── 4. Motion storyboard ─────────────────────────────────────────────────
    storyboard = None
    try:
        from video_director_v3.director.storyboard_builder import build_motion_storyboard, write_outputs
        storyboard = build_motion_storyboard(
            narration_plan.get("director_output", {}),
            aspect_ratio="9:16",
            platform_profile=args.platform,
            target_duration=audio_duration,
            narration_plan=narration_plan,
            audio_timeline=audio_timeline,
        )
        from video_director_v3.renderers.hyperframes.studio_native_project_builder import scale_storyboard_to_audio
        storyboard = scale_storyboard_to_audio(storyboard, audio_duration)
        write_outputs(storyboard, project_dir)
        _record_stage(stages, "motion_storyboard", "PASS", f"{len(storyboard.get('scenes', []))} scenes")
    except Exception as e:
        _record_error(errors, "motion_storyboard", e)
        _record_stage(stages, "motion_storyboard", "FAIL", str(e))
        storyboard = _fallback_storyboard(args.project_id, audio_duration)
        (project_dir / "motion_storyboard.json").write_text(
            json.dumps(storyboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    # ── 5. Design dials & profile ───────────────────────────────────────────
    st_data = {}
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
            audio_duration,
        )
        (project_dir / "semantic_transitions.json").write_text(
            json.dumps(st_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _record_stage(stages, "semantic_transitions", "PASS", f"{st_data.get('transition_count', 0)} transitions")
    except Exception as e:
        _record_error(errors, "semantic_transitions", e)
        _record_stage(stages, "semantic_transitions", "FAIL", str(e))

    # ── 7. Visual beats ─────────────────────────────────────────────────────
    visual_beats = {}
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

    # ── 9. Studio Native preview ────────────────────────────────────────────
    try:
        from video_director_v3.renderers.hyperframes.studio_native_project_builder import build_studio_native_project

        manifest = build_studio_native_project(
            project_dir=project_dir,
            storyboard=storyboard or {},
            narration_plan=narration_plan,
            tts_result=tts_result,
            caption_beats=caption_beats_data,
            visual_beats=visual_beats,
            transitions=st_data,
        )
        timeline_dir = project_dir / "hyperframes_timeline"
        _record_stage(stages, "studio_native_preview", "PASS", "hyperframes_timeline/index.html generated", timeline_dir)
    except Exception as e:
        _record_error(errors, "studio_native_preview", e)
        _record_stage(stages, "studio_native_preview", "FAIL", str(e))

    # ── 10. Review frames capture ─────────────────────────────────────────
    review_frames_data = None
    try:
        from video_director_v3.renderers.hyperframes.studio_native_project_builder import capture_native_review_frames
        timeline_dir = project_dir / "hyperframes_timeline"
        if (timeline_dir / "index.html").exists():
            review_frames_dir = project_dir / "review_frames"
            capture_result = capture_native_review_frames(timeline_dir, frames=7)
            review_frames_data = capture_result

            ok_count = capture_result.get("ok_count", 0)
            status = "PASS" if ok_count >= 7 else "FAIL"
            _record_stage(
                stages, "review_frames", status,
                f"{ok_count}/7 frames captured",
                review_frames_dir,
            )
        else:
            _record_stage(stages, "review_frames", "FAIL", "hyperframes_timeline/index.html not found")
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

    # ── 12. Error report ──────────────────────────────────────────────────
    _write_error_report(project_dir, stages, errors)

    # ── 13. Preview report ────────────────────────────────────────────────
    try:
        preview_md = _build_preview_report(project_dir, stages, args)
        (project_dir / "preview_report.md").write_text(preview_md, encoding="utf-8")
        _record_stage(stages, "preview_report", "PASS", "preview_report.md generated")
    except Exception as e:
        _record_error(errors, "preview_report", e)
        _record_stage(stages, "preview_report", "FAIL", str(e))

    # ── 13.5. Viral QA report (P3.6) ─────────────────────────────────────
    try:
        from video_director_v3.qa.viral_qa_evaluator import build_viral_quality_report
        vq_report = build_viral_quality_report(
            project_id=args.project_id,
            project_dir=project_dir,
            narration_plan=narration_plan,
            storyboard=storyboard or {},
            sync_report_path=project_dir / "rendered_smoke" / "sync_report.json",
        )
        (project_dir / "viral_quality_report.json").write_text(
            json.dumps(vq_report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        _record_stage(
            stages, "viral_qa", "PASS" if vq_report["status"] == "PASS" else "WARN",
            f"score={vq_report['total_score']}/{vq_report['max_score']} status={vq_report['status']}",
        )
    except Exception as e:
        _record_error(errors, "viral_qa", e)
        _record_stage(stages, "viral_qa", "FAIL", str(e))

    # ── 14. Approval required ─────────────────────────────────────────────
    try:
        approval = _build_approval_payload(
            project_id=args.project_id,
            project_dir=project_dir,
            stages=stages,
            tts_result=tts_result,
            caption_beats_data=caption_beats_data,
            review_frames_data=review_frames_data,
        )
        (project_dir / "approval_required.json").write_text(
            json.dumps(approval, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _record_stage(stages, "approval_required", "PASS" if approval["can_approve_preview"] else "FAIL", "approval_required.json generated")
    except Exception as e:
        _record_error(errors, "approval_required", e)
        _record_stage(stages, "approval_required", "FAIL", str(e))

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n[V3] Preview complete for {args.project_id}")
    print(f"  project_dir: {project_dir}")
    print(f"  studio_native_timeline: {project_dir / 'hyperframes_timeline'}")
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

    # ── Check Studio Native timeline ─────────────────────────────────────────
    timeline_dir = project_dir / "hyperframes_timeline"
    native_index = timeline_dir / "index.html"
    if not native_index.exists():
        print(f"ERROR: hyperframes_timeline/index.html not found: {native_index}")
        print("Please run hyperframes_preview first")
        return 1

    # ── Check audio exists ───────────────────────────────────────────────────
    audio_path = timeline_dir / "assets" / "voiceover.mp3"
    if not audio_path.exists():
        print(f"ERROR: voiceover.mp3 not found: {audio_path}")
        return 1

    # ── Render ───────────────────────────────────────────────────────────────
    smoke_seconds = args.render_smoke_seconds
    is_smoke = smoke_seconds is not None

    print(f"[V3] Rendering {'smoke' if is_smoke else 'full'} video")
    print(f"  fps: {args.fps}")
    print(f"  hyperframes_timeline: {timeline_dir}")
    print(f"  audio: {audio_path}")

    if is_smoke:
        print(f"  smoke_seconds: {smoke_seconds}")

    try:
        from video_director_v3.renderers.hyperframes.native_mp4_renderer import render_native_mp4

        report = render_native_mp4(
            project_dir=project_dir,
            fps=args.fps,
            smoke_seconds=smoke_seconds,
        )

        print(f"\n[V3] Render {'smoke' if is_smoke else 'full'} complete")
        print(f"  render_status: {report.get('render_status')}")
        print(f"  final_video: {report.get('final_video')}")
        print(f"  duration: {report.get('final_video_duration', 0):.2f}s")
        print(f"  video_stream: {report.get('final_video_has_video_stream')}")
        print(f"  audio_stream: {report.get('final_video_has_audio_stream')}")
        print(f"  sync_status: {report.get('sync_status')}")

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


def _stage_status_map(stages: list[dict]) -> dict[str, str]:
    return {stage["name"]: stage["status"] for stage in stages}


def _build_approval_payload(
    *,
    project_id: str,
    project_dir: Path,
    stages: list[dict],
    tts_result: dict | None,
    caption_beats_data: dict | None,
    review_frames_data: dict | None,
) -> dict:
    native_index_path = project_dir / "hyperframes_timeline" / "index.html"
    native_exists = native_index_path.exists()
    native_size = native_index_path.stat().st_size if native_exists else 0
    preview_report_exists = (project_dir / "preview_report.md").exists()

    stage_status = _stage_status_map(stages)
    required_stage_names = [
        "narration_plan",
        "tts",
        "motion_storyboard",
        "semantic_transitions",
        "caption_beats",
        "studio_native_preview",
        "review_frames",
        "input_relevance",
        "preview_report",
    ]
    failed_required_stages = [
        name for name in required_stage_names
        if stage_status.get(name) != "PASS"
    ]

    review_frames_ok = (
        review_frames_data is not None
        and review_frames_data.get("status") == "PASS"
        and review_frames_data.get("ok_count", 0) >= 7
    )
    input_relevance_ok = stage_status.get("input_relevance") == "PASS"
    tts_ok = (tts_result or {}).get("status") == "ok"
    caption_count = (caption_beats_data or {}).get("caption_count", 0)
    transitions_count = _read_transition_count(project_dir)
    audio_exists = (project_dir / "audio" / "voiceover.mp3").exists()

    can_approve = (
        not failed_required_stages
        and native_exists
        and preview_report_exists
        and audio_exists
        and tts_ok
        and input_relevance_ok
        and review_frames_ok
        and caption_count > 0
        and transitions_count > 0
    )

    return {
        "status": "pending_human_review",
        "approval_required": True,
        "approved": False,
        "preview_status": "READY" if can_approve else "FAILED",
        "review_frames_count": review_frames_data.get("ok_count", 0) if review_frames_data else 0,
        "review_frames_status": review_frames_data.get("status", "unknown") if review_frames_data else "unknown",
        "can_approve_preview": can_approve,
        "next_command": (
            f"python3 -m video_director_v3.cli --project-id {project_id} --output-mode render_mp4 --approved"
            if can_approve else "N/A — preview gate failed"
        ),
        "checks": {
            "required_stage_status": {name: stage_status.get(name, "missing") for name in required_stage_names},
            "failed_required_stages": failed_required_stages,
            "studio_native_index_exists": native_exists,
            "studio_native_index_size": native_size,
            "preview_report_exists": preview_report_exists,
            "audio_exists": audio_exists,
            "tts_status": (tts_result or {}).get("status", "none"),
            "input_relevance_passed": input_relevance_ok,
            "caption_beats_count": caption_count,
            "semantic_transition_count": transitions_count,
            "review_frames_ok": review_frames_ok,
            "review_frames_count": review_frames_data.get("ok_count", 0) if review_frames_data else 0,
        },
    }


def _read_transition_count(project_dir: Path) -> int:
    transition_path = project_dir / "semantic_transitions.json"
    if not transition_path.exists():
        return 0
    try:
        data = json.loads(transition_path.read_text(encoding="utf-8"))
    except Exception:
        return 0
    return int(data.get("transition_count", 0))


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
    native_index = project_dir / "hyperframes_timeline" / "index.html"
    native_exists = native_index.exists()
    native_size = native_index.stat().st_size if native_exists else 0

    audio_ok = False
    audio_duration = 0.0
    if tts_result and tts_result.get("audio_path"):
        audio_path = Path(tts_result["audio_path"])
        if audio_path.exists():
            audio_ok = True
            audio_duration = tts_result.get("real_duration", 0.0)

    score = 60
    if native_exists and native_size > 2000:
        score += 20
    if audio_ok and audio_duration > 0:
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
            "studio_native_preview": {"score": 40 if (native_exists and native_size > 2000) else 0, "details": f"size={native_size}"},
            "audio": {"score": 20 if audio_ok else 0, "details": f"duration={audio_duration:.2f}s"},
            "review_frames": {
                "score": 20 if review_frames_ok else 0,
                "details": f"ok={review_frames_data.get('ok_count', 0) if review_frames_data else 0}/7",
            },
            "preview": {"score": 40 if native_exists else 0},
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
    lines = [f"# Preview Report: {args.project_id}", "", f"- Platform: `{args.platform}`", "- Duration authority: `voiceover audio`", ""]
    lines.append("## Stages")
    for s in stages:
        lines.append(f"- {s['status']}: {s['name']} — {s['detail']}")
    return "\n".join(lines)
