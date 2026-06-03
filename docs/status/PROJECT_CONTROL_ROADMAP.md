# Project Control Roadmap

## Highest Principle

AI 负责语义导演，契约文件负责约束，模板负责确定性执行，HyperFrames 负责稳定预览/渲染，QA Gate 负责阻止垃圾产出。

This repo advances only through the following control loop:

1. plan
2. execute
3. verify
4. commit to GitHub
5. wait for review
6. only then enter the next batch

## Five Layers

### Layer 1: Semantic Director

Purpose:
- Understand script structure, pain, proof, method, offer, CTA
- Produce stable semantic scene intent before rendering

Representative files:
- `src/video_director_v3/director/semantic_planner.py`
- `src/video_director_v3/director/scene_pack_schema.py`
- future: `offer_planner.py`

### Layer 2: Contract Files

Purpose:
- Lock input/output contracts
- Prevent drift caused by chat memory or temporary prompt heuristics

Representative files:
- `docs/architecture/SCENE_PACK_SCHEMA.md`
- `docs/architecture/TEMPLATE_CONTRACTS.md`
- `docs/architecture/QA_GATE.md`
- `src/video_director_v3/director/template_contracts.py`

### Layer 3: Deterministic Templates

Purpose:
- Consume only `scene_pack.slots`
- Execute stable visual composition deterministically

Rules:
- Templates must not guess body content from raw narration or raw script
- Missing slots must fail lint or fallback explicitly

Representative files:
- `src/video_director_v3/renderers/hyperframes/publish_templates.py`
- `src/video_director_v3/renderers/hyperframes/studio_native_project_builder.py`

### Layer 4: HyperFrames Runtime

Purpose:
- Native preview
- Review frames / contact sheet
- Confirmed render after human approval

Rules:
- Do not rewrite renderer
- Do not return to `combined/index.html`
- Do not reintroduce `audio.timeupdate`, `window.__hf`, or custom seek logic

### Layer 5: QA Gate

Purpose:
- Block empty cards, semantic mismatch, fake metrics, missing proof, missing CTA, unreadable layouts

Representative files:
- `src/video_director_v3/qa/semantic_quality_gate.py`
- `approval_required.json`
- contact sheet
- review report

## Completed Stages

### P3.10 Contract System Expansion + Semantic Quality Gate

Completed outcomes:
- 15 contract-driven templates landed
- `scene_pack`, `template_contracts`, and `semantic_quality` connected into preview approval gate
- 3 real previews completed
- no MP4 generated

### P3.10C Workspace Cleanup + Artifact Policy

Completed outcomes:
- `.gitignore` minimally updated for local artifacts
- `docs/status/P3_10C_WORKSPACE_CLEANUP_PLAN.md` committed
- `outputs/`, `renders/`, and waveform cache treated as local artifacts
- archive-later files explicitly excluded from mainline submission

## Five Rounds, Twelve Batches

### Round 0: Architecture Convergence and Boundary Cleanup

- `P3.10 Contract System Expansion`
- `P3.10C Workspace Cleanup`

Status:
- completed

### Round 1: Visual Semantic Quality Hardening

- `P3.11 Visual + Semantic Review`
- `P3.11B Semantic Quality Gate Calibration`
- `P3.11C Worst 3 Scene Repair`

Goal:
- review current previews without expanding templates or changing renderer behavior

### Round 2: Publish Candidate Validation

- `P3.12 Publish Candidate Selection`
- `P3.12B Confirmed MP4 Trial`

Goal:
- identify one publishable candidate before any confirmed MP4 trial

### Round 3: Semantic Director and Conversion Structure Upgrade

- `P3.13 Offer / Proof / CTA System`
- `P3.13B Narrative Compression Decision`

Goal:
- improve semantic conversion logic only after current contract-driven preview quality is understood

### Round 4: Template Library and Production Capacity Expansion

- `P3.14 Template Library Expansion`
- `P3.14B DESIGN / BRAND Contract`

Goal:
- scale production capability only after semantic and QA control is stable

### Round 5: Productization / Delivery

- `P4.0 Operator Runbook`
- `P4.1 Ten Sample Validation`

Goal:
- turn the stabilized workflow into repeatable operator delivery

## Mandatory Batch Structure

Every batch must include:

- PLAN document
- execution scope
- modified file list
- acceptance artifacts
- test commands
- preview/contact-sheet requirements
- GitHub commit hash
- whether MP4 was generated
- next-batch recommendation

## Advancement Rule

No batch may advance by habit or memory.

Required order:

1. write plan
2. execute within scope
3. verify outputs and tests
4. commit to GitHub
5. wait for acceptance
6. enter next batch only after acceptance

## Current Pointer

Current control document:
- `docs/status/PROJECT_CONTROL_ROADMAP.md`

Current batch plan:
- `docs/status/P3_11_VISUAL_SEMANTIC_REVIEW_PLAN.md`
