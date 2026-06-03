# P3.12 Publish Candidate Selection

## 1. 阶段结论

**选择 `v3_p311c_sales_repair_preview` 作为正式 publish candidate。**

### 结论判断

- 是否选择 sales 为正式候选片：**是**
- 是否允许进入 P3.12B Confirmed MP4 Trial：**是**
- 是否需要 P3.11D：**不需要**
- 是否需要 P3.12 polish pass：**建议可选，但不是进入 trial 的前置条件**

### 说明

这条 preview 已满足候选片选择所需的硬条件：

- `gate_status = PASS`
- `approval_status = READY`
- `hard_fail_reasons = []`
- `fallback_count = 0`
- `raw_text_dependency_count = 0`
- `placeholder_count = 0`
- `role_template_mismatch_count = 0`
- `cta_distribution_risk = low`
- `proof_strength_risk = low`
- `hook_strength_risk = low`
- contact sheet 已存在，且主信息可读

虽然 `semantic_quality_score` 仍是 `REVIEW`，但这是“可候选、可进入 trial”的 REVIEW，不是阻断型问题。

## 2. 候选片基础状态

| 字段 | 值 |
|---|---|
| preview_id | `v3_p311c_sales_repair_preview` |
| total_scenes | `13` |
| semantic_quality_score | `84.77` |
| score_band | `REVIEW` |
| publish_candidate_readiness | `REVIEW` |
| gate_status | `PASS` |
| approval_status | `READY` |
| hard_fail_reasons | `[]` |
| fallback_count | `0` |
| raw_text_dependency_count | `0` |
| placeholder_count | `0` |
| role_template_mismatch_count | `0` |
| contact_sheet_exists | `yes` |

### 风险摘要

- `cta_distribution`:
  - `cta_scene_count = 1`
  - `early_cta_count = 0`
  - `repeated_cta_count = 0`
  - `cta_distribution_risk = low`
- `proof_strength`:
  - `proof_scene_count = 1`
  - `abstract_proof_count = 0`
  - `proof_strength_risk = low`
- `scene_repetition`:
  - `repeated_template_runs = 1`
  - `repeated_role_runs = 2`
  - `repetition_risk = medium`
- `hook_strength`:
  - `hook_scene_id = S01`
  - `hook_strength_risk = low`
- `worst_3_scenes`:
  - `S06 / result_summary / repeated_template + repeated_role`
  - `S05 / result_summary / repeated_template + repeated_role`
  - `S11 / before_after / repeated_role`

## 3. Scene-by-scene 审查表

| scene id | role | template_type | visual_template | 这一幕作用 | 是否通过 | 问题 | 是否必须修 |
|---|---|---|---|---|---|---|---|
| S01 | hook | hook | hook_big_claim | 用强问题开场，先抓注意力 | 通过 | 无 | 否 |
| S02 | explain | concept_layers | concept_layers | 把成交逻辑先抽成结构层 | 通过 | 与后面 summary 相比，仍略偏概念 | 否 |
| S03 | cta | result_summary | section_board | 中段收束，提示下一步动作 | 通过 | 与 S05 / S06 / S10 存在 summary 重复感 | 否 |
| S04 | method | concept_layers | concept_layers | 讲成交路径如何建立 | 通过 | 无 | 否 |
| S05 | evidence | result_summary | section_board | 用结果板承接前文 | 通过 | 与 S03 / S06 / S10 重复感明显 | 否 |
| S06 | cta | result_summary | section_board | 再次推动下一步 | 通过 | 重复 summary，偏“中段 CTA 感” | 否 |
| S07 | pain | problem_conflict | broken_chain | 把成交阻塞点摆出来 | 通过 | 无 | 否 |
| S08 | method | concept_layers | concept_layers | 给出可执行的小方案 | 通过 | 无 | 否 |
| S09 | evidence | proof | before_after_compare | 提供真实案例和路径可信度 | 通过 | 可再更具体，但已足够可信 | 否 |
| S10 | cta | result_summary | section_board | 明确下一步做什么 | 通过 | 再次出现 summary 模式 | 否 |
| S11 | method | before_after | before_after_compare | 把成交路径前后对比讲清 | 通过 | 稍长，但语义清楚 | 否 |
| S12 | method | concept_layers | concept_layers | 面向适用场景做收束解释 | 通过 | 概念层略多，但不阻断 | 否 |
| S13 | cta | final_cta | checklist_cta | 结束收口，给出明确行动 | 通过 | 无 | 否 |

## 4. 发布前 must-fix 清单

### 必须修才能进 MP4

**无。**

当前 sales 候选片没有硬失败，也没有阻断型结构风险。

### 可以带着进入 MP4 trial 的小问题

- S03 / S05 / S06 / S10 的 `result_summary` 存在重复感
- S02 / S04 / S08 / S12 的 `concept_layers` 连续感较强
- S11 的文案略长，但仍可读

### 不影响本轮的后续优化项

- 若进入后续精修，可再考虑把中段某一处 `result_summary` 轻微回收为 `verdict` 或 `offer`
- 若后续要抬高视觉新鲜感，可再做一次轻量的 scene polishing

## 5. MP4 trial 前置条件

在进入 P3.12B Confirmed MP4 Trial 前，需要满足：

- `approval gate = READY`
- contact sheet 人工通过
- semantic_quality 无 hard fail
- 用户明确确认
- 不把 MP4 提交到 GitHub

### 当前判断

这些前置条件已经基本满足，且 `sales` 是最适合进入 trial 的候选片。

## 6. 为什么选择 sales

- 它是三条里结构最均衡的一条
- CTA 已经集中在尾部，不再早出
- proof 已经具体化，不再是抽象口号
- hook 稳定
- 画面信息层次清楚，contact sheet 一眼能看懂主信息

## 7. 结论

**正式选择 `v3_p311c_sales_repair_preview` 进入 P3.12B Confirmed MP4 Trial。**

这一步是发布前确认，不是直接 render MP4。

