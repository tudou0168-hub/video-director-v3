# P3.13C Contract Regression Report

## 结论

P3.13A 的 offer / proof / CTA 契约没有破坏 knowledge / toolflow 回归。

## 回归预览

### knowledge

- `scene_count = 14`
- `preview_status = READY`
- `gate_status = PASS`
- `can_approve_preview = True`
- `hard_fail_reasons = []`
- `proof_scene_count = 2`
- `cta_scene_count = 1`
- `contact_sheet_exists = True`

### toolflow

- `scene_count = 13`
- `preview_status = READY`
- `gate_status = PASS`
- `can_approve_preview = True`
- `hard_fail_reasons = []`
- `proof_scene_count = 2`
- `cta_scene_count = 1`
- `contact_sheet_exists = True`

## regression 观察

- knowledge 主要风险集中在 repeated role / repeated template，而不是 contract 失败
- toolflow 主要风险同样是 repeated role / repeated template
- 两条回归都没有出现：
  - missing refs
  - forbidden CTA
  - fake proof metric
  - placeholder slots
  - raw text dependency

## sales 对比

sales 预览通过了 contract-driven validation：

- `gate_status = PASS`
- `hard_fail_reasons = []`
- `cta_policy_risk != high`
- `proof_asset_risk != high`
- `contact sheet exists`
- `approval READY`

sales 本地 MP4 regression trial 结果：

- `final_video.mp4` 已生成
- `sync_status = PASS`
- `video_stream = True`
- `audio_stream = True`

## 不建议的方向

- 不要把这批契约再扩成新模板库
- 不要把 reward 分数当成最终发布判断
- 不要回退到 combined/index.html 或自定义播放内核

## 下一步建议

- 如果要继续推进，可以进入 `P3.13D` 做轻量 polish
- 如果当前目标是候选片稳定，可直接保留 sales 这条 contract-driven 路径

