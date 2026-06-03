# HyperFrames Integration

## Responsibility Split

V3 owns semantic planning:

- script interpretation
- narration roles
- scene intent
- scene slots
- caption timing
- transition intent
- QA gates

HyperFrames owns deterministic preview and render:

- native HTML project structure
- timeline playback
- frame capture
- final MP4 render after confirmation
- audio mux and stream verification

## Allowed Integration Path

```text
pipeline_runner.py
-> narration_plan.json
-> audio_timeline.json
-> caption_beats.json
-> motion_storyboard.json
-> scene_pack.json
-> hyperframes_timeline/data/director_timeline.json
-> hyperframes_timeline/index.html
-> review_frames/contact-sheet
```

The `hyperframes_timeline/` directory is the preview authority. `scene_pack.json` is the semantic contract that will feed future contract-driven templates.

## Forbidden Routes

The following routes are historical or prohibited for new work:

- `combined/index.html`
- `file://` ordinary HTML as product acceptance
- Remotion as the mainline
- CapCut as the mainline
- custom playback kernels
- `audio.timeupdate` control loops
- `window.__hf` timeline control
- custom seek mechanisms
- intermediate `render_mp4`

## Render Rule

`render_mp4` is not part of intermediate development. It is allowed only after human review explicitly confirms the native preview.

## Phase-1 Behavior

The current phase preserves `studio_native_project_builder.py` and writes `scene_pack.json` as a dry-run artifact. Templates continue to render from the existing enriched scene dict until the next migration phase.
