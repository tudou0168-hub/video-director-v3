# P4.1B-R4 Follow-up Contact Sheet Review

日期：2026-06-04  
预览目录：`outputs/p4_1b_r4_followup_visual_rules_preview/`

## 预览基础状态

- `preview_status = READY`
- `approval_required.status = pending_human_review`
- `can_approve_preview = true`
- `review_frames_status = PASS`
- `gate_status = PASS`
- `hard_fail_reasons = []`
- `semantic_quality_score = 55.26`
- `score_band = FAIL`
- `publish_candidate_readiness = NO_GO`

说明：

- 这条 smoke 的目标是验证 R4 通用构图规则，不是发布候选片筛选。
- 所以下面的人工判断只讨论“构图有没有真实进入 contact sheet”，不把它写成“已适配所有文案”。

## 逐 panel 人工验收表

| panel | timestamp | layout_family | caption style unified | center occupancy | glass card placement | viral hook/readability | overlap issue | pass/fail |
|---|---:|---|---|---|---|---|---|---|
| 1 | `0.5s` | `hero_metric` | `yes`，caption 已退到底部辅助层 | 中央重心清楚，左大数字+右 anchor 成立 | 右侧 glass card 不再压主标题 | 开场识别度高，数字+单位可读 | 无明显碰撞；subtitle 区仍略密 | `pass` |
| 2 | `19.5s` | `tool_pipeline` | `yes`，caption 不再压节点主体 | 主体集中在节点区与结果卡之间 | 左节点卡、右结果卡位置清楚 | “流程感”明显，比旧竖排卡更像 pipeline | 无明显重叠 | `pass` |
| 3 | `38.5s` | `tool_pipeline` | `yes` | 中区和右上结果区平衡 | glass card 与 flow line 间距稳定 | 第二张 pipeline 仍然可读 | 无明显重叠；caption 仍可见但不主导 | `pass` |
| 4 | `57.5s` | `framework_map` | `yes` | 中央结构图占比提升 | 右侧 structure 卡位置合理 | 比旧列表态更像结构图 | 无硬碰撞；左下 insight 卡仍稍拥挤 | `pass` |
| 5 | `76.4s` | `framework_map` | `yes` | 中央可读性尚可 | glass card 层级比上一轮稳定 | 主信息能一眼看懂，但字量仍偏多 | 无硬碰撞；仍有“略挤”风险 | `pass` |
| 6 | `95.4s` | `action_close` | `yes` | 收束重心清楚 | 左侧 action list 与右侧 reason 卡分区稳定 | 已不再出现占位词，close 页语义正常 | 无明显重叠 | `pass` |
| 7 | `114.4s` | `checklist_close` | `yes` | 收束板整体集中 | 左 checklist、右 CTA / reason 分层清楚 | 已无 `FINAL SCORE / COMPLETE` 影子；无 policy 禁用短语泄露 | 无明显重叠 | `pass` |

## 重点核验

### 1. close 页旧语义

人工判断：

- 没再看到 `FINAL SCORE`
- 没再看到 `COMPLETE`
- 没再看到旧 score sheet 影子

### 2. fallback 文案泄露

人工判断：

- 没再看到 `这一帧需要补充语义内容`

### 3. CTA policy 泄露

人工判断：

- 没再看到 `评论区打关键词领取资料`
- 没再看到 `私信领取资料`
- close 页显示的是正向动作，而不是禁用短语列表

### 4. caption 降权

人工判断：

- caption 已经统一退到辅助层
- 仍然可见，但不再压主视觉
- 对 `framework_map` 和 `tool_pipeline` 的干扰比上一轮明显下降

## 这一轮仍然保留的问题

1. `framework_map` 仍然有“信息略挤”的风险，尤其是长句场景。
2. `hero_metric` 的下方支持文案仍有一点密度偏高，不算碰撞，但还可继续成熟。
3. `semantic_quality_score` 依旧不高，这提醒我们这条产物仍然只是 smoke 验证，不是发布候选。

## 结论表达边界

这份审查只能说明：

- 通用 skeleton 构图规则已经真实进入当前 smoke 的 contact sheet
- 当前 smoke 的 close / caption / pipeline / framework / hero 都比上一轮更稳定

这**不能**说明：

- 已经适配所有文案
- 可以直接进入多脚本验证
- 可以直接进入 MP4 产出

## 下一步建议

在当前边界下，更稳妥的下一步是：

- `P4.1B-R4 Follow-up Fix`

原因：

- 本轮 contact sheet 已经接近目标，但 `framework_map` 和 `hero_metric` 还存在轻微密度问题
- 在没有更多人工确认前，不建议直接跳进 `P4.1B-R5`

