# NEXT TASK

## 当前任务

**P4.0 First Real Script Production Trial** — 已完成第一条真实脚本试跑，当前进入结果收口与后续复用阶段。

当前重点：

- `outputs/p4_first_real_script_preview/`
- `docs/status/P4_0_FIRST_REAL_SCRIPT_PRODUCTION_TRIAL.md`

## 本轮改动

### P4.0

- 用一条新的真实脚本验证主线是否能稳定用于下一条真实内容
- preview / approval / MP4 全链路均按 runbook 跑通
- 确认当前主线可用于后续真实内容试跑

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `render_mp4 --approved` on `p4_first_real_script_preview`

## 交付物

- `docs/status/P4_0_FIRST_REAL_SCRIPT_PRODUCTION_TRIAL.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-03
