# NEXT TASK

## 当前任务

**P4.1B-R4.1 Visual Scene Aggregation** — 当前只围绕一条 smoke preview 做视觉章节聚合与布局密度门验证，不进入 P4.2，不做三脚本文案验证。

当前重点：

- `outputs/p4_1b_r4_1_visual_scene_aggregation_preview/`
- `docs/status/P4_1B_R4_1_VISUAL_SCENE_AGGREGATION.md`
- `docs/status/P4_1B_R4_1_CONTACT_SHEET_REVIEW.md`

## 本轮改动

### P4.1B-R4.1

- 24 个源 scene 已聚合为 8 个 visual chapters，平均视觉章节时长约 14.15s
- caption beats 保持 39 条，未被压缩掉
- `scene_pack -> director_timeline -> index.html` 改为以 visual chapters 作为实际预览单元
- 新增 `layout_density` gate，防止 chapter 继续堆成同一种重叠骨架
- contact sheet 已生成，仍需人工复核是否还要 follow-up fix

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `hyperframes_preview` on `p4_1b_r4_1_visual_scene_aggregation_preview`

## 交付物

- `docs/status/P4_1B_R4_1_VISUAL_SCENE_AGGREGATION.md`
- `docs/status/P4_1B_R4_1_CONTACT_SHEET_REVIEW.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不提交 contact-sheet.jpg
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-04
