# Review Preview Runbook

## 看什么

1. `review_frames/contact-sheet.jpg`
2. `hyperframes_timeline/index.html`
3. `semantic_quality_report.json`
4. `approval_required.json`
5. `scene_pack.json`

## 检查顺序

### 第一层：人眼看 contact sheet

确认：

- 主信息一眼能看懂
- 没有明显空卡片
- 没有低质 CTA
- proof 不是空泛“真实案例”
- 画面里没有明显的 placeholder

### 第二层：看 gate

重点字段：

- `gate_status`
- `hard_fail_reasons`
- `publish_candidate_readiness`
- `cta_policy_risk`
- `proof_asset_risk`
- `semantic_quality_score`

### 第三层：看 scene_pack

确认：

- offer / proof / CTA 场景有 refs
- `cta_stage` 在最后一段才是 `final`
- `cta_policy_ref` / `proof_asset_ref` / `offer_profile_ref` 真实存在

## 常见结果

- `READY`：可以等用户确认后渲染 MP4
- `REVIEW`：可以继续轻量 polish
- `FAIL`：先修 scene_pack / contract / quality gate

