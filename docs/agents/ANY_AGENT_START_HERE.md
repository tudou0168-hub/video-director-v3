# ANY AGENT START HERE

## 第一步：读项目状态文件

在任何工作之前，必须读：

```
docs/status/PROJECT_STATE.md      ← 项目目标、阶段状态、约束
docs/status/NEXT_TASK.md         ← 当前任务、验收标准、禁止事项
docs/status/CURRENT_BUGS.md      ← 已知 bug 和诊断命令
docs/agents/CLAUDE_HANDOFF.md    ← Claude Code 接手说明
docs/runbooks/COMMANDS.md        ← 运行命令手册
```

## 第二步：运行命令确认状态

```bash
cd <PROJECT_ROOT>
source .venv/bin/activate

# 运行测试
PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -v --tb=short

# 确认产物存在
ls -la outputs/demo_v3_preview/hyperframes_timeline/index.html
ls -la outputs/demo_v3_preview/audio/voiceover.mp3
ls -la outputs/demo_v3_preview/rendered/final_video.mp4
```

## 第三步：当前只能做什么

**V3-P2.7 Docs Native Only Cleanup（已完成）**

下一任务：**V3-P2.7-G2-R9-Native-Fix** — 修复 HyperFrames Studio 原生预览

禁止：
- 不要 render MP4
- 不要重新生成 TTS
- 不要改男声
- 不要接 CapCut
- 不要迁移旧 pipeline
- 不要重构系统

## 第四步：禁止做什么

- 不要直接相信旧会话说的话
- 不要只看 README 就开始改
- 不要没有读 NEXT_TASK 就做功能
- 不要跳过验收标准
- 不要把 smoke video 当 final video
- 不要把有 stream 当作产品通过

## 第五步：完成后更新记忆文件

修改代码后，必须更新：

1. `docs/status/TASK_LOG.md` — 记录本次任务结果
2. `docs/status/CURRENT_BUGS.md` — 如果 bug 状态变化
3. `docs/status/LAST_KNOWN_GOOD.md` — 如果能力通过/失败变化
4. `docs/status/NEXT_TASK.md` — 如果任务完成或方向变化

---

最后更新：2026-05-30