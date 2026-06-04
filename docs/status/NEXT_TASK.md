# NEXT TASK

## 当前任务

**P4.1B-R4 Real Follow-up: Preview Load Fix + Unified Visual Layout Rules** — 当前只围绕一条 smoke preview 收紧通用构图规则，不进入 R5，不进入 P4.2，也不做三脚本文案验证。

当前重点：

- `outputs/p4_1b_r4_real_followup_visual_layout_preview/`
- `docs/status/P4_1B_R4_REAL_FOLLOWUP_VISUAL_LAYOUT.md`
- `docs/status/P4_1B_R4_REAL_FOLLOWUP_CONTACT_SHEET_REVIEW.md`

## 本轮改动

### P4.1B-R4

- `close` 页彻底禁用旧 `FINAL SCORE / COMPLETE / CHAPTER CLOSE`
- `caption` 已统一 foundation 并降权到底部辅助层
- `tool_pipeline` 已增加通用视觉 stage / skeleton / support 层，避免节点、flow line、result card 互相重叠
- `framework_map / proof_matrix` 已提升为可读的结构图 / 四象限版式
- `hero_metric` 已提升为数字 + 单位 + 标题 + 指标卡的成熟层级
- `scene_pack -> director_timeline -> index.html` 已透传 `display_headline / visual_headline / memory_anchor / save_reason`
- `preview` 打开时不再是 `0:00 / 0:00` 的空项目状态；正确项目目录已挂到 HyperFrames Studio
- `contact-sheet.jpg` 仍需按 panel 逐张人工复核，不能仅凭分数收口

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `hyperframes_preview` on `p4_1b_r4_real_followup_visual_layout_preview`（已重新生成）

## 交付物

- `docs/status/P4_1B_R4_REAL_FOLLOWUP_VISUAL_LAYOUT.md`
- `docs/status/P4_1B_R4_REAL_FOLLOWUP_CONTACT_SHEET_REVIEW.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不提交 contact-sheet.jpg
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-04
