# CTA Policy

CTA policy 是结尾与转化动作的显式约束，负责控制 CTA 出现时机、措辞边界和重复频率。

## 作用

- 防止 CTA 过早
- 防止 CTA 过多
- 防止低质催收式 CTA

## 字段

- `policy_id`
- `preferred_cta_text`
- `forbidden_phrases`
- `min_proof_scenes_before_final_cta`
- `max_cta_scenes`
- `early_cta_ratio`
- `strong_cta_ratio`
- `repeated_cta_soft_limit`

## 原则

- 不使用“评论区打关键词领取资料”
- CTA 必须建立在 proof 或 verdict 之后
- CTA 文案应服务于价值，而不是只服务于催收

## 当前默认档

`samples/cta/default_value_first.yaml`

