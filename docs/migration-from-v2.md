# Migration from V2

## Scope

This document lists modules migrated from the old project and explains why others were skipped.

**Old project path:** /Users/muzi/video-director_CapCut2.0

## Immediately Migrated

These modules had verified, stable logic in V2:

| Module | Reason |
|--------|--------|
| script_semantic_extractor.py | Stable semantic extraction logic |
| input_relevance_evaluator.py | Verified scoring logic |
| narration_planner.py | Stable narration/compression logic |
| tts_adapter.py | EdgeTTS + system_say fallback + duration contract |
| edge_tts_provider.py | Working TTS provider |
| caption_beat_generator.py | Working caption beat generation |
| visual_beat_planner.py | Stable beat generation |
| scene_layout_director.py | S01 Hook component logic |
| combined_html_builder.py | Verified HTML generation with scene body, audio injection, caption layer, semantic transitions |
| motion_event_bindings.py | Verified binding logic |
| component_registry.py | Working component registry |
| quality_checker.py | V2.0/V2.1 gate classification logic |
| rendered_frame_inspector.py | Working frame inspection |
| capture_review_frames.py | Verified seek method using window.__timelines["combined"].seek(ts) |

## Reference Only (Not Migrated)

These provide context but were not copied:

- Old README and AGENTS documents
- Historical docs and quality report samples
- Old outputs files

## Not Migrated

These were explicitly excluded:

- archive/, FINAL/, work-hermes/
- VIDEO_SYSTEM_V02/V04/V05
- Old outputs, mock placeholders
- legacy merge_scenes.py
- talking-head overlay old mainline
- CapCut Mate old adapter
- Temporary debug scripts