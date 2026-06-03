# Template Contracts

## Purpose

Template contracts make templates stable. A template should not inspect raw script text or guess body content from keywords. It should consume the `scene_pack.slots` it declares.

This phase adds a static contract registry and lint. Rendering is not migrated yet.

## First Five Contracts

The first contract set covers:

- `hook`
- `problem_conflict`
- `before_after`
- `proof`
- `final_cta`

Each contract defines:

- `required_slots`
- `optional_slots`
- `max_chars`
- `role_compatibility`
- `fallback_template`

## Lint Rules

The lint fails on:

- missing required slots
- placeholder values such as `TODO`, `TBD`, `placeholder`, `占位`, `待补充`
- empty arrays
- empty objects
- overlong slot text
- incompatible role/template pairing

## Migration Rule

Next-stage template migration should be contract-driven:

```text
scene_pack scene
-> template_type
-> contract lint
-> template consumes slots
-> HyperFrames native HTML
```

Templates may keep visual variety, motion presets, and styling variants, but the content they display must come from slots.

## Current Registry

The current registry lives in:

- `src/video_director_v3/director/template_contracts.py`

Tests live in:

- `tests/test_scene_pack_contracts.py`
