# P3.11 Visual Semantic Review Plan

## Batch Goal

Based on the 3 real previews produced by P3.10, perform a visual and semantic review only.

This batch does not:
- add features
- expand template count
- change HyperFrames renderer
- render MP4

## Inputs

Review these preview directories:

- `outputs/v3_p310_batch_knowledge_preview/`
- `outputs/v3_p310_batch_sales_preview/`
- `outputs/v3_p310_batch_toolflow_preview/`

## Required Files Per Preview

Each preview review must read:

- `scene_pack.json`
- `semantic_quality_report.json`
- `approval_required.json`
- `review_frames/contact-sheet.jpg`
- `hyperframes_timeline/data/director_timeline.json`

## Review Dimensions

### Semantic Slot Quality

Check whether:
- `scene_pack.slots` reads like human Chinese rather than placeholder structure
- slots are specific enough for deterministic rendering
- slot content is not padded with fake claims or fake metrics

### Role and Template Match

Check whether:
- selected template matches scene role
- proof scenes really behave like proof
- CTA scenes appear only when structurally appropriate
- CTA is not too early, too frequent, or semantically misplaced

### Trustworthiness

Check whether:
- proof is credible
- fake metrics appear
- fake evidence appears
- empty cards appear
- placeholder text appears
- raw text dependency still leaks through

### Language and Layout

Check whether:
- Chinese is dominant
- English is limited to supporting HUD labels
- layout is too dense
- subtitle safe area may collide
- the contact sheet reveals scenes that are visually overloaded or semantically thin

### Gate Quality

Check whether:
- `worst_3_scenes` actually exposes the weakest scenes
- `semantic_quality_score` is meaningful or too formalized
- `approval_required.json` is too permissive relative to visible quality

## Planned Deliverable

This batch should produce:

- `docs/status/P3_11_VISUAL_SEMANTIC_REVIEW.md`

That review document should summarize all 3 previews and provide publish-candidate guidance.

## Review Output Requirements

For each of the 3 preview runs, the review must provide:

- one overall conclusion
- top 3 problems
- whether the preview is publish-candidate ready
- whether issues are mostly semantic-gate calibration or scene-specific repair

## Acceptance Standard

This batch passes only if:

- no template expansion is performed
- no renderer change is performed
- no MP4 is rendered
- no `outputs/` or `renders/` content is committed
- all 3 previews receive written review conclusions
- each preview has at least top 3 issues listed
- one clear recommendation is made for publish-candidate selection, or a clear no-go is recorded
- required follow-up issues are assigned either to `P3.11B` or `P3.11C`

## Post-Review Routing

### Route to P3.11B

Enter `P3.11B Semantic Quality Gate Calibration` if the main problem is:
- `semantic_quality_score` is inflated or too formalized
- gate scoring does not match visible quality
- `worst_3_scenes` ranking is not trustworthy

### Route to P3.11C

Enter `P3.11C Worst 3 Scene Repair` if the main problem is:
- a few concrete scenes are much weaker than the rest
- semantic structure is acceptable but visual execution is uneven

### Block P3.12

Do not enter `P3.12 Publish Candidate Selection` if:
- all 3 previews fail publish-candidate quality
- proof/CTA trustworthiness is still weak
- contact sheet review shows recurring semantic mismatch

### Allow P3.12

Enter `P3.12 Publish Candidate Selection` only if:
- at least 1 preview can plausibly serve as publish candidate
- its remaining issues are known and containable

## Execution Scope Reminder

This is a governance and review-planning batch only.

Do not:
- modify renderer behavior
- add template count
- attach `narrative_compressor.py` to mainline
- commit `outputs/`
- commit `renders/`
- render MP4
