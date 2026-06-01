# CURRENT BUGS

## 已解决 — 旧 Audio Contract 与新产品方向冲突

**问题**：
- `tts_adapter.py` 强制 `+15%`，超长时会尝试 `+30%`。
- `config.py` 与 renderer 将时长限制在 `38-43s`。
- `narration_planner.py` 会为了命中时长压缩文案。

**影响**：口播不自然，长文无法按内容合理展开。

**状态**：✅ P3.1 已删除加速路径。长文先提炼为目标 `<=120s`、硬上限 `<=150s` 的短视频口播，再由真实音频时长驱动视频总时长。

---

## 已解决 — 正式 MP4 渲染依赖废弃 combined 路线

**问题**：`pipeline_runner.py` 和 `browser_mp4_renderer.py` 仍读取 `combined/index.html`。

**影响**：与 HyperFrames Studio Native Preview 主线冲突。

**状态**：✅ P3.1 已将 preview 和 render 统一到 `hyperframes_timeline/`。

---

## 已解决 — 最终交付缺少完整同步报告

**问题**：已有音频 mux，但缺少 MP4 音频流、音量、字幕尾点、分镜尾点和音频尾点统一检查。

**影响**：无法证明最终视频有声音且同步误差在 1 秒以内。

**状态**：✅ P3.1 新增 `sync_report.json`，验证音轨、音量和三类尾点漂移。

---

## 已解决 — Preview gate fail-open

**问题**：`motion_storyboard` 等必需阶段失败时，preview 仍可能写出 `can_approve_preview=true`，导致错误 fallback 结果继续进入 render。

**影响**：会出现“测试和 smoke 通过，但关键阶段实际失败”的误导性绿灯。

**状态**：✅ 已修复。preview approval 现在记录 required stage status，并在必需阶段失败时 fail closed。

---

## 已解决 — 固定场景与固定转场主链路阻塞

**问题**：pipeline 实际未接入动态 storyboard，scene 与 transition 仍落回固定 7-8 段。

**影响**：不能根据文案重点灵活调整节奏。

**状态**：✅ P3.2 批次 1 已修复。`demo_v3_preview` 现生成 12 scene / 11 transition / 26 caption。

---

## 已解决 — Hook / CTA 还未接入同等级的语义路由

**问题**：
- `method / explain / evidence / proof` 已接入多种语义变体，但 `hook` 和 `cta` 仍主要停留在 `hook_big_claim` 与 `checklist_cta` 两个基础模板。
- 外部截图与 wiki 路由中已经抽出 `comment_quote_hook / big_number_claim / end_score_goodbye`，但尚未接入真实渲染链。

**影响**：开头和结尾仍缺少与中段同等级的样式变化，整条视频的首尾记忆点还不够强。

**状态**：✅ P3.2 批次 7 已修复。`hook_big_claim` 已扩展 `quote_punch / big_number_left`；`checklist_cta` 已扩展 `button_banner / end_score_goodbye / scorecard` 三个复用型 layout_variant；按 narration 关键词自动路由；4 项新单测断言全部通过；preview / smoke 继续 `PASS`，同步漂移仍为 `0.0s`。

## 历史问题 — R9 HyperFrames Studio 打开显示"请先选择"（冻结）

**问题**：R9 的 HyperFrames Studio 原生项目默认 composition/entry/manifest 不完整，导致 Studio 打开后 stage 显示"请先选择"，而非直接显示 scene01。

**影响**：无法通过 HyperFrames Studio 原生预览验收

**修复方式**：修复 Root.tsx / manifest/entry 确保 Studio 打开即显示 scene01

**不允许的绕过方式**：
- autoplay 或 JS 强制 play
- file:// 普通 HTML 作为通过
- 回到 combined/index.html 路线

**状态**：R9 历史路线冻结。P3.1 使用新的 Studio Native 主线实现，不继续补丁式修复 R9。

---

## P1 — combined/index.html 旧路线需清理

**问题**：V3 早期文档大量出现 combined/index.html / file:// / 自定义 GSAP 等旧路线描述

**涉及文件**：README.md, AGENTS.md, docs/status/*.md, docs/runbooks/COMMANDS.md 等

**修复方式**：V3-P2.7-Docs-Native-Only-Cleanup 阶段统一清理，改为 HyperFrames Studio 原生预览

**状态**：✅ V3-P2.7-Docs-Native-Only-Cleanup 已完成

---

## 低优先级（不阻塞主线）

| 问题 | 涉及文件 | 修复方向 | 状态 |
|------|------|------|------|
| 字幕黑条较重 | Caption.tsx | 透明度可降至 0.35 | 低优先级 |
| 动画流畅度 | 各 scene spring config | 调整 damping/stiffness | 低优先级 |
| 107 个调试 JS 未与产品代码隔离 | repo 根目录 | 单独归档或清理 | P2 |
| `get_scene_gsap` 当前仅被废弃 `combined_html_builder` 消费 | `publish_templates.py` | 保留接口作为未来扩展点；不接入 Native Preview（保护 0.0s 漂移） | P3 |

---
最后更新：2026-06-01
