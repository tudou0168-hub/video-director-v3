# NEXT TASK

## 当前任务

**V3-P2.7-Docs-Native-Only-Cleanup** — 文档统一为 HyperFrames Studio 原生预览路线（已完成 ✅）

## 下一任务（待人工审查后启动）

**V3-P2.7-G2-R9-Native-Fix**：HyperFrames Studio Native Preview Repair

目标：修复当前 R9 的 HyperFrames Studio 原生预览，使其：
1. Studio 打开默认显示 scene01，不出现"请先选择"黑屏
2. scene/audio/caption/visual beats 可被 Studio 识别
3. 音频路径稳定
4. caption-layer 在 stage 内
5. 字幕全程覆盖
6. 输出关键帧截图和 contact sheet
7. QA 通过
8. **不 render MP4**

**不允许：**
- 用 autoplay 或 JS 强制 play 绕过
- 用 file:// 普通 HTML 作为通过
- 回到 combined/index.html 路线

---
最后更新：2026-05-31