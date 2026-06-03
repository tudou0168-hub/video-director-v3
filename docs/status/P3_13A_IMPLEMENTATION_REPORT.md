# P3.13A Implementation Report

## 本轮完成内容

完成了 offer / proof / CTA 的显式契约层，并让它们进入语义导演和 QA gate。

### 新增模块

- `src/video_director_v3/director/offer_profile.py`
- `src/video_director_v3/director/proof_asset.py`
- `src/video_director_v3/director/cta_policy.py`

### 新增样本

- `samples/offers/default_ai_content_system.yaml`
- `samples/proofs/default_ai_content_system.yaml`
- `samples/cta/default_value_first.yaml`

### 新增架构文档

- `docs/architecture/OFFER_PROFILE.md`
- `docs/architecture/PROOF_ASSET.md`
- `docs/architecture/CTA_POLICY.md`

### 新增状态文档

- `docs/status/P3_13A_OFFER_PROOF_CTA_SYSTEM.md`
- `docs/status/P3_13A_IMPLEMENTATION_REPORT.md`

## 代码落点

### semantic_planner

`src/video_director_v3/director/semantic_planner.py` 现在会：

- 读取默认 offer / proof / CTA profile
- 给 offer / proof / CTA 场景注入 ref 字段
- 给 final CTA 提供 policy fallback
- 给 proof 提供 evidence source fallback
- 保留旧 scene_pack schema，不破坏现有 pipeline

### scene_pack schema

`src/video_director_v3/director/scene_pack_schema.py` 新增了可选扩展字段：

- `offer_profile_ref`
- `proof_asset_ref`
- `cta_policy_ref`
- `cta_stage`
- `cta_strength`

### semantic quality gate

`src/video_director_v3/qa/semantic_quality_gate.py` 新增检查：

- CTA policy 违规
- 过早 CTA
- 重复 CTA
- 空泛 proof
- fake proof metric
- missing offer core promise

## 结构化字段说明

### offer_profile_ref

指向当前场景使用的 offer profile。用于把“成交承诺”从关键词猜测变成可审计资产引用。

### proof_asset_ref

指向当前场景使用的 proof asset。用于约束 proof 必须带有明确证据来源，而不是泛泛而谈。

### cta_policy_ref

指向当前场景使用的 CTA policy。用于约束 CTA 文案和 CTA 时机，避免低质引导语。

### cta_stage

CTA 所处阶段：

- `opening`
- `mid`
- `late`
- `final`

### cta_strength

CTA 强度：

- `soft`
- `normal`
- `strong`

## 新增测试

- `tests/test_offer_proof_cta_contracts.py`

覆盖：

- contract 加载和校验
- scene_pack optional extension 字段
- sales-like storyboard 的 refs 注入
- forbidden CTA phrase
- fake proof metric

## 预期验收

本轮通过的前提是：

- 仍然不改 HyperFrames renderer
- 仍然不 render MP4
- 仍然不提交 outputs/ 和 renders/
- 仍然保留旧 schema 兼容

