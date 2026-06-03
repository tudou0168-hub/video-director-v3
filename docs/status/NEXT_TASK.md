# NEXT TASK

## 当前任务

**P3.13B + P3.13C Contract-Driven Preview Validation and Regression** — 正在验证 P3.13A 的 offer / proof / CTA 契约是否真正进入 preview 链路，并确认没有破坏 knowledge / toolflow 回归。

当前重点：

- `outputs/v3_p313b_sales_contract_preview/`
- `outputs/v3_p313c_knowledge_contract_regression_preview/`
- `outputs/v3_p313c_toolflow_contract_regression_preview/`
- `docs/status/P3_13B_CONTRACT_PREVIEW_VALIDATION.md`
- `docs/status/P3_13C_CONTRACT_REGRESSION_REPORT.md`

## 本轮改动

### P3.13B / P3.13C

- 重新跑 sales preview，确认 refs 进入 scene_pack / semantic_quality / approval 链路
- 重新跑 knowledge / toolflow 回归 preview，确认契约没有引入回归
- 本地执行 sales MP4 regression trial，音视频与同步均通过

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `render_mp4 --approved` on `v3_p313b_sales_contract_preview`

## 交付物

- `docs/status/P3_13B_CONTRACT_PREVIEW_VALIDATION.md`
- `docs/status/P3_13C_CONTRACT_REGRESSION_REPORT.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-03
