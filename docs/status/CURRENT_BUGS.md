# CURRENT BUGS

## P0 — Smoke 视频时长不符（已修复 ✅）

**问题**：smoke_props.json 指定 duration_seconds: 18.0，但静态 composition 注册为 2063 帧（82.5s）。导致 smoke 渲染实际输出了 82s 而非 18s。

**影响**：smoke 测试无法准确验证 18s 范围内的视觉增强效果

**修复方式**：在 Root.tsx 新增 HudExplainerSmoke composition，durationInFrames=450，fps=25，直接渲染 18s smoke，不再依赖 --frame-range 或 ffmpeg 截取。

**状态**：✅ 已修复（V3-P2.5 Goal 1）

---

## P1 — 字幕黑条仍较重

**问题**：Caption.tsx 透明度 0.52，仍可能影响主体画面

**涉及文件**：src/components/Caption.tsx

**修复方向**：可进一步降低透明度至 0.35，适配 HUD 风格

**状态**：低优先级，V3-P2.5 未涉及

---

## P2 — 动画流畅度可提升

**问题**：部分 spring 动画可能有跳跃感

**涉及文件**：各 scene 的 spring config

**修复方向**：调整 damping/stiffness 参数

**状态**：低优先级，不阻塞主线

---

## V3-P2.5 待解决

| 问题 | 状态 |
|------|------|
| 6 张关键帧人工审查 | **PENDING HUMAN REVIEW** |
| 是否进入下一阶段 | 待决策 |

---
最后更新：2026-05-30