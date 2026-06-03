# V3-P3.10C Workspace Cleanup + Artifact Policy

## Goal

Stabilize the workspace boundary after P3.10 without changing the HyperFrames mainline, without rendering MP4, and without mixing local artifacts into source control.

Mainline remains:

`script -> TTS -> real audio duration -> captions -> scene_pack/director_timeline -> HyperFrames native preview -> review frames/contact sheet -> human review -> confirmed MP4 render`

## Current `git status --short`

```text
?? FINAL_PIPELINE_COMPLETION_REPORT.md
?? docs/narrative/
?? docs/status/COMPOSITE_SPEC_12D_R1.md
?? docs/status/P311G_MOTION_SPEC.md
?? docs/status/P3_13A_NARRATIVE_PLAN.md
?? docs/status/STORYBOARD_AUDIT_12C.md
?? outputs/v3_p310_batch_knowledge_preview/
?? outputs/v3_p310_batch_sales_preview/
?? outputs/v3_p310_batch_toolflow_preview/
?? outputs/v3_p311e_reference_matched_visual_correction_preview/hyperframes_timeline/.waveform-cache/
?? outputs/v3_p311f_chinese_hierarchy_bottom5_polish_preview/
?? outputs/v3_p311g_weak_scene_redesign_capability_extraction_preview/
?? outputs/v3_p311h_weak_scene_hard_redesign_preview/
?? outputs/v3_p312a_motion_pass1_boundary_cleanup_preview/
?? outputs/v3_p312b_reference_asset_extraction_expression_upgrade_preview/
?? outputs/v3_p312d_r2a_single_frame_master/
?? outputs/v3_p312d_visual_scene_compression_14_preview/
?? outputs/v3_p313b_narrative_compressor_dryrun/
?? outputs/v3_p313c_narrative_compressed_preview/
?? outputs/v3_p313g_visual_binding_repair_preview/
?? outputs/v3_p313j_headline_binding_fix/
?? outputs/v3_p315_publish_candidate_polish/
?? outputs/v3_p39_contract_templates_preview/
?? outputs/v3_p40_new_script_validation/
?? outputs/v3_p_arch_convergence_preview/
?? renders/
?? scripts/gen_p312d_r2a_frame.py
?? src/video_director_v3/director/narrative_compressor.py
?? tests/test_narrative_compressor.py
```

## Classification

| Path | Classification | Reason |
|---|---|---|
| `FINAL_PIPELINE_COMPLETION_REPORT.md` | `archive_later` | Historical continuous-run summary that includes MP4-era execution notes and sits outside the current status/doc structure. |
| `docs/narrative/COMPRESSION_RULES.md` | `archive_later` | Narrative compression rules for a later experimental line, not part of the current P3.10 mainline contract set. |
| `docs/status/COMPOSITE_SPEC_12D_R1.md` | `archive_later` | Historical visual spec tied to later preview experiments. |
| `docs/status/P311G_MOTION_SPEC.md` | `archive_later` | Later-stage motion experiment spec, not required for P3.10 continuation. |
| `docs/status/P3_13A_NARRATIVE_PLAN.md` | `archive_later` | Future-stage narrative planning document, not a current mainline contract. |
| `docs/status/STORYBOARD_AUDIT_12C.md` | `archive_later` | Historical audit artifact, useful as reference but not a source entrypoint. |
| `scripts/gen_p312d_r2a_frame.py` | `archive_later` | One-off helper for a specific visual review pass; not part of the stable CLI path. |
| `src/video_director_v3/director/narrative_compressor.py` | `archive_later` | Experimental future-stage compressor; not imported by the current preview/render mainline. |
| `tests/test_narrative_compressor.py` | `archive_later` | Test only for the experimental narrative compressor, not a current mainline gate. |
| `outputs/v3_p310_batch_knowledge_preview/` | `ignore_local_artifact` | Generated preview artifact. Keep local for review, do not commit. |
| `outputs/v3_p310_batch_sales_preview/` | `ignore_local_artifact` | Generated preview artifact. Keep local for review, do not commit. |
| `outputs/v3_p310_batch_toolflow_preview/` | `ignore_local_artifact` | Generated preview artifact. Keep local for review, do not commit. |
| `outputs/v3_p311e_reference_matched_visual_correction_preview/hyperframes_timeline/.waveform-cache/` | `ignore_local_artifact` | Tool cache inside generated preview output; never source. |
| `outputs/v3_p311f_chinese_hierarchy_bottom5_polish_preview/` | `ignore_local_artifact` | Generated preview artifact. |
| `outputs/v3_p311g_weak_scene_redesign_capability_extraction_preview/` | `ignore_local_artifact` | Generated preview artifact. |
| `outputs/v3_p311h_weak_scene_hard_redesign_preview/` | `ignore_local_artifact` | Generated preview artifact. |
| `outputs/v3_p312a_motion_pass1_boundary_cleanup_preview/` | `ignore_local_artifact` | Generated preview artifact. |
| `outputs/v3_p312b_reference_asset_extraction_expression_upgrade_preview/` | `ignore_local_artifact` | Generated preview artifact. |
| `outputs/v3_p312d_r2a_single_frame_master/` | `ignore_local_artifact` | Generated review output, not source. |
| `outputs/v3_p312d_visual_scene_compression_14_preview/` | `ignore_local_artifact` | Generated preview artifact. |
| `outputs/v3_p313b_narrative_compressor_dryrun/` | `ignore_local_artifact` | Generated dry-run output for an experimental future-stage line. |
| `outputs/v3_p313c_narrative_compressed_preview/` | `ignore_local_artifact` | Generated preview artifact. |
| `outputs/v3_p313g_visual_binding_repair_preview/` | `ignore_local_artifact` | Generated preview artifact. |
| `outputs/v3_p313j_headline_binding_fix/` | `ignore_local_artifact` | Generated preview/render workspace. Not source-controlled. |
| `outputs/v3_p315_publish_candidate_polish/` | `ignore_local_artifact` | Generated preview/render workspace. Not source-controlled. |
| `outputs/v3_p39_contract_templates_preview/` | `ignore_local_artifact` | Generated preview artifact from an earlier phase. |
| `outputs/v3_p40_new_script_validation/` | `ignore_local_artifact` | Generated validation preview, not source. |
| `outputs/v3_p_arch_convergence_preview/` | `ignore_local_artifact` | Generated preview artifact. |
| `renders/` | `ignore_local_artifact` | Local render/output scratch area; never part of source history. |

