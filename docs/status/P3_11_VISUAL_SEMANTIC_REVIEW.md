# P3.11 Visual + Semantic Review

## 阶段结论

P3.11 的结论是 **no-go for P3.12**。

当前三条 P3.10 real preview 都已经通过 `scene_pack / template_contracts / semantic_quality / approval gate`，但从 contact sheet 与 scene-level 内容来看，画面与语义仍然不够稳，不适合直接进入 `P3.12 Publish Candidate Selection`。

下一步建议先进入 **P3.11B Semantic Quality Gate Calibration**。

理由：
- 三条 preview 的 `semantic_quality_score` 都是 `106.0`，但肉眼可见仍存在早 CTA、抽象 proof、重复性模板和局部语义偏薄的问题
- 这说明 gate 分数偏乐观，`worst_3_scenes` 也没有充分反映肉眼问题
- 先校准 gate，比直接修单个 scene 更能防止后续把不够好的内容误判为候选片

## 3 条 Preview 对比表

| preview_id | total_scenes | approval_status | semantic_quality_score | fallback_count | proof_scene_count | cta_scene_count | chinese_dominance_score | contact_sheet_exists | publish_candidate_status |
|---|---:|---|---:|---:|---:|---:|---:|---|---|
| `v3_p310_batch_knowledge_preview` | 14 | `READY` / `can_approve_preview=true` | 106.0 | 0 | 2 | 3 | 0.934 | yes | `no-go` |
| `v3_p310_batch_sales_preview` | 13 | `READY` / `can_approve_preview=true` | 106.0 | 0 | 2 | 4 | 0.983 | yes | `no-go` |
| `v3_p310_batch_toolflow_preview` | 13 | `READY` / `can_approve_preview=true` | 106.0 | 0 | 2 | 1 | 0.955 | yes | `no-go` |

## 基础状态汇总

### `v3_p310_batch_knowledge_preview`

- total_scenes: 14
- preview_status: `READY`
- can_approve_preview: `true`
- fallback_count: 0
- raw_text_dependency_count: 0
- slot_missing_count: 0
- placeholder_count: 0
- role_template_mismatch_count: 0
- proof_scene_count: 2
- cta_scene_count: 3
- chinese_dominance_score: 0.934
- semantic_quality_score: 106.0
- worst_3_scenes: `S02 final_cta`, `S03 problem_conflict`, `S06 method_steps`
- contact_sheet_exists: `yes`

### `v3_p310_batch_sales_preview`

- total_scenes: 13
- preview_status: `READY`
- can_approve_preview: `true`
- fallback_count: 0
- raw_text_dependency_count: 0
- slot_missing_count: 0
- placeholder_count: 0
- role_template_mismatch_count: 0
- proof_scene_count: 2
- cta_scene_count: 4
- chinese_dominance_score: 0.983
- semantic_quality_score: 106.0
- worst_3_scenes: `S03 final_cta`, `S06 final_cta`, `S11 before_after`
- contact_sheet_exists: `yes`

### `v3_p310_batch_toolflow_preview`

- total_scenes: 13
- preview_status: `READY`
- can_approve_preview: `true`
- fallback_count: 0
- raw_text_dependency_count: 0
- slot_missing_count: 0
- placeholder_count: 0
- role_template_mismatch_count: 0
- proof_scene_count: 2
- cta_scene_count: 1
- chinese_dominance_score: 0.955
- semantic_quality_score: 106.0
- worst_3_scenes: `S02 problem_conflict`, `S12 concept_layers`, `S01 hook`
- contact_sheet_exists: `yes`

## 视觉语义审查

### 1) `v3_p310_batch_knowledge_preview`

总体结论：
- 结构最完整，但 CTA 过早，且结尾 CTA 过多
- proof 有承载，但偏案例化，可信度还不够强
- contact sheet 里前半段的 `hook -> early CTA -> problem -> proof` 节奏会让人觉得“故事还没展开就开始收口”

Top 3 问题：

1. `S02 / final_cta`
   - 问题类型: CTA 过早
   - 为什么影响发布: 开头 2 帧内就出现收口动作，削弱了 hook 的悬念，也让后续内容像在补说明
   - 建议: 进入 `P3.11C`

2. `S13 / final_cta`
   - 问题类型: CTA 过多
   - 为什么影响发布: 中后段已经完成收口，最后又继续重复 CTA，会让结尾的完成感变弱
   - 建议: 进入 `P3.11C`

