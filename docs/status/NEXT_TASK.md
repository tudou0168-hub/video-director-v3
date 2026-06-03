# NEXT TASK

## 当前任务

**P3.13D Lightweight Sales Polish + P3.14 Operator Runbook Prep** — 正在做 sales 轻量 polish，同时整理 operator runbook，让后续可以稳定复用这条主线。

当前重点：

- `outputs/v3_p313d_sales_polish_preview/`
- `docs/runbooks/CREATE_VIDEO.md`
- `docs/runbooks/REVIEW_PREVIEW.md`
- `docs/runbooks/RENDER_MP4.md`
- `docs/runbooks/TROUBLESHOOTING.md`
- `docs/status/P3_13D_LIGHTWEIGHT_SALES_POLISH.md`
- `docs/status/P3_14_OPERATOR_RUNBOOK_PREP.md`

## 本轮改动

### P3.13D

- 对 sales contract-driven preview 做轻量 polish，减少 repeated role / repeated template 噪音
- 本地执行 sales MP4 polish trial，音视频与同步均通过
- 新增 operator runbook，让后续可以稳定复用主线

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `render_mp4 --approved` on `v3_p313d_sales_polish_preview`

## 交付物

- `docs/status/P3_13D_LIGHTWEIGHT_SALES_POLISH.md`
- `docs/status/P3_14_OPERATOR_RUNBOOK_PREP.md`
- `docs/runbooks/CREATE_VIDEO.md`
- `docs/runbooks/REVIEW_PREVIEW.md`
- `docs/runbooks/RENDER_MP4.md`
- `docs/runbooks/TROUBLESHOOTING.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-03
