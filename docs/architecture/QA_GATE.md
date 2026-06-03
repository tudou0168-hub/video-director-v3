# QA Gate

## Gate Purpose

The QA gate decides whether a native preview is eligible for human review and, after human confirmation, MP4 render. It is not a replacement for human visual review.

## Hard Mainline

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

## Preview Gate Requirements

A preview is not ready unless these artifacts exist and pass their local checks:

- `narration_plan.json`
- `audio_timeline.json`
- `caption_beats.json`
- `motion_storyboard.json`
- `scene_pack.json`
- `semantic_transitions.json`
- `visual_beats.json`
- `hyperframes_timeline/index.html`
- `hyperframes_timeline/data/director_timeline.json`
- `hyperframes_timeline/data/scene_pack.json`
- `review_frames/contact-sheet.jpg`
- `approval_required.json`

## Scene Pack Gate

`scene_pack.json` must pass:

- schema validation
- template contract lint
- non-empty scenes
- supported roles
- non-empty slots
- no placeholders

## Render Gate

MP4 render is blocked until:

- native preview is generated
- review frames/contact sheet are inspected by a human
- the user explicitly confirms render
- `render_mp4` is called with `--approved`

The system must not run intermediate MP4 renders as a shortcut for preview quality.

## Current Phase

The current phase adds dry-run `scene_pack` validation but keeps existing preview rendering intact. Future phases should make five templates consume slots and then add QA checks that compare template output with scene_pack slots.