3. `S09 / case_study_card`
   - 问题类型: proof 可信承载偏弱
   - 为什么影响发布: “案例卡”有结构，但证据仍较抽象，没有清晰的量化或可验证支撑
   - 建议: 进入 `P3.11B`

CTA 审查：
- 过早：是
- 过多：是
- 可信：一般
- 自然：一般
- 不符合用户偏好中的“评论区打关键词领取资料”话术，但仍有过度收口的问题

Proof 审查：
- proof 不是空白，但更多像“经验案例”而不是强证据
- 没有明显假指标
- 仍需更强的 offer/proof/CTA 结构分离

视觉审查：
- 中文主导：基本成立
- 英文：主要是 HUD 标签，比例可接受
- 画面密度：前半段略密，后半段可读性更好
- 空卡片：未见明显空卡
- placeholder：未见明显 placeholder
- 字幕安全区：总体安全，但末帧 CTA 区域略拥挤
- contact sheet 可读性：中等偏上，节奏可读，但不够像 publish candidate

QA Gate 审查：
- `semantic_quality_score=106.0` 明显偏乐观
- `worst_3_scenes` 选中的最差场景里，有些确实是肉眼薄弱项，但没有完整覆盖早 CTA 和结尾过度收口问题
- `approval_required` 过宽松，已经不能单独作为发布候选判断依据

### 2) `v3_p310_batch_sales_preview`

总体结论：
- 三条里最像“成交流程”，但也是 CTA 最密的一条
- proof 里有真实案例感，但仍偏抽象，容易显得像结构正确但内容不够硬
- contact sheet 上中段视觉表现稳定，但结尾重复 CTA 太多，削弱了收口力度

Top 3 问题：

1. `S03 / final_cta`
   - 问题类型: CTA 过早
   - 为什么影响发布: 在前段就进入 action 收口，导致前面的 problem / proof 还没充分建立就急着转化
   - 建议: 进入 `P3.11C`

2. `S06 / final_cta`
   - 问题类型: CTA 过多
   - 为什么影响发布: 中段再次 CTA，会让整条内容像不断催促下一步，而不是自然推进
   - 建议: 进入 `P3.11C`

3. `S09 / proof`
   - 问题类型: proof 可信承载偏弱
   - 为什么影响发布: 结构上是 proof，但证据还是“真实案例”这种泛化描述，不足以支撑成交判断
   - 建议: 进入 `P3.11B`

CTA 审查：
- 过早：是
- 过多：是
- 可信：一般
- 自然：偏弱
- 没有出现用户明确不喜欢的“评论区打关键词领取资料”话术，但整体还是偏催促

Proof 审查：
- proof 不是假的，但不够硬
- 与前文主张有对应关系
- 缺少可验证承载，容易让人觉得是“讲得对”但不够“证得住”

视觉审查：
- 中文主导：很好
- 英文：HUD 标签比例正常
- 画面密度：中等，整体比知识流更均衡
- 空卡片：未见明显空卡
- placeholder：未见明显 placeholder
- 字幕安全区：总体安全
- contact sheet 可读性：三条里最好，但仍不足以成为候选片

QA Gate 审查：
- `semantic_quality_score=106.0` 明显偏乐观
- `worst_3_scenes` 抓到 `final_cta` 和 `before_after`，说明局部问题存在，但没有把 CTA 过多这一类结构性问题完整表达出来
- `approval_required` 对视觉观感的约束不够

### 3) `v3_p310_batch_toolflow_preview`

总体结论：
- 这条最克制，CTA 最少，视觉也相对清爽
- 但前半段问题堆得较密，`problem_conflict` 重复出现，像是先把痛点打满，再进入流程，仍有“模板感”
- proof 有，但仍偏案例描述，不够强证据

Top 3 问题：

1. `S02 / problem_conflict`
   - 问题类型: 结构重复 / 前段压迫感过强
   - 为什么影响发布: 进入太早，而且跟后续 `S03` 重复同类冲突结构，节奏上显得闷
   - 建议: 进入 `P3.11C`

2. `S12 / concept_layers`
   - 问题类型: 视觉与语义偏薄
   - 为什么影响发布: 末段方法层更多是概念拆层，缺少更强的收束力量，像总结而不是结论
   - 建议: 进入 `P3.11B`

3. `S01 / hook`
   - 问题类型: hook 力度一般
   - 为什么影响发布: 虽然是 hook，但视觉冲击和语义张力没有明显压住后续内容
   - 建议: 进入 `P3.11C`

CTA 审查：
- 过早：否，整体是三条里最克制的
- 过多：否
- 可信：一般
- 自然：相对最好
- 没有用户明确不喜欢的“评论区打关键词领取资料”话术

