# P4.1B-R3 Layout Skeleton Deepening

日期：2026-06-04

## 目标

把 `layout_family` 从“类名标记”推进到“实际视觉骨架”。  
这轮关注的不是再加字段，也不是扩模板库，而是让同一套 contract-driven scene 在 contact sheet 里呈现出真正不同的结构。

## 本轮输入

- 脚本：`samples/scripts/p4_batch_ai_toolflow.md`
- 输出目录：`outputs/p4_1b_r3_layout_skeleton_smoke_preview/`
- 预览模式：`hyperframes_preview`
- 约束：
  - 不改 HyperFrames renderer 主线
  - 不 render MP4
  - 不扩模板库
  - 不引入新播放机制

## 已做的接骨

- `visual_strategy.choose_layout_family()` 对 AI 工具流开头场景增加了数值识别，数值/时长/量词命中时可进入 `hero_metric`
- `publish_templates.py` 的 contract scene 流程不再只渲染原始 contract body，而是：
  1. 先生成 contract body
  2. 再按 `layout_family` 重新套骨架
  3. 最后交给 Native Preview 输出
- 增加了可见骨架：
  - `hero_metric`
  - `tool_pipeline`
  - `framework_map` / `proof_matrix`
  - `action_close` / `checklist_close` / `insight_close`
- `tests/test_visual_strategy_pack.py` 增加了 layout skeleton 绑定回归

## 预览中实际看到的结构

### 1. `hero_metric`

- 开头 scene 已进入 `hero_metric`
- contact sheet 里能看到大号数字 + 指标卡 + 结果卡
- 这类场景和旧的“标题板”已经明显不是同一种结构

### 2. `tool_pipeline`

- pipeline scene 出现了明显的竖向节点链路
- `hf-flow-line` 作为管线连接件有实际渲染痕迹
- `Obsidian / Claude / Hermes` 被放进了节点卡，而不是只放在正文里

### 3. `framework_map` / `proof_matrix`

- 结构从“单块说明卡”变成了矩阵 / 图谱式布局
- 右侧保留了 INSIGHT / STRUCTURE / CENTER CLAIM 类信息
- 不是单纯的 proof 结果条

### 4. `action_close` / `checklist_close`

- 收束页不再像旧的 final score 页面
- 结尾区能看到 CTA 卡、progress、checklist / action 语义
- 目前仍有一条 scene 保留了 `checklist_close` 风格，这是按当前脚本和策略走出来的结果，不是空白 fallback

## 这轮验证到的事实

- `scene_count = 24`
- `layout_families` 统计中：
  - `hero_metric = 1`
  - `tool_pipeline = 2`
  - `framework_map = 7`
  - `file_tree = 5`
  - `config_panel = 4`
  - `checklist_close = 4`
  - `action_close = 1`
- `index.html` 中：
  - `LAYOUT FAMILY = 0`
  - `CAPTION / = 0`
  - `hf-scan-beam = 0`
  - `vf-strategy-meta = 2`
  - `hf-big-number = 5`
  - `hf-flow-line = 1`
  - `hf-metric-card = 2`
  - `hf-status-stamp = 7`
- `approval_required.json`
  - `preview_status = READY`
  - `review_frames_status = PASS`
  - `can_approve_preview = true`
  - `status = pending_human_review`

## 风险点

- 目前 `tool_pipeline` 和 `framework_map` 已经明显分开，但 `config_panel` 与 `file_tree` 仍会在同一批 scene 中出现，需要继续观察是否会让某些中段仍显得偏相近。
- `action_close / checklist_close` 的边界已经更清晰，但是否足够“像发布收口”还需要继续看更复杂脚本。
- 这轮 smoke 证明了骨架绑定是可见的，但还没有把它验证成最终发布候选。

## 结论性记录

这轮的价值在于：`layout_family` 不再只是数据标签，而是开始影响真实画面骨架。  
后续如果继续扩展，应当优先复用这套骨架映射，而不是再加新的“半成品布局”。

