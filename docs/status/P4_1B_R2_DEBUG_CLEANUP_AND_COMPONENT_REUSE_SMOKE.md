# P4.1B-R2 Debug Cleanup + Mature Visual Component Reuse Smoke

## Input

- Script: `samples/scripts/p4_batch_ai_toolflow.md`
- Output directory: `outputs/p4_1b_r2_debug_smoke_preview/`

## What We Ran

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --script samples/scripts/p4_batch_ai_toolflow.md \
  --platform douyin \
  --target-duration 40 \
  --project-id p4_1b_r2_debug_smoke_preview \
  --output-mode hyperframes_preview \
  --tts-mode edge_tts \
  --tts-fallback system_say \
  --design-variance 7 \
  --motion-intensity 6 \
  --visual-density 8 \
  --no-allow-mock-audio
```

## Result Summary

- `preview_status = READY`
- `can_approve_preview = true`
- `approval_required.status = pending_human_review`
- `review_frames_status = PASS`
- `contact_sheet_exists = true`
- `semantic_quality_score = 55.26`
- `gate_status = PASS`
- `publish_candidate_readiness = NO_GO`

## Contract / QA Summary

### Scene pack

- `video_type = ai_toolflow`
- `visual_strategy_id = vs_ai_toolflow_v1`
- `scene_count = 24`

### Semantic quality

- `fallback_count = 0`
- `slot_missing_count = 0`
- `placeholder_count = 0`
- `raw_text_dependency_count = 0`
- `role_template_mismatch_count = 0`

### Offer / proof / CTA checks

- `offer_profile_risk = low`
- `proof_asset_risk = low`
- `cta_policy_risk = low`
- `fake_metric_count = 0`
- `forbidden_cta_count = 0`
- `early_cta_count = 0`
- `repeated_cta_count = 0`

### QA notes

The preview is clean enough for human review, but not a publish candidate:

- `publish_candidate_readiness = NO_GO`
- the worst-scene set is still dominated by repeated method / template patterns

That is fine for this smoke because the goal was debug cleanup and component reuse, not a publishable candidate.

## Human Review Notes

The contact sheet shows:

- no visible `LAYOUT FAMILY` or `CAPTION / ...` debug meta
- no scan beam / sweep line
- clearer caption differentiation
- visible reuse of mature HUD components such as status stamps, glass panels, and metric cards

## MP4

- `final_video.mp4` was **not** generated
- no `render_mp4` step was run

## Conclusion

This smoke pass confirms that the debug cleanup and mature HUD component reuse are live in the normal preview path.
It is safe to keep this as the current preview baseline.
