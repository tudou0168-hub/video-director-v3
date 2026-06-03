# P3.13A Offer-Proof-CTA System

## 阶段目标

把成交结构从“靠 scene role + 关键词猜内容”收敛成显式契约：

- `offer_profile`
- `proof_asset`
- `cta_policy`

这些契约作为 `scene_pack` 的可选扩展字段进入语义导演和 QA gate。

## 当前边界

本阶段允许：

- 新增 offer / proof / CTA 契约文件
- 将契约 ref 写入 `scene_pack`
- 让 `semantic_planner` 为销售类脚本注入更稳定的 offer / proof / CTA slots
- 让 `semantic_quality_gate` 对 CTA 违规、伪造 proof 数字、空泛 proof、过早 CTA 做显式拦截

本阶段禁止：

- 改 HyperFrames renderer
- 扩模板库
- render MP4
- 接入 `narrative_compressor.py`
- 回到 `combined/index.html`

## 契约资产

### Offer Profile

- 默认文件：`samples/offers/default_ai_content_system.yaml`
- 代码模块：`src/video_director_v3/director/offer_profile.py`
- 作用：定义目标用户、核心承诺、交付形态、风险回撤、下一步动作

### Proof Asset

- 默认文件：`samples/proofs/default_ai_content_system.yaml`
- 代码模块：`src/video_director_v3/director/proof_asset.py`
- 作用：定义可支撑主张的 evidence items、metric source、credibility note、factual boundaries

### CTA Policy

- 默认文件：`samples/cta/default_value_first.yaml`
- 代码模块：`src/video_director_v3/director/cta_policy.py`
- 作用：定义 CTA 文案偏好、禁用短语、CTA 触发阶段和强度

## scene_pack 新字段

在不破坏旧 schema 的前提下，新增以下 optional 扩展：

- `offer_profile_ref`
- `proof_asset_ref`
- `cta_policy_ref`
- `cta_stage`
- `cta_strength`

这些字段只在 offer / proof / CTA 相关场景上出现。

## QA gate 新检查

- CTA 是否违反 policy
- proof 是否只有空泛词
- offer 是否缺核心承诺
- CTA 是否过早
- CTA 是否重复
- proof 是否伪造数字

## 预期效果

这一步不是为了做更多模板，而是为了让同一批模板在销售场景下：

- 有明确的成交结构
- 有可追踪的证据来源
- 有可审计的 CTA 约束

