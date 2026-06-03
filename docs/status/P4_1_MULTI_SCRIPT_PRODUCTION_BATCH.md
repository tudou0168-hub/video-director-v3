# P4.1 Multi-Script Production Batch

## 阶段结论

P4.1 **通过**，主线可以批量复用。

本轮完成了 3 条真实脚本的连续试跑，其中：

- 3 条脚本都成功生成 preview
- 2 条达到 `approval READY`
- 1 条可以做本地 MP4 trial，且 trial 通过
- 证明当前主线可以继续用于下一批真实内容

但这轮也保留了一个真实边界：

- `knowledge_method` 这条 preview 生成成功，但 `template_contracts` 未通过，因此不进入发布候选
- 这不是主线故障，而是内容结构与模板契约的匹配度还不够高

## 三条脚本信息表

| script | preview_id | preview 输出 | 结论 |
|---|---|---|---|
| 知识方法型 | `p4_1_batch_knowledge_method_preview` | `outputs/p4_1_batch_knowledge_method_preview/` | preview 成功，但不达发布 |
| 工具流程型 | `p4_1_batch_ai_toolflow_preview` | `outputs/p4_1_batch_ai_toolflow_preview/` | preview READY，可继续复用 |
| 销售转化型 | `p4_1_batch_sales_offer_preview` | `outputs/p4_1_batch_sales_offer_preview/` | preview READY，已通过本地 MP4 trial |

## Preview 汇总

### 1) knowledge_method

- `total_scenes`: 21
- `gate_status`: PASS
- `preview_status`: READY
- `can_approve_preview`: True
- `score_band`: FAIL
- `publish_candidate_readiness`: NO_GO
- `semantic_quality_score`: 61.89
- `hard_fail_reasons`: []
- `fallback_count`: 1
- `raw_text_dependency_count`: 0
- `placeholder_count`: 0
- `role_template_mismatch_count`: 0
- `cta_policy_risk`: None
- `proof_asset_risk`: None
- `offer_profile_risk`: None
- `worst_3_scenes`:
  - `S13 / knowledge_graph / repeated_role + fallback_used + contract_not_pass`
  - `S15 / progress_tracker / abstract_proof + generic_proof`
  - `S06 / problem_conflict / repeated_template + repeated_role`
- `approval_required`:
  - `preview_status`: FAILED
  - `can_approve_preview`: False
  - `failed_required_stages`: template_contracts
  - `required stages`: not all passed

### 2) ai_toolflow

- `total_scenes`: 24
- `gate_status`: PASS
- `preview_status`: READY
- `can_approve_preview`: True
- `score_band`: REVIEW
- `publish_candidate_readiness`: REVIEW
- `semantic_quality_score`: 77.83
- `hard_fail_reasons`: []
- `fallback_count`: 0
- `raw_text_dependency_count`: 0
- `placeholder_count`: 0
- `role_template_mismatch_count`: 0
- `cta_policy_risk`: None
- `proof_asset_risk`: None
- `offer_profile_risk`: None
- `worst_3_scenes`:
  - `S19 / problem_conflict / repeated_template + repeated_role`
  - `S20 / problem_conflict / repeated_template + repeated_role`
  - `S10 / method_steps / repeated_role`
- `approval_required`:
  - `preview_status`: READY
  - `can_approve_preview`: True
  - `failed_required_stages`: none
  - `required stages`: all passed

### 3) sales_offer

- `total_scenes`: 20
- `gate_status`: PASS
- `preview_status`: READY
- `can_approve_preview`: True
- `score_band`: REVIEW
- `publish_candidate_readiness`: REVIEW
- `semantic_quality_score`: 75.05
- `hard_fail_reasons`: []
- `fallback_count`: 0
- `raw_text_dependency_count`: 0
- `placeholder_count`: 0
- `role_template_mismatch_count`: 0
- `cta_policy_risk`: None
- `proof_asset_risk`: None
- `offer_profile_risk`: None
- `worst_3_scenes`:
  - `S12 / proof / repeated_template + repeated_role`
  - `S13 / proof / repeated_template + repeated_role`
  - `S14 / proof / repeated_template + repeated_role`
- `approval_required`:
  - `preview_status`: READY
  - `can_approve_preview`: True
  - `failed_required_stages`: none
  - `required stages`: all passed

## Contact sheet 人工审查

### knowledge_method

- 主信息可读：是
- 空卡片：未见明显空卡
- 低质 CTA：未见
- proof 空泛：有一点，主要集中在 progress / 收束类场景
- 字幕安全区冲突：未见明显冲突
- 画面是否过密：中等偏高
- 是否值得进入 MP4 trial：不建议，先修契约匹配

### ai_toolflow

- 主信息可读：是
- 空卡片：未见明显空卡
- 低质 CTA：未见
- proof 空泛：轻微，但整体可接受
- 字幕安全区冲突：未见明显冲突
- 画面是否过密：中等
- 是否值得进入 MP4 trial：可以，但优先级低于 sales

### sales_offer

- 主信息可读：是
- 空卡片：未见明显空卡
- 低质 CTA：未见
- proof 空泛：没有明显空泛
- 字幕安全区冲突：未见明显冲突
- 画面是否过密：中等，最后收束清楚
- 是否值得进入 MP4 trial：是

## MP4 Trial

本轮只对 1 条做了本地 MP4 trial：

- `outputs/p4_1_batch_sales_offer_preview/rendered/final_video.mp4`
- `render_status`: PASS
- `video_stream`: True
- `audio_stream`: True
- `sync_status`: PASS
- `duration`: 111.60s

## 结论

### 1. 主线是否可批量复用

可以。

这轮证明：

- 新脚本可以稳定进入 preview
- 2 条脚本达到了 `approval READY`
- sales 脚本可直接进入本地 MP4 trial 并通过
- 当前主线可以继续用在下一批真实内容上

### 2. 哪条最稳

`sales_offer` 最稳，适合作为当前批次的优先复用模板。

### 3. 哪条需要回炉

`knowledge_method` 需要先修模板契约匹配或重构句子组织，再谈发布。

## 下一步建议

- 继续复用主线，进入下一批真实脚本试跑
- 如果要做知识方法型内容，先做一次轻量 polish，重点清掉 `knowledge_graph` / `progress_tracker` 的重复角色噪音
- 暂时不扩系统，不扩模板，不动 renderer

## 交接备注

- 不提交 `outputs/`
- 不提交 `renders/`
- 不提交 `final_video.mp4`
- 不提交 `contact-sheet.jpg`
- 不把 `narrative_compressor.py` 接入主线
