# NEXT TASK

## 当前任务

**P4.1 Multi-Script Production Batch** — 已完成三条真实脚本的第一轮批量试跑，当前进入结果收口与批量复用判断阶段。

当前重点：

- `outputs/p4_1_batch_knowledge_method_preview/`
- `outputs/p4_1_batch_ai_toolflow_preview/`
- `outputs/p4_1_batch_sales_offer_preview/`
- `docs/status/P4_1_MULTI_SCRIPT_PRODUCTION_BATCH.md`

## 本轮改动

### P4.1

- 用 3 条新的真实脚本验证主线是否可以批量稳定复用
- sales / ai_toolflow preview 通过，knowledge preview 保持回归但未达发布
- sales 通过本地 MP4 trial，确认主线可继续批量试跑真实内容

## 验证

已完成：

- `PYTHONPATH=src .venv/bin/python3 -m pytest`（见 P4.1 批量试跑记录）
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
- `git diff --check`
- `render_mp4 --approved` on `p4_1_batch_sales_offer_preview`

## 交付物

- `docs/status/P4_1_MULTI_SCRIPT_PRODUCTION_BATCH.md`

## 注意

- 不把 MP4 提交到 GitHub
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-03
