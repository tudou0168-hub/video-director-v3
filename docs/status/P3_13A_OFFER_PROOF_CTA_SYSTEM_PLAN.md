# P3.13A Offer-Proof-CTA System Plan

## 目标

把成交结构独立成系统，让 `offer`、`proof`、`cta` 不再只依赖 scene role 和简单关键词，而是由显式契约和结构化资产驱动。

## 设想一：offer_profile.yaml

建议为不同内容类型建立 `offer_profile.yaml`：

- `offer_name`
- `target_user`
- `core_promise`
- `delivery_shape`
- `risk_reversal`
- `next_step`
- `prohibited_cta`

用途：

- 统一 offer 语义
- 让 CTA 和 proof 绑定到 offer，而不是绑到 raw 文案
- 避免每次都重新猜“到底卖什么”

## 设想二：proof_asset schema

建议建立 `proof_asset.json` / `proof_asset.yaml` 结构：

- `proof_id`
- `proof_type`
- `claim_supported`
- `evidence_items`
- `metric_source`
- `credibility_note`
- `factual_boundaries`

硬约束：

- proof 不伪造数字
- proof 不空喊“真实案例”
- proof 必须能对应前文主张

## 设想三：CTA policy

CTA 需要独立策略：

- CTA 不能过早出现
- CTA 不能过多重复
- CTA 必须建立在 proof 或明确 verdict 之后
- 禁止“评论区打关键词领取资料”
- 禁止低质、模板化催收式 CTA

## 设想四：与 scene_pack 的结合点

建议把 offer / proof / CTA 作为 scene_pack 的显式语义槽：

- `offer_profile_ref`
- `proof_asset_ref`
- `cta_policy_ref`
- `cta_stage`
- `cta_strength`

这样模板消费的是结构化槽位，不再直接猜正文。

## 后续测试计划

1. Offer profile contract test
2. Proof asset factuality test
3. CTA placement test
4. Early CTA / repeated CTA / fake proof lint
5. Scene pack 与 offer/proof/cta 映射一致性测试

## 本阶段不做

- 不扩模板库
- 不改 renderer
- 不改播放机制
- 不 render MP4
