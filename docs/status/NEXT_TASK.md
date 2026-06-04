# NEXT TASK

## 当前任务

**P4.1B-R1 Render-Effective Visual Strategy** — 已完成三条真实脚本的 render-effective 视觉策略验证，当前进入收口与下一阶段多脚本复用准备。

当前重点：

- `outputs/p4_1b_r1_knowledge_render_strategy_preview/`
- `outputs/p4_1b_r1_ai_toolflow_render_strategy_preview/`
- `outputs/p4_1b_r1_sales_render_strategy_preview/`
- `docs/status/P4_1B_R1_RENDER_EFFECTIVE_VISUAL_STRATEGY.md`

## 本轮改动

### P4.1B-R1

- `visual_strategy` 不再只是 scene_pack 的数据字段，而是真正进入 render layer
- `layout_family` 通过 HTML class 和 CSS 真实改变布局轮廓
- `caption_mode` 通过字幕 class 真实改变字幕样式
- `ending_variant` 通过结尾板真实分流
- `memory_anchor` / `visual_object` / `save_reason` 进入 preview 与 QA 报告
- 三条 preview 都已生成，并保留 `gate_status=PASS`、`approval READY`

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `hyperframes_preview` on `p4_1b_r1_knowledge_render_strategy_preview`
- `hyperframes_preview` on `p4_1b_r1_ai_toolflow_render_strategy_preview`
- `hyperframes_preview` on `p4_1b_r1_sales_render_strategy_preview`

## 交付物

- `docs/status/P4_1B_R1_RENDER_EFFECTIVE_VISUAL_STRATEGY.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-04
