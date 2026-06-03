# P4.0 First Real Script Production Trial

## 输入脚本

- `samples/scripts/p4_first_real_script.md`

## 试跑目标

用一条新的真实脚本，严格按 runbook 跑完整生产流程，验证当前主线是否可以稳定用于下一条真实内容。

## preview 输出路径

- `outputs/p4_first_real_script_preview/`

## semantic_quality 摘要

- `status = PASS`
- `gate_status = PASS`
- `preview_status = READY`
- `can_approve_preview = True`
- `score_band = REVIEW`
- `publish_candidate_readiness = REVIEW`
- `semantic_quality_score = 75.0`
- `hard_fail_reasons = []`
- `fallback_count = 0`
- `raw_text_dependency_count = 0`
- `placeholder_count = 0`
- `role_template_mismatch_count = 0`

## approval gate

- `preview_status = READY`
- `can_approve_preview = True`
- `review_frames_count = 7`
- `review_frames_status = PASS`

## contact sheet 人工审查结论

- contact sheet 存在
- 主信息可读
- 没有明显空卡片
- CTA 位于末段
- proof 不为空泛内容
- 整体可进入本地 MP4 trial

## 本地 MP4 trial

- 已生成
- 本地路径：`outputs/p4_first_real_script_preview/rendered/final_video.mp4`
- `render_status = PASS`
- `sync_status = PASS`
- `video_stream = True`
- `audio_stream = True`
- 时长：`84.55s`

## 遇到的问题

本轮试跑过程中出现过两次轻量实现问题，但都已收敛：

1. `tool_stack` helper 早期返回 tuple，导致 `scene_pack` 组装失败
2. `case_study_card` / `before_after` 的 role compatibility 需要对齐真实 summary-like 轮换

这两处问题都通过小范围修复收口，没有改 renderer，没有扩模板，没有重开契约系统。

## 是否证明 runbook 可用

- `yes`

理由：

- 能按 runbook 直接跑出 preview
- 能看到 `scene_pack` / `semantic_quality_report` / `approval_required`
- 用户确认前不需要 render MP4
- 用户确认后能稳定进入 `render_mp4`

## 下一步建议

- 继续按 runbook 复用主线，作为下一条真实内容的标准模板
- 若后续要更进一步，优先从内容脚本质量与 repeated role/template 轻量优化入手，而不是重开系统设计

