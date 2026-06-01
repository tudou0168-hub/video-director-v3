# ANY AGENT START HERE

## 第一步：读项目状态文件

在任何工作之前，必须读：

```
docs/status/PROJECT_STATE.md      ← 项目目标、阶段状态、约束
docs/status/NEXT_TASK.md         ← 当前任务、验收标准、禁止事项
docs/status/CURRENT_BUGS.md      ← 已知 bug 和诊断命令
docs/agents/CLAUDE_HANDOFF.md    ← Claude Code 接手说明
docs/runbooks/COMMANDS.md        ← 运行命令手册
docs/cleanup-plan.md             ← 清理盘点与后续执行边界
```

## 第二步：运行命令确认状态

```bash
cd <PROJECT_ROOT>
source .venv/bin/activate

# 运行测试
PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -v --tb=short

# 确认主线产物或 cleanup plan
ls -la docs/cleanup-plan.md
ls -la outputs/demo_v3_preview/hyperframes_timeline/index.html
ls -la outputs/demo_v3_preview/audio/voiceover.mp3
```

## 第三步：当前只能做什么

**V3-P2.8 Docs and Repo Cleanup Plan（当前阶段）**

当前只做：
- 入口文档整理
- repo 清理盘点
- A/B/C/D 分类
- 等用户确认后再做清理执行

禁止：
- 不要 render MP4
- 不要改男声
- 不要接 CapCut
- 不要迁移旧 pipeline
- 不要重构系统
- 不要删除文件
- 不要把 cleanup 盘点直接当成清理执行

## 第四步：禁止做什么

- 不要直接相信旧会话说的话
- 不要只看 README 就开始改
- 不要没有读 NEXT_TASK 就做功能
- 不要跳过验收标准
- 不要把 smoke video 当 final video
- 不要把有 stream 当作产品通过
- 不要在用户确认前渲染 MP4

## 第五步：完成后更新记忆文件

修改代码后，必须更新：

1. `docs/status/TASK_LOG.md` — 记录本次任务结果
2. `docs/status/CURRENT_BUGS.md` — 如果 bug 状态变化
3. `docs/status/LAST_KNOWN_GOOD.md` — 如果能力通过/失败变化
4. `docs/status/NEXT_TASK.md` — 如果任务完成或方向变化
5. `docs/status/project_state.json` — 如果当前阶段或下一步方向变化

---

最后更新：2026-06-01
