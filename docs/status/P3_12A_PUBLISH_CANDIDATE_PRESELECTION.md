# P3.12A Publish Candidate Preselection

## 1. 阶段结论

**有候选片。**

本阶段基于 P3.11C 的三条新 preview，做了 publish candidate 预选判断。

### 结论

- 可以进入 **P3.12 Publish Candidate Selection**
- 推荐首选：`v3_p311c_sales_repair_preview`
- `knowledge` / `toolflow` 暂不作为首选候选片

## 2. 三条 preview 对比表

| preview_id | total_scenes | approval_status | semantic_quality_score | fallback_count | proof_scene_count | cta_scene_count | chinese_dominance_score | contact_sheet_exists | publish_candidate_status |
|---|---:|---|---:|---:|---:|---:|---:|---|---|
| `v3_p311c_knowledge_repair_preview` | 14 | `READY` | `80.60` | 0 | 2 | 1 | `0.942` | yes | `secondary` |
| `v3_p311c_sales_repair_preview` | 13 | `READY` | `84.77` | 0 | 1 | 1 | `0.984` | yes | `recommended` |
| `v3_p311c_toolflow_repair_preview` | 13 | `READY` | `77.77` | 0 | 2 | 1 | `0.971` | yes | `secondary` |

## 3. 候选片判断依据

### `v3_p311c_sales_repair_preview`

- `gate_status`: `PASS`
- `score_band`: `REVIEW`
- `publish_candidate_readiness`: `REVIEW`
- `hard_fail_reasons`: none
- `fallback_count`: 0
- `raw_text_dependency_count`: 0
- `placeholder_count`: 0
- `role_template_mismatch_count`: 0
- `cta_distribution_risk`: `low`
- `proof_strength_risk`: `low`
- `hook_strength_risk`: `low`
- `contact_sheet_exists`: `yes`
- 人眼审查：主信息可读、节奏完整、收口自然

### 为什么推荐它

- 三条里结构最均衡
- 早 CTA 已消失
- proof 已从抽象变成具体承载
- CTA 只剩尾部收束
- 画面上看，最后一帧是明确的收尾板，不像中途催收口

## 4. 其他两条为什么不是首选

### `v3_p311c_knowledge_repair_preview`

- 优点：早 CTA 已修复，proof 抽象问题下降明显
- 问题：中段 method 重复仍较明显，`repetition_risk = high`
- 结论：可作为备选，不作为首选候选片

### `v3_p311c_toolflow_repair_preview`

- 优点：CTA 和 proof 都已经比旧版稳
- 问题：重复 role / template 仍然偏多，`repetition_risk = high`
- 结论：暂不作为首选候选片

## 5. 是否允许进入正式 P3.12 Publish Candidate Selection

**允许。**

### 推荐顺序

1. `v3_p311c_sales_repair_preview`
2. `v3_p311c_knowledge_repair_preview`
3. `v3_p311c_toolflow_repair_preview`

## 6. 进入 P3.12 前还需要修哪些问题

对首选候选片 `sales` 而言：

- 继续观察中段 result_summary 的重复感
- 如果要进一步抬高候选片质量，可以做一次视觉层面的轻量 polish

对 `knowledge` / `toolflow` 而言：

- 还需要再压一轮 repeated role / repeated template
- 如果想把它们也推到更强候选，建议做 `P3.11D`

## 7. 是否需要 P3.11D 再修一轮

**不是必须。**

如果目标只是选出一个进入 P3.12 的候选片，当前结果已经够用。

如果目标是把三条都进一步抬高，尤其是 knowledge / toolflow，则可以再做一轮 `P3.11D`，专门修重复结构。

## 8. 下一步建议

进入 **P3.12 Publish Candidate Selection**，首选 `v3_p311c_sales_repair_preview`。

