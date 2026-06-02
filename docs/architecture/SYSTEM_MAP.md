# System Map

This is a compact map for agents and maintainers. It complements the existing `docs/architecture.md` file.

## Product goal

Turn Chinese short-video scripts into HyperFrames Studio Native Preview projects, then render final MP4 only after review approval.

## High-level modules

| Area | Path | Role |
|---|---|---|
| CLI | `src/video_director_v3/cli.py` | User-facing command entrypoint |
| Pipeline | `src/video_director_v3/pipeline/` | Orchestrates preview and render modes |
| Director | `src/video_director_v3/director/` | Script extraction, narration planning, storyboard building |
| Design | `src/video_director_v3/design/` | Design profile, dials, brand kit, visual style inputs |
| TTS | `src/video_director_v3/tts/` | Male TTS and fallback behavior |
| Motion | `src/video_director_v3/motion/` | Captions, visual beats, motion bindings, semantic transitions |
| Renderers | `src/video_director_v3/renderers/` | HyperFrames preview capture and approved MP4 rendering |
| Quality | `src/video_director_v3/quality/` | Reports, frame inspection, quality gates |
| Exporters | `src/video_director_v3/exporters/` | Approval gate and output contracts |
| Samples | `samples/scripts/` | Example input scripts |
| Tests | `tests/` | Regression tests and contract checks |

## Data flow

```text
script.md
  -> semantic extraction / narration planning
  -> storyboard and scene protocol
  -> TTS audio and real duration
  -> caption beats
  -> visual beats
  -> semantic transitions
  -> HyperFrames Studio native project
  -> review frames / quality reports / approval gate
  -> approved render_mp4
```

## Output conventions

- Production outputs: `outputs/<project_id>/`
- Test outputs: `test_outputs/<project_id>/`
- Do not write final artifacts under `src/`.

## Review artifacts

The review stage should produce or reference:

- `hyperframes_timeline/`
- `review_frames/`
- `approval_required.json`
- `quality_report.json`

## Final render artifacts

Only after approval:

- `rendered/final_video.mp4`
- `rendered/render_report.json`
- `rendered/sync_report.json`

## Stability principle

Do not replace the native HyperFrames review path with a parallel custom preview path. Improve the existing pipeline and templates in place.
