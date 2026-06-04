# NEXT TASK

## 当前任务

**P4.1B-R3 Layout Skeleton Deepening / Strategy-to-Skeleton Binding** — 当前已完成 smoke 预览跑通，接下来要看 contact sheet 里 `hero_metric / tool_pipeline / framework_map / action_close` 是否真的形成不同骨架，再决定是否继续扩展。

当前重点：

- `outputs/p4_1b_r3_layout_skeleton_smoke_preview/`
- `docs/status/P4_1B_R3_LAYOUT_SKELETON_DEEPENING.md`
- `docs/status/P4_1B_R3_STRATEGY_TO_SKELETON_AUDIT.md`

## 本轮改动

### P4.1B-R3

- 让 `layout_family` 真正决定画面骨架，而不是只挂类名
- 关注 `hero_metric / tool_pipeline / framework_map / action_close` 的结构差异是否足够明显
- smoke 只跑 `p4_batch_ai_toolflow.md`，输出到 `outputs/p4_1b_r3_layout_skeleton_smoke_preview/`
- 不要把这轮当成发布候选选择；先看 contact sheet 再决定后续是否扩展

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `hyperframes_preview` on `p4_1b_r3_layout_skeleton_smoke_preview`

## 交付物

- `docs/status/P4_1B_R3_LAYOUT_SKELETON_DEEPENING.md`
- `docs/status/P4_1B_R3_STRATEGY_TO_SKELETON_AUDIT.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-04
