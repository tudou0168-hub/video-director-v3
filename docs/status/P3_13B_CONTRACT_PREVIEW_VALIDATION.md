# P3.13B Contract-Driven Preview Validation

## 阶段目标

验证 P3.13A 新增的 `offer_profile` / `proof_asset` / `cta_policy` 是否真的进入 preview 生成链路。

## 结论

- **sales preview：通过**
- **knowledge regression preview：通过**
- **toolflow regression preview：通过**
- **允许进入本地 MP4 regression trial：已执行并通过**

本阶段未修改 HyperFrames renderer，未扩模板，未提交任何 `outputs/`、`renders/` 或 MP4 到 GitHub。

## preview 输出路径

- `outputs/v3_p313b_sales_contract_preview/`
- `outputs/v3_p313c_knowledge_contract_regression_preview/`
- `outputs/v3_p313c_toolflow_contract_regression_preview/`

## sales preview 审查

### 基础状态

- `preview_status = READY`
- `gate_status = PASS`
- `can_approve_preview = True`
- `score_band = REVIEW`
- `publish_candidate_readiness = REVIEW`
- `hard_fail_reasons = []`

### contract 进入链路

sales 场景中，offer / proof / CTA 相关场景已带上 refs：

- `offer_profile_ref = default_ai_content_system`
- `proof_asset_ref = default_ai_content_system_proof`
- `cta_policy_ref = default_value_first`
- `cta_stage = final`
- `cta_strength = strong`

### QA 结果

- `offer_profile_risk = medium`
- `proof_asset_risk = low`
- `cta_policy_risk = low`
- `fallback_count = 0`
- `raw_text_dependency_count = 0`
- `placeholder_count = 0`
- `role_template_mismatch_count = 0`

### 约束检查

- CTA 未出现 forbidden phrase
- proof 未出现 fake metric
- final CTA 仅在末段收束
- contact sheet 存在
- approval 状态为 READY

## knowledge / toolflow 回归

### knowledge

- `preview_status = READY`
- `gate_status = PASS`
- `can_approve_preview = True`
- `hard_fail_reasons = []`
- `proof_asset_risk = low`
- `cta_policy_risk = low`

### toolflow

- `preview_status = READY`
- `gate_status = PASS`
- `can_approve_preview = True`
- `hard_fail_reasons = []`
- `offer_profile_risk = low`
- `proof_asset_risk = low`
- `cta_policy_risk = low`

## 本地 MP4 regression trial

- 已执行
- 输出路径：`outputs/v3_p313b_sales_contract_preview/rendered/final_video.mp4`
- 状态：`PASS`
- 时长：`75.64s`
- 视频流：有
- 音频流：有
- `sync_status = PASS`
- `max_drift_seconds = 0.248`

## 关键观察

- P3.13A 的契约确实进入了 sales preview 的生成链路
- 旧主线未被破坏
- knowledge / toolflow 没有被销售契约污染
- sales 仍然是 `REVIEW` band，但 preview gate 与 approval gate 是健康的

## 下一步建议

- 进入 `P3.13C Contract Regression Report`
- 如需再收紧，可做轻量 polish，但不必重开契约建设

