# Visual Strategy Pack

`visual_strategy` 是 V3 在 `scene_pack` 之上的视觉分化层，用来把同一条文案明确收敛成不同的视频骨架，而不是让模板继续靠原始全文猜内容。

P4.1B-R1 之后，这一层已经进入 render-effective 阶段：

- `layout_family` 真正影响 HyperFrames Native HTML 预览的布局类名
- `caption_mode` 真正影响字幕 class 和字幕区域视觉强度
- `ending_variant` 真正影响结尾板形态
- `memory_anchor` / `visual_object` / `save_reason` 真正进入 scene 和 QA 报告

## 作用

- 识别脚本更像 `knowledge_method`、`ai_toolflow` 还是 `sales_offer`
- 为整条视频选择不同的 `opening_variant`、`ending_variant` 和 `template_sequence_signature`
- 为每一幕生成 `caption_mode`、`visual_role`、`sequence_slot`、`layout_band`
- 给 QA gate 提供 `differentiation_score`、`layout_readability_score`、`caption_conflict_count` 等可读性与差异化指标

## 输入

优先级从高到低：

1. `script.md` / 真实脚本文本
2. frontmatter 里的 `content_role`
3. `title`
4. `narration_plan`
5. `storyboard`

当前策略包在 `content_role` 明确时优先使用它：

- `知识方法型` → `knowledge_method`
- `工具流程型` → `ai_toolflow`
- `销售转化型` → `sales_offer`

## 输出

### 顶层字段

- `video_type`
- `visual_strategy_id`
- `opening_variant`
- `ending_variant`
- `template_sequence_signature`
- `visual_strategy`
- `memory_anchor`
- `save_reason`
- `visual_object`
- `layout_family_sequence`

### scene_pack scene 字段

- `caption_mode`
- `visual_role`
- `sequence_slot`
- `visual_strategy_reason`
- `layout_band`
- `headline_compact`
- `title_caption_similarity`
- `readability_risk`
- `layout_family`
- `visual_object`
- `visual_headline`
- `memory_anchor`
- `save_reason`

### QA 字段

- `template_sequence`
- `dominant_template_count`
- `repeated_opening_risk`
- `repeated_ending_risk`
- `template_repetition_risk`
- `caption_mode_repetition_risk`
- `differentiation_score`
- `top_heavy_risk`
- `title_caption_overlap_risk`
- `long_headline_count`
- `dense_scene_readability_risk`
- `caption_conflict_count`
- `layout_readability_score`
- `same_video_risk`
- `headline_fragment_risk_count`
- `visual_object_missing_count`
- `memory_anchor_missing_count`
- `save_reason_missing_count`

## 设计原则

- `knowledge_method` 更偏方法、框架、层次、结论
- `ai_toolflow` 更偏工具栈、工作流、进度、结构
- `sales_offer` 更偏痛点、对比、证据、成交收束
- 最后一幕 CTA 保持稳定，不把它变成空心收尾
- 模板不能再直接读原始全文猜 body content，只能消费 `scene_pack`

## 与 QA 的关系

`semantic_quality_gate` 不只看槽位是否完整，还会看：

- 是否重复使用同一种模板骨架
- 是否过度堆叠类似 caption
- 是否顶部信息太重
- 是否标题和字幕过于相似
- 是否真的把三类内容做出了不同的视觉骨架
- 是否真的把 `layout_family` / `caption_mode` / `ending_variant` 消费到渲染层
- 是否真的让 `memory_anchor` / `visual_object` / `save_reason` 成为可读、可记、可复用的视觉锚点

这层的目标不是让分数更高，而是让预览更像三条不同的视频，而不是同一个骨架换内容。
