# P4.1B-R3 Strategy to Skeleton Audit

日期：2026-06-04

## 审查对象

- `src/video_director_v3/director/visual_strategy.py`
- `src/video_director_v3/renderers/hyperframes/publish_templates.py`
- `tests/test_visual_strategy_pack.py`
- `tests/test_preview_pipeline.py`
- 预览产物：`outputs/p4_1b_r3_layout_skeleton_smoke_preview/`

## 审查结论（事实型记录）

### 1. 调试 meta 是否默认隐藏

- `LAYOUT FAMILY` 和 `CAPTION /` 没有出现在 `index.html` 的可见正文里
- `vf-strategy-meta` 只有在显式 debug 打开时才会出现
- 默认预览未显示调试 meta

### 2. 扫描线是否保留

- `hf-scan-beam = 0`
- `scan beam / sweep` 已不在正常预览里出现

### 3. caption_mode 是否仍然分化

- `emphasis_caption / minimal_caption / standard_caption / action_caption` 仍然能在不同 scene 上走出差异
- 不是完全退回同一条底部字幕条

### 4. layout_family 是否真的影响骨架

下面是这轮 smoke 中实际观察到的映射：

| layout_family | 观察到的结构 | 视觉判断 |
|---|---|---|
| `hero_metric` | 大数字、指标卡、记忆锚点卡 | 已明显不同于标题板 |
| `tool_pipeline` | 竖向节点、flow line、workflow result | 已明显像管线 |
| `framework_map` / `proof_matrix` | 矩阵 / 图谱 / 结构卡 | 已明显像结构图 |
| `action_close` / `checklist_close` / `insight_close` | CTA 卡 + 收束区 + checklist / action 语义 | 已不再像旧 final score 页面 |

### 5. 成熟 HUD 组件是否真被复用

在当前 smoke 里能直接看到：

- `hf-status-stamp`
- `hf-glass-panel`
- `hf-metric-card`
- `hf-big-number`
- `hf-flow-line`

这些不是只挂在 DOM 里，而是进入了可见结构。

## 与上一轮相比的变化

- 上一轮主要是“debug cleanup + component reuse”
- 这一轮进一步把“组件复用”推进到“布局骨架选择”
- 也就是说，画面变化不再只来自内容词，而开始来自骨架本身

## 仍然需要盯住的点

- `config_panel` 和 `file_tree` 在部分 scene 中仍然偏近，需要继续看是否会拖低中段辨识度
- `framework_map` 的复用范围比较大，后续如果脚本更长，可能会出现结构重复，需要再做一次节奏控制
- `checklist_close` 与 `action_close` 目前已经分开，但还需要在更多脚本里确认收尾页的“发布感”是否稳定

## 不建议现在做的事

- 不要把这轮当成新的系统设计起点
- 不要再扩模板库
- 不要把 `narrative_compressor.py` 接进主线
- 不要 render MP4
- 不要回 combined/index.html

## 下一步路由建议

继续观察更复杂的脚本，确认这套骨架映射在不同内容类型里是否还能维持可读性。  
如果 contact sheet 继续显示出明显区分，再考虑往下一个多脚本验证阶段推进；如果不行，优先修骨架，而不是加新模板。

