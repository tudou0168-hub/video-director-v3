# NEXT TASK

## 当前任务

**P4.1B-R4 Visual Composition Polish + Collision Cleanup** — 当前只围绕一条 smoke preview 收紧通用构图规则，不进入 P4.2，不做三脚本文案验证。

当前重点：

- `outputs/p4_1b_r3_layout_skeleton_smoke_preview/`
- `docs/status/P4_1B_R3_LAYOUT_SKELETON_DEEPENING.md`
- `docs/status/P4_1B_R3_STRATEGY_TO_SKELETON_AUDIT.md`

## 本轮改动

### P4.1B-R4

- `close` 页已禁用旧 `FINAL SCORE / COMPLETE / CHAPTER CLOSE`
- `caption` 已整体降权到底部辅助层
- `tool_pipeline` 已做通用防碰撞
- `framework_map / proof_matrix` 已做中心结构图可读化
- `hero_metric` 已升级为数字 + 单位 + 标题 + 指标卡层级
- `scene_pack -> director_timeline -> index.html` 已透传 `display_headline / visual_headline / memory_anchor / save_reason`
- `contact-sheet.jpg` 需要继续按 panel 逐张人工复核，不要直接宣布收口

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `hyperframes_preview` on `p4_1b_r4_followup_visual_rules_preview`（已重新生成）

## 交付物

- `docs/status/P4_1B_R4_FOLLOWUP_VISUAL_RULES.md`
- `docs/status/P4_1B_R4_FOLLOWUP_CONTACT_SHEET_REVIEW.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不提交 contact-sheet.jpg
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-04
