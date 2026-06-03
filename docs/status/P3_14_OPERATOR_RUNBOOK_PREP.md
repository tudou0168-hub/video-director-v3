# P3.14 Operator Runbook Prep

## 目标

把当前主线整理成可稳定复用的 operator 文档，方便后续按步骤执行：

1. 输入脚本
2. 生成 preview
3. 审查 preview
4. 用户确认后 render MP4

## 已新增 runbook

- `docs/runbooks/CREATE_VIDEO.md`
- `docs/runbooks/REVIEW_PREVIEW.md`
- `docs/runbooks/RENDER_MP4.md`
- `docs/runbooks/TROUBLESHOOTING.md`

## 这套 runbook 解决什么问题

- 新用户知道怎么跑主线
- 新 agent 知道先看什么
- 不会误把 `combined/index.html` 或自定义播放路线当主线
- 不会在 preview 阶段误 render MP4

## 核心原则

- HyperFrames 是稳定 preview/render 底座
- semantic director 负责语义导演
- QA gate 负责阻止垃圾产出
- MP4 只在用户确认后生成

