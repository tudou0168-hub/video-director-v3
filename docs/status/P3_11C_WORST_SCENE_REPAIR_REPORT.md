# P3.11C Worst Scene Repair Report

## 1. 阶段结论

**P3.11C 通过。**

本阶段已经基于 P3.11B 的 semantic quality gate，修复了三条 preview 里最影响发布的结构问题，并重新生成了三条 preview。

### 结果摘要

- early CTA 明显下降
- repeated CTA 明显下降
- proof 偏抽象问题被压住
- hook 依然稳定
- worst_3_scenes 能够真实反映剩余结构风险

## 2. 修改文件清单

- [src/video_director_v3/director/semantic_planner.py](/Users/muzi/video-director-v3/src/video_director_v3/director/semantic_planner.py)
- [tests/test_scene_pack_contracts.py](/Users/muzi/video-director-v3/tests/test_scene_pack_contracts.py)
- [docs/status/P3_11C_P3_12A_REPAIR_AND_CANDIDATE_PLAN.md](/Users/muzi/video-director-v3/docs/status/P3_11C_P3_12A_REPAIR_AND_CANDIDATE_PLAN.md)

## 3. 修复策略

### 3.1 CTA 回收

- 把前 30% 左右的 CTA 句收回为 `verdict` / `offer`
- 将中段需要的“推进感”改为 `result_summary`
- 仅保留最后一帧作为真正的 `final_cta`

### 3.2 proof 具体化

- proof 不再只落到“真实案例 / 已验证 / 可复用”这类泛词
- `metric_or_evidence` 改为更具体的承载：
  - `前后对比`
  - `执行记录`
  - `流程闭环`
  - `素材包`
- `case_study_card` 补入了 `metric_or_evidence` 与 `credibility_note`

### 3.3 前段重复结构收敛

- 对连续 problem/conflict、cta/offer 做轻量重排
- 让前段结构更像：
  - `hook -> problem -> verdict/method -> proof -> method -> cta`

## 4. 三条 preview 的 before / after 对比

| preview_id | before score / band / readiness | after score / band / readiness | before CTA risk | after CTA risk | before proof risk | after proof risk | before repetition | after repetition |
|---|---:|---:|---|---|---|---|---|---|
| `v3_p310_batch_knowledge_preview` -> `v3_p311c_knowledge_repair_preview` | `68.47 / FAIL / NO_GO` | `80.60 / REVIEW / REVIEW` | `medium` | `low` | `medium` | `medium` | `high` | `high` |
| `v3_p310_batch_sales_preview` -> `v3_p311c_sales_repair_preview` | `73.34 / FAIL / NO_GO` | `84.77 / REVIEW / REVIEW` | `high` | `low` | `medium` | `low` | `medium` | `medium` |
| `v3_p310_batch_toolflow_preview` -> `v3_p311c_toolflow_repair_preview` | `75.62 / REVIEW / REVIEW` | `77.77 / REVIEW / REVIEW` | `low` | `low` | `medium` | `medium` | `high` | `high` |

## 5. 每条新版 preview 的结构摘要

### 5.1 `v3_p311c_knowledge_repair_preview`

- `semantic_quality_score`: `80.60`
- `score_band`: `REVIEW`
- `publish_candidate_readiness`: `REVIEW`
- `cta_distribution_risk`: `low`
- `proof_strength_risk`: `medium`
- `repetition_risk`: `high`
- `hook_strength_risk`: `low`
- `worst_3_scenes`:
  - `S06 / method_steps / repeated_role`
  - `S12 / concept_layers / repeated_role`
  - `S07 / framework_quadrant / repeated_role`

### 5.2 `v3_p311c_sales_repair_preview`

- `semantic_quality_score`: `84.77`
- `score_band`: `REVIEW`
- `publish_candidate_readiness`: `REVIEW`
- `cta_distribution_risk`: `low`
- `proof_strength_risk`: `low`
- `repetition_risk`: `medium`
- `hook_strength_risk`: `low`
- `worst_3_scenes`:
  - `S06 / result_summary / repeated_template + repeated_role`
  - `S05 / result_summary / repeated_template + repeated_role`
  - `S11 / before_after / repeated_role`

### 5.3 `v3_p311c_toolflow_repair_preview`

- `semantic_quality_score`: `77.77`
- `score_band`: `REVIEW`
- `publish_candidate_readiness`: `REVIEW`
- `cta_distribution_risk`: `low`
- `proof_strength_risk`: `medium`
- `repetition_risk`: `high`
- `hook_strength_risk`: `low`
- `worst_3_scenes`:
  - `S02 / result_summary / repeated_template + repeated_role`
  - `S03 / result_summary / repeated_template + repeated_role`
  - `S06 / concept_layers / repeated_template + repeated_role`

## 6. 已被修复的问题

- `v3_p310_batch_knowledge_preview` 的早 CTA 已被回收
- `v3_p310_batch_sales_preview` 的早 CTA 和 repeated CTA 已被清掉
- 三条 preview 的 abstract proof 都明显下降
- 最后一帧 CTA 现在更稳定，且结尾更像收束而不是随意催收

## 7. 仍未完全解决的问题

- 三条 preview 都还有 repeated role / repeated template 的结构性重复
- knowledge / toolflow 的中段方法链仍然偏长
- toolflow 的 repeated_role 风险仍然是高

## 8. 是否存在回归

**没有明显回归。**

检查结果：

- 没有 hard fail
- 没有 fallback 增长
- 没有 raw_text_dependency
- 没有 placeholder
- 没有模板契约失配
- 没有新增 renderer 改写

## 9. 是否仍然 no-go for P3.12

**整体不再是 no-go。**

原因：

- 已经有 1 条较清晰的 publish candidate 预选对象
- gate 能够把问题和候选片区分开
- 人眼审查下，至少一条 preview 的主信息已经足够稳定

但：

- 如果目标是把 3 条都推到更强的 publish 候选，还可以再做一轮 `P3.11D`

## 10. 下一步建议

优先进入 **P3.12 Publish Candidate Selection**，以 `v3_p311c_sales_repair_preview` 为首选。

