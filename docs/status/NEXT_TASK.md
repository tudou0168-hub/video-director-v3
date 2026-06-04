# NEXT TASK

## 当前任务

**P4.1B-R3 Follow-up Fix** — 当前已把 `layout_family` 从 `scene_pack` 透传到 `director_timeline/index.html`，现在要重新看 contact sheet 与 HTML 是否一致，确认这次不是旧模板缓存。

当前重点：

- `outputs/p4_1b_r3_layout_skeleton_smoke_preview/`
- `docs/status/P4_1B_R3_LAYOUT_SKELETON_DEEPENING.md`
- `docs/status/P4_1B_R3_STRATEGY_TO_SKELETON_AUDIT.md`

## 本轮改动

### P4.1B-R3

- `scene_pack` 的 `layout_family` 已经进入 `director_timeline.json`
- `publish_templates.py` 已对非 contract scene 与 contract scene 统一套 skeleton
- 重新生成的 `contact-sheet.jpg` 需要用人工眼睛确认是否已经摆脱旧模板骨架
- 先留在 R3 范围内，不进入 P4.2

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `hyperframes_preview` on `p4_1b_r3_layout_skeleton_smoke_preview`（已重新生成）

## 交付物

- `docs/status/P4_1B_R3_LAYOUT_SKELETON_DEEPENING.md`
- `docs/status/P4_1B_R3_STRATEGY_TO_SKELETON_AUDIT.md`
- `docs/status/P4_1B_R3_FOLLOWUP_FIX.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-04
