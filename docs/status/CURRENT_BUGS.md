# CURRENT BUGS

## P0 — R9 HyperFrames Studio 打开显示"请先选择"（待修复）

**问题**：R9 的 HyperFrames Studio 原生项目默认 composition/entry/manifest 不完整，导致 Studio 打开后 stage 显示"请先选择"，而非直接显示 scene01。

**影响**：无法通过 HyperFrames Studio 原生预览验收

**修复方式**：修复 Root.tsx / manifest/entry 确保 Studio 打开即显示 scene01

**不允许的绕过方式**：
- autoplay 或 JS 强制 play
- file:// 普通 HTML 作为通过
- 回到 combined/index.html 路线

**状态**：待 V3-P2.7-G2-R9-Native-Fix 修复

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

---
最后更新：2026-05-31