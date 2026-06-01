# Agent Handoff — Claude Code

## 重要前提

本项目**不是从零开发**。

如果你（Claude Code）在一个新会话中接手这个项目：

1. **不要**只看 README 就开始改代码
2. **不要**直接相信旧会话中说过的话
3. **不要**跳过上一步的验收标准
4. **不要**在没读 NEXT_TASK 的情况下做功能

## 当前项目不是从零开发

video-director-v3 是一个**已经有实际运行产出**的项目：
- 跑通过完整 preview → review_frames → approval → render_mp4 管线
- 24 个测试全部通过
- 有实际产出的 MP4 文件和 HTML 预览

但也存在**已知问题**：
- final_video.mp4 用户反馈播放无声音
- 调试控件被录入视频
- 字幕显示裁切
- 逐帧缓存未清理

## 当前核心策略

**复用成熟能力，不优先自研。**

- 使用 edge-tts 做 TTS，系统 say 做 fallback
- 使用 Playwright + FFmpeg 渲染视频
- 不自研视频引擎
- 不重构 HyperFrames Studio native
- 不接 CapCut / 素材库
- 不在用户确认前 render MP4
- 不把旧路线当主线入口

## 当前只做入口整理和清理盘点

**当前任务**：V3-P2.8 Docs and Repo Cleanup Plan

当前只做：
- README / AGENTS / docs 统一口径
- repo 清理盘点
- A/B/C/D 分类
- 等人工确认后再执行清理

## 接手步骤

1. 读 `docs/status/PROJECT_STATE.md`
2. 读 `docs/status/NEXT_TASK.md`
3. 读 `docs/status/CURRENT_BUGS.md`
4. 读 `docs/cleanup-plan.md`
5. 运行诊断命令确认问题
6. 修改
7. 更新记忆文件

## 修改后必须更新这些文件

- `docs/status/PROJECT_STATE.md` — 如果阶段状态变化
- `docs/status/CURRENT_BUGS.md` — 如果 bug 状态变化
- `docs/status/LAST_KNOWN_GOOD.md` — 如果能力通过/失败变化
- `docs/status/NEXT_TASK.md` — 如果完成或方向变化
- `docs/status/TASK_LOG.md` — 记录任务结果

---

最后更新：2026-06-01
