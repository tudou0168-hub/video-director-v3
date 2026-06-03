# NEXT TASK

## 当前任务

**P4.1B Visual Differentiation + Readability Director** — 已完成三条真实脚本的视觉骨架分化验证，当前进入结果收口与人工视觉审查阶段。

当前重点：

- `outputs/p4_1b_knowledge_visual_strategy_preview/`
- `outputs/p4_1b_ai_toolflow_visual_strategy_preview/`
- `outputs/p4_1b_sales_visual_strategy_preview/`
- `docs/status/P4_1B_VISUAL_DIFFERENTIATION_AND_READABILITY.md`

## 本轮改动

### P4.1B

- 用 `visual_strategy` pack 将 knowledge / toolflow / sales 三类内容的骨架分开
- 三条 preview 全部 `gate_status=PASS`、`approval READY`
- knowledge / toolflow / sales 的 `video_type` 与 `template_sequence_signature` 已显式写入 `scene_pack`
- `semantic_quality_report` 新增视觉差异化与可读性指标，且未破坏现有 contract / QA 主线

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `hyperframes_preview` on `p4_1b_knowledge_visual_strategy_preview`
- `hyperframes_preview` on `p4_1b_ai_toolflow_visual_strategy_preview`
- `hyperframes_preview` on `p4_1b_sales_visual_strategy_preview`

## 交付物

- `docs/status/P4_1B_VISUAL_DIFFERENTIATION_AND_READABILITY.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-04
