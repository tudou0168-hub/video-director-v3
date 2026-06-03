# P4.1B Visual Differentiation + Readability Director

## 阶段结论

- `P4.1B` 通过
- 三条 preview 都进入 `READY`
- `sales`、`ai_toolflow`、`knowledge_method` 的视觉骨架已经显式分化
- 当前不需要回到 renderer 侧重写，也不需要扩模板库
- 可进入下一阶段 `P4.1C` 做人工视觉审查与候选片收口

## 三条 preview 对比

| preview_id | total_scenes | approval_status | semantic_quality_score | fallback_count | proof_scene_count | cta_scene_count | chinese_dominance_score | contact_sheet_exists | publish_candidate_status |
|---|---:|---|---:|---:|---:|---:|---:|---|---|
| `p4_1b_knowledge_visual_strategy_preview` | 21 | `READY` | 41.99 | 0 | 10 | 1 | 0.942 | yes | `REVIEW` |
| `p4_1b_ai_toolflow_visual_strategy_preview` | 24 | `READY` | 42.91 | 0 | 10 | 1 | 0.948 | yes | `REVIEW` |
| `p4_1b_sales_visual_strategy_preview` | 20 | `READY` | 41.95 | 0 | 10 | 1 | 0.943 | yes | `REVIEW` |

说明：
- `semantic_quality_score` 仍然是偏保守的工程分，不代表最终发布评分。
- 真正判断是否可进入下一步，要结合 `visual_strategy`、`worst_3_scenes` 和 contact sheet。

## Stage 状态摘要

| preview_id | gate_status | preview_status | hard_fail_reasons | cta_distribution | proof_strength | scene_repetition | hook_strength |
|---|---|---|---|---|---|---|---|
| `p4_1b_knowledge_visual_strategy_preview` | `PASS` | `READY` | `[]` | `low` | `low` | `low` | `high` |
| `p4_1b_ai_toolflow_visual_strategy_preview` | `PASS` | `READY` | `[]` | `low` | `low` | `low` | `high` |
| `p4_1b_sales_visual_strategy_preview` | `PASS` | `READY` | `[]` | `low` | `low` | `low` | `high` |

`hook_strength` 仍偏高风险，说明开头仍是整个系统里最值得继续打磨的一幕，但它没有破坏本轮的 preview gate。

## 每条 preview 的 top 3 问题

### `p4_1b_knowledge_visual_strategy_preview`

1. `S01` / `hook`
   - 问题类型：hook 偏弱
   - 影响：开头冲击力不够，第一眼仍然偏“讲道理”而不是“先抓人”
   - 建议：进入 `P4.1C`

2. `S13` / `knowledge_graph`
   - 问题类型：中段信息密度偏高
   - 影响：知识图谱节点在 contact sheet 里略挤，阅读成本偏高
   - 建议：进入 `P4.1C`

3. `S14` / `result_summary`
   - 问题类型：收束感偏保守
   - 影响：结尾没有把方法论进一步压成“可执行下一步”
   - 建议：进入 `P4.1C`

### `p4_1b_ai_toolflow_visual_strategy_preview`

1. `S01` / `hook`
   - 问题类型：hook 偏弱
   - 影响：工具流主题需要更强的“问题压迫感”起手
   - 建议：进入 `P4.1C`

2. `S20` / `cta`
   - 问题类型：结尾 CTA 视觉仍偏保守
   - 影响：最后一幕虽然可读，但还可以更像“完成动作”而不是普通收口
   - 建议：进入 `P4.1C`

3. `S12` / `case_study_card`
   - 问题类型：案例化表达偏密
   - 影响：中后段案例卡在 contact sheet 上略重，需要再提炼
   - 建议：进入 `P4.1C`

### `p4_1b_sales_visual_strategy_preview`

1. `S01` / `hook`
   - 问题类型：hook 偏弱
   - 影响：销售转化型内容需要更强的痛点压场
   - 建议：进入 `P4.1C`

2. `S17` / `before_after`
   - 问题类型：中段对比感偏保守
   - 影响：需要更强的“前后变化”视觉差异
   - 建议：进入 `P4.1C`

3. `S02` / `before_after`
   - 问题类型：前段铺垫感偏高
   - 影响：前段还不够像成交片，略像工具讲解
   - 建议：进入 `P4.1C`

## CTA 审查

- 是否过早：否
- 是否过多：否
- 是否可信：是
- 是否自然：基本自然
- 是否出现“评论区打关键词领取资料”类低质 CTA：否

结论：CTA 可以进入下一步，但仍建议在后续 polish 里继续把结尾板做得更强一点。

## Proof 审查

- 是否真实：是
- 是否有假指标：否
- 是否支撑主张：是
- 是否需要 offer / proof / CTA system 后续增强：不需要重开系统，但可以继续优化证据表达密度

## 视觉审查

- 中文主导情况：良好
- 画面密度：整体可读，但知识图谱和案例卡仍有局部偏密
- 空卡片风险：低
- 字幕安全区风险：低
- HUD 风格是否稳定：稳定

## QA Gate 审查

- `semantic_quality_score`：保守且可信
- `worst_3_scenes`：可信，基本指向开头与中后段密度问题
- `approval gate`：不宽松，能挡住明显垃圾产出
- `P4.1B` 之后仍需关注的问题：hook 强度、局部密度、末幕的视觉收束感

## Publish candidate 建议

- 推荐进入下一步的对象：`p4_1b_sales_visual_strategy_preview`
- 但本阶段还不直接做 MP4 发布
- 进入 `P4.1C` 前必须修的问题：
  - 更强的 hook
  - 更清晰的 mid-scene 信息节奏
  - 更像“完成动作”的 CTA 终板

## 下一步路由

**建议进入 `P4.1C`**

理由：
- 三条 preview 已经证明 visual_strategy pack 可以稳定驱动不同内容类型
- 这轮问题已经从“系统不通”转成“开头和局部阅读性还可以继续抠”
- 不需要回头重构 renderer，也不需要扩模板库

---
最后更新：2026-06-04
