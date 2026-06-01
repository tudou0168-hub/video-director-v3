# NEXT TASK

## 当前任务

**V3-P3.2 Visual Differentiation（批次 4）** — 已完成并验证。

路线图：`docs/plans/V3_P3_VIRAL_VIDEO_ROADMAP.md`

## 下一任务

**V3-P3.2 CTA 路由融合 + GSAP 可选动效层评估**

目标：
1. 评估是否在不破坏 Native Preview 稳定性的前提下，将 GSAP 仅作为可选动效层接到现有 HTML scene，而不是引入新 runtime。
2. 把 `hook / cta` 的剩余路由补齐，优先复用现有 HUD 组件和模板语法，避免再出现首尾重复。
3. 保持 P3.1 的自然语速、Native Preview、显式音频 mux 和 `<= 1.0s` 同步 gate。

## P3.2 批次 6 验收证据

- `broken_chain` 已复用现有 HUD 卡片骨架扩展为 `responsibility_split / binary_choice_split`。
- `before_after_compare` 已复用现有对比卡骨架扩展为 `dashboard_mobile / symptom_panel`。
- `hook_big_claim` 已增加 `quote_punch / big_number_left`，`tool_chain_three_cols` 已增加 `intro_offset`。
- `demo_v3_preview` 的 `director_timeline.json` 已可直接看到：`S01=quote_punch`、`S03=intro_offset`、`S04=responsibility_split`。
- 定向 snapshot 已证明 `S01 / S03 / S04` 从同类居中双卡变成封面式 / 导语式 / 对撞式。
- preview 继续 `READY`，5 秒 smoke render 继续 `PASS`，同步报告仍为 `0.0s` 漂移。
- 本批次测试：`tests/test_preview_pipeline.py`、`tests/test_tts_contract.py`、`compileall`、`git diff --check`、真实 preview、真实 smoke render 通过。

## 后续阶段

- `V3-P3.3 Template Registry MVP`
- `V3-P3.4 Template Library Expansion`
- `V3-P3.5 Template Library Complete`
- `V3-P3.6 Viral QA Loop`

## 不允许

- 为命中固定时长加速语音。
- 公众号长文未经提炼直接生成超长口播。
- 用简化占位画面替代 HUD 科技风发布基线。
- 固定生成 6、7、8 个场景。
- 回到 `combined/index.html` / `file://` 路线。
- 预览静音后未经最终 MP4 音频验证就交付。

---
最后更新：2026-06-01
