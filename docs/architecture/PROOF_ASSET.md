# Proof Asset

Proof asset 是证据结构的显式契约，负责把“证据是什么、支撑什么主张、来源是什么、可信边界是什么”写成结构化字段。

## 作用

- 防止 proof 退化成空泛“真实案例”
- 防止伪造数字和伪造结果
- 为 QA gate 提供证据约束

## 字段

- `asset_id`
- `claim_supported`
- `evidence_items`
- `metric_source`
- `credibility_note`
- `factual_boundaries`

## 原则

- proof 不伪造数字
- proof 不空喊“已验证”
- proof 必须能对上前文主张

## 当前默认档

`samples/proofs/default_ai_content_system.yaml`

