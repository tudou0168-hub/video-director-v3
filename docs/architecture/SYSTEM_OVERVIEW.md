# V3 System Overview

## Product Boundary

V3 is a semantic video director. Its job is to understand the script, decide the narrative structure, produce scene intent, fill scene slots, and gate whether a video is ready for human review.

HyperFrames is the deterministic HTML-native preview/render foundation. It should receive structured timeline data and render it consistently. It is not the semantic director brain.

## Only Mainline

```text
script
-> TTS
-> real audio duration
-> captions
-> scene_pack / director timeline
-> HyperFrames native preview
-> review frames / contact sheet
-> human review
-> confirmed MP4 render
```

MP4 render is only allowed after explicit human confirmation. Intermediate phases must stop at HyperFrames native preview and review frames.

## Current Main Pipeline Files

Keep these as the current production path:

- `src/video_director_v3/cli.py`
- `src/video_director_v3/pipeline/pipeline_runner.py`
- `src/video_director_v3/pipeline/project_paths.py`
- `src/video_director_v3/director/narration_planner.py`
- `src/video_director_v3/director/storyboard_builder.py`
- `src/video_director_v3/director/semantic_planner.py`
- `src/video_director_v3/director/scene_pack_schema.py`
- `src/video_director_v3/director/template_contracts.py`
- `src/video_director_v3/tts/tts_adapter.py`
- `src/video_director_v3/motion/caption_beat_generator.py`
- `src/video_director_v3/motion/visual_beat_planner.py`
- `src/video_director_v3/motion/semantic_transition_planner.py`
- `src/video_director_v3/renderers/hyperframes/studio_native_project_builder.py`
- `src/video_director_v3/renderers/hyperframes/publish_templates.py`
- `src/video_director_v3/renderers/hyperframes/native_mp4_renderer.py`

## Legacy / Fallback Inventory

Do not delete these in this phase. Keep them visible as cleanup candidates:

- `src/video_director_v3/renderers/hyperframes/combined_html_builder.py`
- `src/video_director_v3/renderers/hyperframes/html_renderer.py`
- `src/video_director_v3/renderers/browser/browser_mp4_renderer.py`
- `docs/migration-from-v2.md`
- `docs/quickstart-preview-to-mp4.md`
- `docs/archive/tests/manual_archive/`
- `outputs/v3_p3*/`
- `outputs/demo_v3_preview/`
- `outputs/archive/`
- `renders/`
- `scripts/gen_p312d_r2a_frame.py`

These files and directories can be historically useful, but new agents should not treat them as execution entry points.

## First-Stage Convergence

This phase adds a dry-run `scene_pack.json` alongside existing preview outputs. It does not make templates consume scene_pack yet. The next phase should migrate five templates to read slots from scene_pack while keeping HyperFrames native preview unchanged.
