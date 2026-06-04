# P4.1B-R3 Follow-up Fix

日期：2026-06-04

## 触发原因

用户人工审查指出：之前的 R3 contact sheet 与报告不一致，画面仍接近 R2 / 旧模板。具体表现为：

- 开场没有真正的大数字主视觉
- 工具页仍像竖排卡片
- `framework_map` 仍偏列表感
- 结尾还有 `FINAL SCORE` 影子

## 根因

这不是截图缓存问题，而是渲染链路里两层布局字段没有真正传到最终 HTML：

1. `scene_pack.json` 已经有 `layout_family`
2. 但 `director_timeline.json` 在非 contract 以及部分 contract 分支里丢掉了这层字段
3. `publish_templates.py` 虽然已经有 skeleton 逻辑，但若 `director_timeline` 还是旧布局，contact sheet 仍然会沿旧模板看起来渲染

## 修复内容

- `publish_templates.py`
  - `get_scene_body()` 对带 `layout_family` 的 scene 统一包 `vf-strategy-shell`
  - contract scene 继续走 skeleton 包装
- `studio_native_project_builder.py`
  - `_contract_hud_scene_config()` 透传 `layout_family` / `caption_mode` / `ending_variant`
  - `_hud_scene_config()` 读取 `scene_pack_scene` 并保留布局字段
  - 这样 `director_timeline.json` 和 `index.html` 会使用同一套布局信息
- `tests/test_visual_strategy_pack.py`
  - 增加 layout skeleton 透传回归测试

## 重新生成后看到的事实

- `director_timeline.json`
  - `S01` 进入 `hero_metric`
  - `S05` 进入 `tool_pipeline`
  - `S06 / S08` 进入 `framework_map`
  - `S04 / S09` 仍可见 `checklist_close`
- `index.html`
  - `vf-strategy-shell = 25`
  - `vf-content-region = 25`
  - `vf-layout-hero_metric = 2`
  - `vf-layout-tool_pipeline = 4`
  - `vf-layout-framework_map = 14`
  - `vf-layout-action_close = 2`
  - `vf-layout-checklist_close = 8`
- contact sheet 里已经能看到：
  - 左上角大数字主视觉
  - 中间两页是节点式工具管线
  - 下方是矩阵/结构图
  - 结尾不再像旧 final score 页

## 仍需注意

- 这轮只修了“布局骨架接线”和“截图入口一致性”
- 还没有进入 P4.2
- 不要把这次修复当成新的视觉系统设计
- 不要 render MP4

