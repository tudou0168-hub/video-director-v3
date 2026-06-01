# NEXT TASK

## 当前任务

**V3-P2.8 Repo Cleanup Apply** — 已执行完成。

## 下一任务

**等待人工确认 `docs/cleanup-status.md` 后，再决定是否处理 D 类文件**

当前只允许：
- 整理入口文档
- 盘点仓库内容
- 输出 A/B/C/D 分类
- 等人工确认

### 暂不开始 V4

V4 仍然保留为后续方向，但在 cleanup status 被确认前，不进入 V4 开发。

## P3.2 批次 7 验收证据

- `checklist_cta` 已复用现有 HUD 卡片骨架扩展为 4 个 layout_variant：
  - `checklist_steps`（默认 3-step action list）
  - `button_banner`（大按钮式行动号召）
  - `end_score_goodbye`（大分数收束 + 下期预告）
  - `scorecard`（3 项指标得分卡）
- `_cta_layout_variant_from_narration()` 按 narration 关键词自动路由：
  - 完结 / 下期 / 系列 → `end_score_goodbye`
  - 得分 / 状态 / 指标 → `scorecard`
  - 立即 / 现在 / 下一步 → `button_banner`
  - 其他 → `checklist_steps`
- `_render_cta_button_banner / _render_cta_end_score_goodbye / _render_cta_scorecard` 三个新 render 函数全部接入 `get_scene_body` 的 dispatch 路径。
- GSAP 评估结论：`get_scene_gsap` 当前只被已废弃的 `combined_html_builder` 消费；Native Preview 主线（`studio_native_project_builder`）未消费 GSAP，**故评估为"接入但未触发"状态**。按用户"如破坏稳定性就停止扩大范围"原则，**不**把 GSAP timeline 注入到 Native Preview HTML，以保护 0.0s 同步漂移基线。`get_scene_gsap` 函数体保留作为未来扩展点。
- 47 个测试基线保持通过（`tests/test_preview_pipeline.py` 25 个 + 其他 22 个），`compileall` 通过，`git diff --check` 通过，真实 preview `READY`，5 秒 smoke render `PASS`，`sync_report.json` `max_drift=0.0s`。
- 新增 4 项测试断言（`test_cta_routes_to_layout_variants_by_narration_semantics` / `test_cta_renders_distinct_html_for_each_variant` / `test_template_checklist_cta_dispatches_by_layout_variant`）全部通过。

## 后续阶段

- 等待人工确认 `docs/cleanup-status.md`

## 不允许

- 为命中固定时长加速语音。
- 公众号长文未经提炼直接生成超长口播。
- 用简化占位画面替代 HUD 科技风发布基线。
- 固定生成 6、7、8 个场景。
- 回到 `combined/index.html` / `file://` 路线。
- 预览静音后未经最终 MP4 音频验证就交付。
- 把 GSAP timeline 注入到 Native Preview HTML（会破坏 0.0s 同步漂移基线）。
- 未经人工确认就 render MP4。

---
最后更新：2026-06-01