Proof 审查：
- proof 比另两条略稳
- 但依旧偏案例卡，不够“证据型”
- 需要更强的 proof 承载方式支撑后续 offer/proof/CTA 系统升级

视觉审查：
- 中文主导：成立
- 英文：辅助标签为主
- 画面密度：前半段偏密，后半段正常
- 空卡片：未见明显空卡
- placeholder：未见明显 placeholder
- 字幕安全区：总体安全
- contact sheet 可读性：中等偏上，但前半段重复痛点降低了第一眼吸引力

QA Gate 审查：
- `semantic_quality_score=106.0` 仍然过高
- `worst_3_scenes` 抓到 `problem_conflict`、`concept_layers`、`hook`，这与肉眼感受基本一致，但还不足以成为完整可发布判断
- `approval_required` 允许人眼继续，但不够严格地阻止“看起来像成品、实际还不稳”的情况

## CTA 审查总评

三条里都没有出现用户明确不喜欢的“评论区打关键词领取资料”式低质 CTA，但整体 CTA 的主要问题不是话术，而是位置和频率。

结论：
- `knowledge`：CTA 过早、过多
- `sales`：CTA 过早、过多，最明显
- `toolflow`：CTA 相对自然，但前半段痛点堆叠太重

当前 CTA 还没有达到 publish candidate 所需的节奏感。

## Proof 审查总评

三条都没有明显假指标，也没有明显 placeholder proof，但 proof 仍然偏“案例型说明”，而不是“可验证证据”。

结论：
- `knowledge`：proof 有承载，但偏抽象
- `sales`：proof 与成交主张相关，但可信承载不够硬
- `toolflow`：proof 比较稳，但仍偏经验性

后续仍需要更强的 `offer / proof / CTA` 系统增强。

## 视觉审查总评

三条都满足：
- 中文主导
- 英文只是 HUD 辅助
- 没有明显空卡片
- 没有明显 placeholder
- contact sheet 基本能看出主信息

但也都存在共性问题：
- 前半段局部过密
- 结尾 CTA 过于结构化
- 部分场景的视觉语义还停留在“模板对了”，没有到“内容真的硬了”

## QA Gate 审查总评

当前 `semantic_quality_score=106.0` 明显偏乐观，不能单独作为 publish candidate 依据。

`worst_3_scenes` 有一定参考价值，但还没有把“早 CTA、重复 CTA、proof 过抽象”这些更影响发布的结构性问题完整暴露出来。

因此：
- QA gate 现在能挡住明显的空卡、缺 slot、raw_text dependency
- 但还挡不住“整体看起来像过审，实际还不够 publish”的内容

## Publish Candidate 建议

**结论：三条都不建议进入 `P3.12 Publish Candidate Selection`。**

推荐顺序不是“谁可以直接发布”，而是“谁更适合成为后续修复基准”：

1. `v3_p310_batch_toolflow_preview`
   - 最克制，CTA 最少
   - 更适合作为 P3.11B / P3.11C 修复基准

2. `v3_p310_batch_sales_preview`
   - 结构最像成交流程
   - 但 CTA 过密，proof 偏抽象，适合做 gate 校准参考

3. `v3_p310_batch_knowledge_preview`
   - 结构完整，但早 CTA 和结尾 CTA 过多最明显
   - 更适合作为“如何不把 CTA 做太早”的反例

进入 `P3.12` 前必须修的问题：
- 校准 `semantic_quality_score`，让分数能反映肉眼问题
- 让 `worst_3_scenes` 更真实地暴露早 CTA、重复 CTA、proof 偏弱等结构性问题
- 让 `final_cta` 只在真正合适的收口点出现
- 提升 proof 的可信承载，而不是只保留“真实案例”这种泛化描述

## 下一步路由

**建议进入：`P3.11B Semantic Quality Gate Calibration`**

理由：
- 当前最大问题不是单条 preview 的局部坏点，而是 gate 过宽、分数过乐观
- 先把评分和 `worst_3_scenes` 调准，后续 `P3.11C` 的 scene 修复才有可靠依据

如果在 P3.11B 后仍然看到某些具体 scene 明显偏弱，再进入 `P3.11C Worst 3 Scene Repair`

## 结论摘要

- `P3.11`：no-go for `P3.12`
- publish candidate：无
- 下一步：`P3.11B Semantic Quality Gate Calibration`
- 必要时再接 `P3.11C Worst 3 Scene Repair`
