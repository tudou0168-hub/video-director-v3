# P4.1B-R4 Follow-up Fix: Unified Caption + Center Composition + Viral Layout Rules

日期：2026-06-04  
阶段：`P4.1B-R4 Visual Composition Polish + Collision Cleanup`

## 本轮边界

这轮只做通用构图规则修正，不进入 `P4.2`，不扩模板，不改 HyperFrames playback，不渲染 MP4。

本轮 smoke 只使用：

- 输入脚本：`samples/scripts/p4_batch_ai_toolflow.md`
- 输出目录：`outputs/p4_1b_r4_followup_visual_rules_preview/`

重要说明：

- 下面的修改是**系统级规则**，不是针对当前 smoke 文案、scene id、project_id 的特判。
- 本轮 smoke 只是验证样本，不能据此声称“已适配所有文案”。

## 系统级规则修改

### 1. close 页彻底禁用旧 scoreboard 语义

目标：

- close 页不再出现旧 `FINAL SCORE / COMPLETE / CHAPTER CLOSE`
- 收束页改成动作板、清单板、观点收束板

通用规则：

- `action_close` 显示 `ACTION CLOSE / NEXT ACTION`
- `checklist_close` 显示 `CHECKLIST CLOSE / CHECKLIST`
- `insight_close` 显示 `INSIGHT CLOSE / INSIGHT`
- close 页正文只显示正向动作信息，不显示 CTA policy 的禁用短语列表

### 2. skeleton 主体遵守统一安全区

目标：

- 主体不被字幕压住
- 收束页、hero、pipeline、framework 都有稳定的底部安全区

通用规则：

- `hero_metric / tool_pipeline / framework_map / proof_matrix / action_close / checklist_close`
  的 `--vf-safe-bottom` 全部提高
- caption 统一下沉到底部辅助层

### 3. caption 降权为辅助层

目标：

- caption 只做辅助阅读，不再统治画面

通用规则：

- 降低 caption 默认字号
- 缩窄 caption 最大宽度
- 收紧 padding
- 各 caption mode 统一下移

### 4. tool_pipeline 防碰撞

目标：

- 节点、flow line、workflow result 不互相压住

通用规则：

- 增大节点区与结果卡区的留白
- 减小节点标题字号
- 增加节点最小高度
- 调整 `hf-flow-line` 长度与位置

### 5. framework_map / proof_matrix 可读化

目标：

- 从“小卡片堆叠”提升成“可读结构图”

通用规则：

- 增加 grid gap
- 放大中心结构带
- 降低右侧 insight 卡权重
- 提升中区占比，减少右侧抢画面

### 6. hero_metric 成熟层级

目标：

- 大数字页不只是粗暴放大数字
- 要有“数字 + 单位 + 标题 + 指标卡”的成熟层级

通用规则：

- 将 metric 文本做通用拆分：`number + unit`
- 数字、单位、标题、anchor card 分层显示
- 不依赖具体词，如 “10分钟 / Obsidian / Claude / Hermes”

### 7. scene_pack 信息透传到 timeline / skeleton

目标：

- `display_headline / display_subtitle / visual_headline / memory_anchor / save_reason`
  不在 `scene_pack -> director_timeline -> index.html` 过程中丢失

通用规则：

- contract scene 与 non-contract scene 都透传这些字段
- close skeleton 优先消费这些显式字段，不再露出占位词

## 本轮关键 grep 证据

基于：

- `outputs/p4_1b_r4_followup_visual_rules_preview/hyperframes_timeline/index.html`

结果：

```text
HERO METRIC = 1
TOOL PIPELINE = 2
FRAMEWORK MAP = 7
ACTION CLOSE = 2
hf-big-number = 6
hf-flow-line = 36
FINAL SCORE = 0
COMPLETE = 0
CHAPTER CLOSE = 0
LAYOUT FAMILY = 0
CAPTION / = 0
这一帧需要补充语义内容 = 0
评论区打关键词领取资料 = 0
私信领取资料 = 0
```

## 本轮 smoke 观察结果（不是泛化结论）

本轮 smoke 里，新的 skeleton 规则已经真实进入：

- `hero_metric`：左侧大数字 + 单位，右侧 anchor card，caption 退到辅助层
- `tool_pipeline`：节点区、结果区、flow line 已分开
- `framework_map`：中区更像结构图，不再主要像列表堆叠
- `action_close / checklist_close`：已不再露出旧 score 文案，也不再显示 CTA policy 禁用短语

但这还只是当前 smoke 样本的观察结果，不代表已经覆盖所有脚本类型。

## 本轮仍需人工盯的点

- `framework_map` 在长句场景里仍有“略挤”的风险
- caption 虽然已降权，但在低位仍然可见，是否继续降权需要结合下一轮人工判断
- `semantic_quality_score` 仍然不高（`55.26`），说明这条 smoke 仍然只是 smoke，不是发布候选

## 本轮没有做的事

- 没有 render MP4
- 没有提交 `outputs/`
- 没有提交 `renders/`
- 没有提交 `contact-sheet.jpg`
- 没有碰 `narrative_compressor.py`
- 没有处理历史未跟踪实验文件