## Special Judgments

### `src/video_director_v3/director/narrative_compressor.py`

Classification: `archive_later`

Current dependency chain check:

- Present import hit: `tests/test_narrative_compressor.py`
- No current import from `pipeline_runner.py`, `semantic_planner.py`, `storyboard_builder.py`, `studio_native_project_builder.py`, or CLI mainline
- Mentioned only in future-stage planning docs

Conclusion:
This is **not** a current mainline dependency. Do not submit it as part of P3.10C. Keep it local until we either formalize a P3.13 narrative-compression phase or archive it.

### `tests/test_narrative_compressor.py`

Classification: `archive_later`

It validates the experimental compressor only. It is not part of the current preview approval or contract gate.

### `docs/narrative/`

Classification: `archive_later`

Narrative guidance is useful, but it belongs either in a future P3.13 package or under archived reference docs. It is not a current start-here/mainline doc set.

### `FINAL_PIPELINE_COMPLETION_REPORT.md`

Classification: `archive_later`

This file documents a later continuous execution line and includes MP4 output notes. It should not sit at repo root as if it were a mainline status entry.

### `outputs/`

Classification: `ignore_local_artifact`

Policy:

- `outputs/<project_id>/` is a runtime/output workspace, not source.
- Keep outputs locally for human review and verification.
- Do not commit preview trees, screenshots, contact sheets, or rendered media.
- If a run needs permanent traceability, summarize it in `docs/status/` rather than tracking the output directory.

### `renders/`

Classification: `ignore_local_artifact`

This is local render scratch space and should stay out of Git.

### `.waveform-cache/`

Classification: `ignore_local_artifact`

This is a cache nested inside generated output; it is never source and should be ignored.

## Keep-And-Commit for This Phase

Only two files belong in this phase commit:

- `.gitignore`
- `docs/status/P3_10C_WORKSPACE_CLEANUP_PLAN.md`

No functional source files should be added in P3.10C.

## Delete Candidates

None in this phase.

Reason:
P3.10C is boundary cleanup only. We are not deleting historical or experimental files until they are either archived or explicitly approved for removal.

## Minimal `.gitignore` Policy Added

- Ignore `outputs/*` generated project trees
- Keep `outputs/archive/README.md` visible
- Ignore `renders/`
- Ignore nested `outputs/**/.waveform-cache/`

This keeps GitHub stable while preserving local review workflows.

## Next Step for P3.11

Proceed on a clean boundary:

- Mainline source and docs stay in Git
- Generated previews/renders stay local
- Experimental narrative-compression files remain out of the mainline until explicitly promoted or archived
