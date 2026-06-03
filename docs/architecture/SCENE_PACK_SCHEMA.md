# Scene Pack Schema

## Purpose

`scene_pack.json` is the core contract between V3 semantic director and HyperFrames native preview. It turns script understanding into stable scene data that templates can consume without reading the raw script or guessing content from keywords.

The current implementation is dry-run. It is generated during preview, linted, and written to:

- `outputs/<project_id>/scene_pack.json`
- `outputs/<project_id>/hyperframes_timeline/data/scene_pack.json`

## Required Scene Fields

Every scene must contain:

- `id`
- `role`
- `intent`
- `duration`
- `voiceover`
- `display_headline`
- `display_subtitle`
- `template_type`
- `slots`
- `qa_rules`

## Supported Roles

- `hook`
- `problem`
- `conflict`
- `method`
- `proof`
- `offer`
- `cta`
- `verdict`

Legacy roles are normalized in the dry-run planner:

- `pain -> problem`
- `explain -> method`
- `evidence -> proof`
- `summary -> verdict`
- `ready -> offer`

## Example

```json
{
  "id": "S01",
  "role": "hook",
  "intent": "capture_attention",
  "duration": 4.0,
  "voiceover": "你有没有发现，工具越多，执行越慢？",
  "display_headline": "你有没有发现，工具越多，执行越慢？",
  "display_subtitle": "工具越多，执行越慢",
  "template_type": "hook",
  "slots": {
    "headline": "你有没有发现，工具越多，执行越慢？",
    "hook_line": "你有没有发现，工具越多，执行越慢？",
    "subtitle": "工具越多，执行越慢",
    "keyword": "执行力"
  },
  "qa_rules": {
    "headline_max_chars": 32,
    "requires_voiceover": true,
    "requires_slots": true,
    "no_placeholder_slots": true
  }
}
```

## Validation

Schema validation lives in `src/video_director_v3/director/scene_pack_schema.py`.

Template contract lint lives in `src/video_director_v3/director/template_contracts.py`.

Both must pass before scene_pack can become a rendering dependency.
