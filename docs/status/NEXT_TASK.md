# NEXT TASK

## 当前任务

**P4.1B-R2 Debug Cleanup + Mature Visual Component Reuse Smoke** — 已完成 smoke 预览验证，当前进入结果收口与是否扩展到更多脚本的决策准备。

当前重点：

- `outputs/p4_1b_r1_knowledge_render_strategy_preview/`
- `outputs/p4_1b_r1_ai_toolflow_render_strategy_preview/`
- `outputs/p4_1b_r1_sales_render_strategy_preview/`
- `docs/status/P4_1B_R1_RENDER_EFFECTIVE_VISUAL_STRATEGY.md`

## 本轮改动

### P4.1B-R2

- 默认预览不再显示 `LAYOUT FAMILY / CAPTION` 这类调试 meta
- 取消 scan beam / sweep 视觉干扰
- `caption_mode` 通过 CSS 变量和模式类表现出更清楚的差异
- 复用成熟 HUD 组件（`hf-status-stamp` / `hf-glass-panel` / `hf-metric-card`）进入真实 smoke 预览
- `outputs/p4_1b_r2_debug_smoke_preview/` 已完成 preview，`contact-sheet.jpg` 可读，`approval_required.json` 仍为 `READY`

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_preview_pipeline.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `hyperframes_preview` on `p4_1b_r2_debug_smoke_preview`

## 交付物

- `docs/status/P4_1B_R2_VISUAL_COMPONENT_REUSE_AUDIT.md`
- `docs/status/P4_1B_R2_DEBUG_CLEANUP_AND_COMPONENT_REUSE_SMOKE.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-04
