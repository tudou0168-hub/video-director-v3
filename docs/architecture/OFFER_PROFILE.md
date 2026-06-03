# Offer Profile

Offer profile 是成交结构的显式契约，负责把“卖什么、给谁、怎么给、风险如何反转、下一步是什么”写成结构化字段。

## 作用

- 给 semantic director 提供稳定的成交目标
- 给 scene_pack 提供 offer 级别的约束引用
- 给 CTA 和 proof 提供共同的语义锚点

## 字段

- `profile_id`
- `target_user`
- `core_promise`
- `delivery_shape`
- `risk_reversal`
- `next_step`
- `prohibited_cta`

## 原则

- core promise 必须清楚
- next step 必须可执行
- prohibited CTA 必须明确列出
- 不允许用关键词猜 offer

## 当前默认档

`samples/offers/default_ai_content_system.yaml`

